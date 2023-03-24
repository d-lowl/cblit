"""API for interacting with OpenAI GPT"""
import dataclasses
import os
from enum import Enum
from typing import Type, Dict, List, Optional
from typing_extensions import Self

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


class ChatRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    @classmethod
    def from_role(cls: Type[Self], role: str) -> Self:
        for chat_role in ChatRole:
            if chat_role.value == role:
                return chat_role
        raise ValueError(f"{role} is not a valid chat role")


@dataclasses.dataclass
class ChatMessage:
    role: ChatRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclasses.dataclass
class Chat:
    messages: List[ChatMessage]

    def __init__(self, system_prompt: Optional[str] = None):
        if system_prompt is not None:
            self.messages = [
                ChatMessage(
                    role=ChatRole.SYSTEM,
                    content=system_prompt
                )
            ]
        else:
            self.messages = []

    def add(self, role: ChatRole, content: str) -> Self:
        self.messages += [ChatMessage(role, content)]
        return self

    def to_list(self) -> List[Dict[str, str]]:
        return [message.to_dict() for message in self.messages]


class ChatSession:
    model: str = "gpt-3.5-turbo"
    chat: Chat

    def __init__(self, system_prompt: Optional[str] = None):
        self.chat = Chat(system_prompt=system_prompt)

    def send(self, content: str) -> str:
        self.chat.add(ChatRole.USER, content)

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.chat.to_list()
        )

        response_content: str = completion["choices"][0]["message"]["content"]

        self.chat.add(ChatRole.ASSISTANT, response_content)

        return response_content
