import asyncio
import json
from uuid import uuid4
from typing import Any, Union, get_args
from functools import singledispatch, singledispatchmethod

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

from .resources import Resources
from .tools.base import Tool


class MessageLog:
    """
    The MessageLog tracks and persists message histories.
    """
    def __init__(self, res: Resources, system: str | None = None, log_id = str | None):
        self.res = res
        self.system_message = system
        self.log_id = log_id or uuid4().hex
        self._log = []
        if system:
            self._log.append({"role": "system", "content": system})

    async def get_messages(self) -> list[ChatCompletionMessageParam]:
        return self._log

    async def add_message_param(self, mesg: ChatCompletionMessageParam):
        self._log.append(mesg)
        # TODO: Write log

    async def add(self, **kwargs):
        await self.add_message_param(kwargs)  # type: ignore


class Completion:
    """
    A simple openai wrapper in order to decouple from openai.
    """
    def __init__(self, openai: AsyncOpenAI | None = None):
        self._openai = openai or AsyncOpenAI()

    @singledispatchmethod
    async def send(self, messages: list[ChatCompletionMessageParam], **kwargs) -> ChatCompletion:
        return await self._openai.chat.completions.create(
            messages=messages,
            **kwargs
        )

    @send.register
    async def _(self, messages: MessageLog, **kwargs) -> ChatCompletion:
        return await self.send(await messages.get_messages(), **kwargs)


class Chat:
    """
    Chat adds a MessageLog to track and persist conversations and
    Tools in order to provide additional functionality.
    """
    tools: dict[str, Tool]

    def __init__(self,
                 res: Resources,
                 system: str | None = None,
                 /,
                 tools: list[Tool] | None = None,
                 completion: Completion | None = None,
                 message_log: MessageLog | None = None,
                 **kwargs):
        self._res = res
        self.tools = {tool.get_tool_name(): tool for tool in tools} if tools else {}
        self.tools = _tool_list_to_dict(tools) if tools else {}
        self._completion = completion or Completion()
        self._messages = message_log or MessageLog(res)
        self._system = system
        self._completion_params = kwargs

    async def send(self, prompt: str, /, tools: list[Tool] | None = None, **kwargs):
        await self._messages.add(role="user", content=prompt)
        params: dict[str, Any] = self._completion_params.copy()
        params.update(kwargs)
        tool_map = self.tools.copy()
        if tools:
            tool_map.update(_tool_list_to_dict(tools))

        params.setdefault("tools", [])
        params["tools"].extend([tool.get_tool_function() for tool in tool_map.values()])
        if not params["tools"]:
            del params["tools"]

        message = None
        while message is None:
            response = await self._completion.send(self._messages, **params)
            message = await self.handle_response(params, response, tool_map)

        return message

    async def handle_response(self, params: dict[str, Any], response: ChatCompletion, tools: dict[str, Tool], choice: int = 0) -> ChatCompletionMessage | None:
        message = response.choices[choice].message
#        await self._messages.add_message_param({"role": "assistant", "content": message.content, "name": "", "tool_calls": message.tool_calls})
        await self._messages.add(role="assistant", content=message.content, name="", tool_calls=message.tool_calls)

        match response.choices[choice].finish_reason:
            case "tool_calls":
                message = self.handle_tool_calls(message, tools)
            case "content_filter" | "function_call" | "length":
                raise Exception(f"unsupported error...")  # TODO
            case _:
                return message

    async def handle_tool_calls(self, message: ChatCompletionMessage, tools: dict[str, Tool]):
        assert message.tool_calls is not None
        async with asyncio.TaskGroup() as group:
            for tool_call in message.tool_calls:
                group.create_task(self.run_tool_call(tools[tool_call.function.name], tool_call.function.arguments))

    async def run_tool_call(self, tool: Tool, arguments: str):
        instance = tool.model_validate_strings(arguments)
        return await instance.run()


def _tool_list_to_dict(tools: list[Tool]) -> dict[str, Tool]:
    return {tool.get_tool_name(): tool for tool in tools} if tools else {}
