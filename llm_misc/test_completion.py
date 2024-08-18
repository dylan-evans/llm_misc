import asyncio
import pytest
from unittest.mock import MagicMock
from llm_misc.completion import Chat, MessageLog, Completion, Tool, Resources
from .resources import get_resources, Config

@pytest.fixture
def mock_tool():
    return MagicMock(spec=Tool)


@pytest.fixture
def mock_completion():
    return MagicMock(spec=Completion)


@pytest.fixture
def mock_message_log():
    return MagicMock(spec=MessageLog)


@pytest.fixture
def chat(mock_tool, mock_completion, mock_message_log):
    res = get_resources(Config.model_validate({"db": {"path": "/workspaces/db"}}))
    return Chat(res, tools=[mock_tool], completion=mock_completion, message_log=mock_message_log)




def test_basic_completion():
    comp = Completion()
    response = asyncio.run(comp.send([{"role": "user", "content": "Hello"}], model="gpt-4o-mini"))
    assert response.choices[0].message.content
    assert response.choices[0].finish_reason == "stop"


def test_basic_chat():
    chat = Chat(get_resources(Config.model_validate({"db": {"path": "/workspaces/db"}})), model="gpt-4o-mini")
    response = asyncio.run(chat.send("Hello"))
    assert response.choices[0].message.content
    assert response.choices[0].finish_reason == "stop"

    response = asyncio.run(chat.send("How are you?"))

    assert response.choices[0].message.content
    assert response.choices[0].finish_reason == "stop"

    assert response.choices[0].message.content
    assert response.choices[0].finish_reason == "stop"
