import functools
from uuid import uuid4
from typing import Optional, Literal

import litellm
import wrapt
from pydantic import BaseModel

from .resources import Resources


class MessageLog:
    """
    The MessageLog tracks and persists message histories.
    """
    def __init__(self, res: Resources, system: str | None = None, log_id = str | None):
        self.res = res
        self.system_message = system
        self.log_id = log_id or uuid4().hex
        self.log = []
        if system:
            self.log.append({"role": "system", "content": system})

    def add(self, mesg):
        self.log.append(mesg)
        # TODO: Write log



class AgentStep:
    def __init__(self, index, name, callback, next_step):
        self.index = index
        self.name = name
        self.callback = callback
        self.next_step = next_step


class AgentPipeline:
    def __init__(self, agent: "Agent", input: str):
        self.agent = agent
        self._next_step = agent.steps[0]

    @property
    def next_step(self) -> AgentStep | None:
        return self._next_step

    @next_step.setter
    def next_step(self, value: str | int | AgentStep):
        if isinstance(value, AgentStep):
            self._next_step = value
        else:
            if isinstance(value, int) and value > len(self.agent.steps):
                self._next_step = None
            else:
                self._next_step = self.agent.get_step(value)


class Agent:
    def __init__(self, res: Resources):
        self.res = res
        self.steps = []
        self._step_names = {}

    def get_step(self, step_id: str | int):
        if isinstance(step_id, str):
            return self._step_names(step_id)
        return self.steps[step_id]

    @wrapt.decorator
    def step(
        self,
        wrapped = None,
        /,
        name: Optional(str) = None,
        tools: Optional(list[object]) = None,
        next_step: Optional(int | str) = None,
    ):
        if wrapped is None:
            return functools.partial(self.step, name=name, tools=tools)

        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        agent_step = AgentStep(index=len(self.steps), name=name, callback=callback)
        self.steps.append(agent_step)
        if name is not None:
            self._step_names[name] = agent_step

        return wrapper(wrapped)

    async def prompt(self, **kwargs):
        response = litellm.completion(**kwargs)
        return response.choice[0].message

    async def run(self, message):
        pipeline = AgentPipeline(self, message)
        while step := pipeline.next_step:
            message = step.callback(pipeline=self, input=message)
            if id(step) == id(pipeline.next_step):
                if step.next_step is not None:
                    pipeline.next_step = step.next_step
                else:
                    pipeline.next_step = step.index + 1
        return message
