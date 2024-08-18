import json

from pydantic import BaseModel

class Tool(BaseModel):
    """
    The base class for tool functions.
    """

    @classmethod
    def get_tool_name(cls) -> str:
        return cls.__name__

    @classmethod
    def get_tool_function(cls):
        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
                "description": cls.__doc__,
                "parameters": cls.model_json_schema()
            }
        }

    async def run(self):
        raise NotImplementedError()
