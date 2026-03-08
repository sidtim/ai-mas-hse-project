"""
MCP Math Solver Agent - упрощенная версия только с LLM
"""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from config import get_llm


class MCPClient:
    """Клиент для подключения к MCP Math Server"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, server_path: Optional[str] = None):
        if MCPClient._initialized:
            return
            
        self.server_path = server_path or "/app/calculator_server.py"
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self.tools: List[Any] = []
        MCPClient._initialized = True
    
    async def connect(self) -> "MCPClient":
        """Подключение к MCP серверу"""
        if self.session is not None:
            return self
            
        self.exit_stack = AsyncExitStack()
        
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_path, "--stdio"],
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        
        await self.session.initialize()
        
        # Получаем инструменты
        tools_result = await self.session.list_tools()
        self.tools = tools_result.tools if hasattr(tools_result, 'tools') else list(tools_result)
        
        print(f"✅ MCP подключен, доступно инструментов: {len(self.tools)}")
        return self
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Вызов инструмента MCP"""
        if not self.session:
            raise RuntimeError("MCP клиент не подключен")
        
        print(f"🔧 Вызов инструмента: {tool_name}({arguments})")
        result = await self.session.call_tool(tool_name, arguments)
        
        if result.content and len(result.content) > 0:
            text = result.content[0].text
            try:
                parsed = json.loads(text)
                print(f"📥 Результат: {parsed}")
                return parsed
            except json.JSONDecodeError:
                print(f"📥 Результат (raw): {text[:100]}")
                return {"result": text}
        return {"result": str(result.content)}
    
    async def close(self):
        """Закрытие соединения"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.session = None
            self.exit_stack = None


class MCPSolverAgent:
    """Агент-решатель с использованием MCP инструментов - только LLM"""
    
    def __init__(self):
        self.llm = get_llm()
        self.mcp_client = MCPClient()
        self._connected = False
    
    async def ensure_connected(self):
        """Убедиться, что подключение установлено"""
        if not self._connected:
            await self.mcp_client.connect()
            self._connected = True
    
    def _create_tools_prompt(self) -> str:
        """Создание описания инструментов для LLM"""
        tools_desc = []
        for tool in self.mcp_client.tools:
            params = []
            schema = getattr(tool, 'inputSchema', {}) or {}
            if 'properties' in schema:
                for name, info in schema['properties'].items():
                    ptype = info.get('type', 'any')
                    params.append(f"{name}: {ptype}")
            
            desc = getattr(tool, 'description', 'No description')
            tools_desc.append(
                f"Tool: {tool.name}\n"
                f"  Description: {desc[:100]}...\n"
                f"  Parameters: {', '.join(params) if params else 'none'}"
            )
        
        return "\n\n".join(tools_desc)
    
    async def solve(self, problem: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Решение задачи через LLM + MCP инструменты
        БЕЗ регулярных выражений - только LLM решает какой инструмент использовать
        """
        await self.ensure_connected()
        
        system_msg = f"""Ты математический ассистент с доступом к точным вычислительным инструментам MCP.

Доступные инструменты:
{self._create_tools_prompt()}

Твоя задача:
1. Проанализируй математическую задачу
2. Выбери ПОДХОДЯЩИЙ инструмент из списка выше
3. Подготовь правильные аргументы для вызова
4. Вызови инструмент и получи результат
5. Дай финальный ответ

ФОРМАТ ОТВЕТА (строго соблюдай):

Для вызова инструмента:
TOOL_CALL: {{"tool": "имя_инструмента", "arguments": {{"параметр": "значение"}}}}

После получения результата:
FINAL_ANSWER: [числовой ответ или решение]

ПРИМЕРЫ:

Пример 1 - Уравнение:
Задача: Реши x**2 - 5*x + 6 = 0
TOOL_CALL: {{"tool": "solve_equation", "arguments": {{"equation": "x**2 - 5*x + 6 = 0"}}}}
FINAL_ANSWER: x = 2, x = 3

Пример 2 - Производная:
Задача: Найди производную от x**3 + 2*x
TOOL_CALL: {{"tool": "differentiate", "arguments": {{"expression": "x**3 + 2*x", "variable": "x"}}}}
FINAL_ANSWER: 3*x**2 + 2

Пример 3 - Среднее:
Задача: Найди среднее 10, 20, 30
TOOL_CALL: {{"tool": "mean", "arguments": {{"data": [10, 20, 30]}}}}
FINAL_ANSWER: 20

ВАЖНО:
- Уравнения должны содержать '=' и переменную x/y/z
- Для производных и интегралов указывай variable='x'
- Для статистики передавай data как список чисел [1, 2, 3]
- Используй Python синтаксис: ** для степеней, * для умножения

Теперь реши задачу:"""

        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"Задача: {problem}")
        ]
        
        tool_calls = []
        
        for i in range(max_iterations):
            print(f"\n🔄 Итерация {i+1}/{max_iterations}")
            
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()
            print(f"🤖 LLM: {content[:200]}...")
            
            # Проверяем вызов инструмента
            if "TOOL_CALL:" in content:
                try:
                    # Извлекаем JSON
                    json_str = content.split("TOOL_CALL:")[1].strip()
                    if "\n" in json_str:
                        json_str = json_str.split("\n")[0]
                    
                    call = json.loads(json_str)
                    tool_name = call.get("tool")
                    arguments = call.get("arguments", {})
                    
                    # Вызываем инструмент
                    result = await self.mcp_client.call_tool(tool_name, arguments)
                    tool_calls.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": result
                    })
                    
                    # Добавляем результат в контекст
                    messages.extend([
                        AIMessage(content=content),
                        SystemMessage(content=f"Результат инструмента: {json.dumps(result, ensure_ascii=False)}")
                    ])
                    
                    # Если получили решение - сразу даем ответ
                    if "solutions" in result or "result" in result:
                        # Просим LLM сформулировать финальный ответ
                        messages.append(HumanMessage(content="Сформулируй FINAL_ANSWER на основе результата"))
                        continue
                    
                except Exception as e:
                    print(f"❌ Ошибка вызова: {e}")
                    messages.extend([
                        AIMessage(content=content),
                        SystemMessage(content=f"Ошибка: {e}. Попробуй снова с правильным форматом TOOL_CALL.")
                    ])
                    
            elif "FINAL_ANSWER:" in content:
                answer = content.split("FINAL_ANSWER:")[1].strip()
                print(f"✅ Ответ: {answer}")
                return {
                    "full_response": content,
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "iterations": i + 1
                }
            else:
                # Нет ни инструмента, ни ответа
                messages.extend([
                    AIMessage(content=content),
                    HumanMessage(content="Ты должен использовать TOOL_CALL: для вызова инструмента или FINAL_ANSWER: для ответа.")
                ])
        
        # Достигли лимита
        return {
            "full_response": messages[-1].content if messages else "",
            "answer": "Не удалось получить ответ",
            "tool_calls": tool_calls,
            "iterations": max_iterations,
            "error": "max_iterations_reached"
        }
    
    async def close(self):
        """Закрытие соединения"""
        await self.mcp_client.close()
        self._connected = False


class MCPSolverAgentSync:
    """Синхронная обертка для MCP агента"""
    
    def __init__(self):
        self._agent = MCPSolverAgent()
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Синхронный вызов решения"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._agent.solve(problem))
    
    def close(self):
        """Закрытие соединения"""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._agent.close())
        except:
            pass