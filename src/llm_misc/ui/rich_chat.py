#!/usr/bin/env python3

import asyncio

from rich import print
from rich.markdown import Markdown
from rich.prompt import Prompt

from ..completion import Chat

from ..resources import get_resources, Config


async def main():
    chat = Chat(get_resources(Config.model_validate({"db": {"path": "_db"}})))

    while True:
        user_input = Prompt().ask("CHAT")
        response = await chat.send(user_input)
        print(Markdown(response.content))


if __name__ == '__main__':
    asyncio.run(main())
