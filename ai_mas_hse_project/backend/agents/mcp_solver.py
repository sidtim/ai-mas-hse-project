"""
MCP Math Solver Agent
Интеграция MCP инструментов в систему агентов
"""

import asyncio
import json
import os
import sys
import re
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
        
        result = await self.session.call_tool(tool_name, arguments)  # ← ИСПРАВЛЕНО
        
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
    
    def _create_tools_prompt(self) -> str:
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
                f"- {tool.name}({', '.join(params)}): {desc[:80]}..."
            )
        
        return "\n".join(tools_desc)
    
    def _detect_tool_hint(self, problem: str) -> str:
        """Автоматическое определение нужного инструмента по тексту задачи"""
        p = problem.lower()
        
        # Уравнения с переменными (x, y, z) и =
        if "=" in p and any(c in p for c in ["x", "y", "z"]):
            return "💡 Это УРАВНЕНИЕ. Используй solve_equation с аргументом 'equation' (строка с '=')."
        
        # Производные
        elif any(word in p for word in ["производн", "дифференц", "производная"]):
            return "💡 Это ПРОИЗВОДНАЯ. Используй differentiate с аргументами 'expression' и 'variable'='x'."
        
        # Интегралы
        elif any(word in p for word in ["интеграл", "интегрирование", "первообразная"]):
            return "💡 Это ИНТЕГРАЛ. Используй integrate с аргументами 'expression' и 'variable'='x'."
        
        # Статистика
        elif any(word in p for word in ["среднее", "средн", "mean", "average"]):
            return "💡 Это СТАТИСТИКА. Используй mean с аргументом 'data' (список чисел, например [1, 2, 3])."
        
        # По умолчанию
        else:
            return "💡 Используй calculate для простых вычислений."
    
    def _extract_equation(self, problem: str) -> Optional[str]:
        """Извлечение уравнения из текста задачи"""
        p = problem.lower()
        
        # Убираем целые слова с границами (чтобы "сначала" не оставило "x")
        words_to_remove = ["реши", "систему", "уравнение", "найди", "из", "сначала", "потом", "что", "корни", "какие"]
        for word in words_to_remove:
            p = re.sub(r'\b' + word + r'\b', ' ', p)
        
        p = re.sub(r'\s+', ' ', p).strip()
        print(f"После очистки: {p}")
        
        # Ищем уравнение вида x**2 - 9 = 0 или x^2 - 9 = 0
        patterns = [
            r'(x\*\*\d+\s*[\+\-]\s*\d+\s*=\s*\d+)',  # x**2 - 9 = 0
            r'(x\*\*\d+\s*=\s*\d+)',                   # x**2 = 9
            r'(x\^\d+\s*[\+\-]\s*\d+\s*=\s*\d+)',      # x^2 - 9 = 0
            r'(x\^\d+\s*=\s*\d+)',                     # x^2 = 9
            r'([x\d\s\+\-\*\(\)]+=[x\d\s\+\-\*\(\)]+)', # общий случай
        ]
        
        for pattern in patterns:
            match = re.search(pattern, p)
            if match:
                eq = match.group(1).replace(" ", "").replace("^", "**")
                print(f"Найдено уравнение: {eq}")
                if 'x' in eq and '=' in eq:
                    return eq
        
        return None
    
    def _extract_expression(self, problem: str) -> Optional[str]:
        """Извлечение математического выражения из текста"""
        p = problem.lower()
        
        # Ищем после "от", "=", "функции"
        patterns = [
            r'от\s+([x\d\s\+\-\*\^\(\)]+?)(?:\s|$)',      # "интеграл от 2*x"
            r'=\s*([x\d\s\+\-\*\^\(\)]+?)(?:\s|$)',       # "f(x) = x**2"
            r'функции?\s+([x\d\s\+\-\*\^\(\)]+?)(?:\s|$)', # "функции x**2"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, p)
            if match:
                expr = match.group(1).strip().replace("^", "**")
                if 'x' in expr:
                    return expr
        return None
    
    async def solve_direct(self, problem: str) -> Dict[str, Any]:
        """
        Прямое решение без LLM-итераций — быстро и надежно
        ИСПРАВЛЕНО: лучшее извлечение уравнений
        """
        await self.ensure_connected()
        
        p = problem.lower()
        tool_calls = []
        
        # Паттерн 1: Уравнение с '=' и 'x'
        if "=" in p and "x" in p:
            equation = self._extract_equation(problem)
            if equation:
                print(f"Извлечено уравнение: {equation}")
                result = await self.mcp_client.call_tool(
                    "solve_equation", 
                    {"equation": equation}
                )
                tool_calls.append({
                    "tool": "solve_equation", 
                    "arguments": {"equation": equation},
                    "result": result
                })
                
                # Форматируем ответ красиво
                solutions = result.get("solutions", "неизвестно")
                return {
                    "answer": f"x = {solutions}",
                    "full_response": f"Решено уравнение {equation}. Корни: {solutions}",
                    "tool_calls": tool_calls,
                    "iterations": 1
                }
            else:
                print("Уравнение не распознано, пробуем LLM")
        
        # Паттерн 2: Производная
        elif "производн" in p:
            expr = self._extract_expression(problem)
            if expr:
                result = await self.mcp_client.call_tool(
                    "differentiate",
                    {"expression": expr, "variable": "x"}
                )
                tool_calls.append({
                    "tool": "differentiate",
                    "arguments": {"expression": expr, "variable": "x"},
                    "result": result
                })
                return {
                    "answer": result.get("result", "неизвестно"),
                    "full_response": f"Производная от {expr}",
                    "tool_calls": tool_calls,
                    "iterations": 1
                }
        
        # Паттерн 3: Интеграл
        elif "интеграл" in p:
            expr = self._extract_expression(problem)
            if expr:
                result = await self.mcp_client.call_tool(
                    "integrate",
                    {"expression": expr, "variable": "x"}
                )
                tool_calls.append({
                    "tool": "integrate",
                    "arguments": {"expression": expr, "variable": "x"},
                    "result": result
                })
                return {
                    "answer": result.get("result", "неизвестно"),
                    "full_response": f"Интеграл от {expr}",
                    "tool_calls": tool_calls,
                    "iterations": 1
                }
        
        # Паттерн 4: Среднее значение
        elif "среднее" in p or "средн" in p:
            numbers = re.findall(r'\d+', problem)
            if len(numbers) >= 2:
                data = [float(n) for n in numbers]
                result = await self.mcp_client.call_tool(
                    "mean",
                    {"data": data}
                )
                tool_calls.append({
                    "tool": "mean",
                    "arguments": {"data": data},
                    "result": result
                })
                return {
                    "answer": str(result.get("result", "неизвестно")),
                    "full_response": f"Среднее значение {data}",
                    "tool_calls": tool_calls,
                    "iterations": 1
                }
        
        # Если не сработало — fallback на LLM
        raise ValueError(f"Не удалось распознать задачу: {problem}")
    
    async def solve(self, problem: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Решение задачи с использованием MCP инструментов
        """
        print(f"DEBUG solve(): получена задача: {problem}")
        # Сначала пробуем быстрый прямой метод
        try:
            return await self.solve_direct(problem)
        except Exception as e:
            print(f"Прямое решение не сработало: {e}, переходим к LLM")
        
        # Fallback: LLM с улучшенным промптом
        await self.ensure_connected()
        
        tool_hint = self._detect_tool_hint(problem)
        
        system_msg = f"""Ты математический ассистент с точными инструментами.

ЗАДАЧА: {problem}

{tool_hint}

Доступные инструменты:
{self._create_tools_prompt()}

ВАЖНЫЕ ПРАВИЛА:
1. Для уравнений с '=' и 'x' ВСЕГДА используй solve_equation
2. Для производных используй differentiate с variable='x'  
3. Для интегралов используй integrate с variable='x'
4. Для среднего значения используй mean с data=[числа]

ФОРМАТ:
TOOL_CALL: {{"tool": "имя_инструмента", "arguments": {{...}}}}

После результата:
FINAL_ANSWER: [числовой ответ]"""

        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content="Реши задачу одним вызовом инструмента.")
        ]
        
        tool_calls = []
        
        for i in range(max_iterations):
            response = await self.llm.ainvoke(messages)
            content = response.content
            
            if "TOOL_CALL:" in content:
                try:
                    json_str = content.split("TOOL_CALL:")[1].strip().split("\n")[0]
                    call = json.loads(json_str)
                    
                    tool_name = call.get("tool")
                    arguments = call.get("arguments", {})
                    
                    result = await self.mcp_client.call_tool(tool_name, arguments)
                    tool_calls.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": result
                    })
                    
                    answer = str(result.get("solutions", result.get("result", "неизвестно")))
                    
                    return {
                        "full_response": content,
                        "answer": answer,
                        "tool_calls": tool_calls,
                        "iterations": i + 1
                    }
                    
                except Exception as e:
                    messages.extend([
                        AIMessage(content=content),
                        HumanMessage(content=f"Ошибка: {e}. Попробуй снова.")
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
                messages.extend([
                    AIMessage(content=content),
                    HumanMessage(content="Используй TOOL_CALL:")
                ])
        
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