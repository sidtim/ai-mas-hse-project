"""
MCP Math Solver Agent
Интеграция MCP инструментов в систему агентов
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
        
        return self
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Вызов инструмента MCP"""
        if not self.session:
            raise RuntimeError("MCP клиент не подключен")
        
        result = await self.session.call_tool(tool_name, arguments)
        
        if result.content and len(result.content) > 0:
            text = result.content[0].text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"result": text}
        return {"result": str(result.content)}
    
    async def close(self):
        """Закрытие соединения"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.session = None
            self.exit_stack = None


class MCPSolverAgent:
    """Агент-решатель с использованием MCP инструментов"""
    
    def __init__(self):
        self.llm = get_llm()
        self.mcp_client = MCPClient()
        self._connected = False
    
    async def ensure_connected(self):
        """Убедиться, что подключение установлено"""
        if not self._connected:
            await self.mcp_client.connect()
            self._connected = True
    
    def _create_system_prompt(self) -> str:
        """Создание системного промпта с описанием инструментов"""
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
                f"Tool: {tool.name}({', '.join(params)})\n  {desc[:100]}..."
            )
        
        return f"""Ты математический репетитор с доступом к точным вычислительным инструментам.

Доступные инструменты:
{chr(10).join(tools_desc)}

ПРАВИЛА:
1. Анализируй задачу и выбери ПОДХОДЯЩИЙ инструмент
2. Для вызова используй формат (строго JSON):
   TOOL_CALL: {{"tool": "имя_инструмента", "arguments": {{...}}}}
3. После получения результата дай финальный ответ:
   FINAL_ANSWER: [числовой ответ или решение]

ВАЖНО:
- solve_equation: уравнение должно содержать '=' и x
- differentiate/integrate: выражение с переменной x
- mean/std/var: передавай список чисел [1, 2, 3]
- calculate: любое математическое выражение"""

    async def solve(self, problem: str, max_iterations: int = 5) -> Dict[str, Any]:
        """Решение задачи с использованием MCP инструментов"""
        await self.ensure_connected()
        
        messages = [
            SystemMessage(content=self._create_system_prompt()),
            HumanMessage(content=f"Реши задачу: {problem}")
        ]
        
        tool_calls = []
        
        for i in range(max_iterations):
            response = await self.llm.ainvoke(messages)
            content = response.content
            
            # Проверяем вызов инструмента
            if "TOOL_CALL:" in content:
                try:
                    # Парсим JSON
                    json_str = content.split("TOOL_CALL:")[1].strip().split("\n")[0]
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
                    
                    # Добавляем в контекст
                    messages.extend([
                        AIMessage(content=content),
                        ToolMessage(
                            content=json.dumps(result, ensure_ascii=False),
                            tool_call_id=f"call_{i}",
                            name=tool_name
                        )
                    ])
                    
                except Exception as e:
                    messages.extend([
                        AIMessage(content=content),
                        HumanMessage(content=f"Ошибка вызова инструмента: {e}. Попробуй снова.")
                    ])
                    
            elif "FINAL_ANSWER:" in content:
                answer = content.split("FINAL_ANSWER:")[1].strip()
                
                return {
                    "full_response": content,
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "iterations": i + 1
                }
            else:
                # Просим действовать
                messages.extend([
                    AIMessage(content=content),
                    HumanMessage(content="Используй TOOL_CALL: для инструмента или FINAL_ANSWER: для ответа")
                ])
        
        # Лимит итераций
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


# Синхронная обертка для использования в существующем коде
class MCPSolverAgentSync:
    """Синхронная обертка для MCP агента"""
    
    def __init__(self):
        self._agent = MCPSolverAgent()
    
    def solve(self, problem: str) -> Dict[str, Any]:
        """Синхронный вызов решения"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # В Jupyter/async контексте
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