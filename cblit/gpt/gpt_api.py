"""API for interacting with OpenAI GPT"""
import dataclasses
import os
import re
from enum import Enum
from typing import Type, Dict, List, Optional, Self, Any

from dataclasses_json import dataclass_json, DataClassJsonMixin

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


class DataClassGPTJsonMixin(DataClassJsonMixin):
    @classmethod
    def from_gpt_response(cls: Type[Self], response: str) -> Self:
        return cls.from_json(cls.get_json_from_response(response))

    @staticmethod
    def get_json_from_response(response: str) -> str:
        json_pattern = r'\{[\s\S]+\}'
        match = re.search(json_pattern, response)
        if match is None:
            raise ValueError(f"Response does not contain JSON: {response}")
        return match.group(0)


class ChatRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    @classmethod
    def from_role(cls: Type[Self], role: str) -> "ChatRole":
        for chat_role in ChatRole:
            if chat_role.value == role:
                return chat_role
        raise ValueError(f"{role} is not a valid chat role")


@dataclass_json
@dataclasses.dataclass
class ChatMessage:
    role: ChatRole
    content: str

    def to_str_dict(self) -> Dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> Self:
        return cls(
            role=ChatRole.from_role(d["role"]),
            content=d["content"]
        )


@dataclass_json
@dataclasses.dataclass
class Chat:
    messages: List[ChatMessage]

    @classmethod
    def initialise_with_system(cls: Type["Chat"], system_prompt: Optional[str] = None) -> "Chat":
        if system_prompt is not None:
            return cls(
                messages=[
                    ChatMessage(
                        role=ChatRole.SYSTEM,
                        content=system_prompt
                    )
                ]
            )
        else:
            return cls(messages=[])

    def add(self, role: ChatRole, content: str) -> Self:
        self.messages += [ChatMessage(role, content)]
        return self

    def to_list(self) -> List[Dict[str, str]]:
        return [message.to_str_dict() for message in self.messages]

    @classmethod
    def from_list(cls, input_list: List[Dict[str, str]]) -> Self:
        messages = [ChatMessage.from_dict(item) for item in input_list]
        chat = cls(messages=messages)
        return chat


@dataclass_json
@dataclasses.dataclass
class ChatSession:
    chat: Chat

    @classmethod
    def generate(cls) -> Self:
        raise NotImplementedError

    def send(self, content: str) -> str:
        self.chat.add(ChatRole.USER, content)

        model: str = "gpt-3.5-turbo"

        # No types are provided but for Chat Completion at least a Dict with this hierarchy is expected
        completion: Dict[str, Any] = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
            model=model,
            messages=self.chat.to_list()
        )

        response_content: str = completion["choices"][0]["message"]["content"]

        self.chat.add(ChatRole.ASSISTANT, response_content)

        return response_content
