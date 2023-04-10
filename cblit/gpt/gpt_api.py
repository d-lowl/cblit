"""API for interacting with OpenAI GPT"""
import dataclasses
import json
import os
import re
from enum import Enum
from json import JSONDecodeError
from typing import Type, Dict, List, Optional, Self, Any, TypeVar

from dacite import from_dict
from dataclasses_json import dataclass_json, DataClassJsonMixin

import openai
from loguru import logger

from cblit.gpt.completion import Completion, CompletionUsage

openai.api_key = os.getenv("OPENAI_API_KEY")


class DataClassGPTJsonMixin(DataClassJsonMixin):
    @classmethod
    def from_gpt_response(cls: Type[Self], response: str) -> Self:
        json_str = cls.get_json_from_response(response)
        json_fixed_str = cls.fix_multiline_str(json_str)
        if json_str != json_fixed_str:
            logger.debug("JSON string was fixed:")
            logger.debug(json_str)
            logger.debug(json_fixed_str)
        return cls.from_json(json_fixed_str)

    @classmethod
    def list_from_gpt_response(cls: Type[Self], response: str) -> List[Self]:
        json_str = cls.get_json_list_from_response(response)
        json_fixed_str = cls.fix_multiline_str(json_str)
        if json_str != json_fixed_str:
            logger.debug("JSON string was fixed:")
            logger.debug(json_str)
            logger.debug(json_fixed_str)
        raw_list: List[Any] = json.loads(json_fixed_str)
        return [cls.from_json(json.dumps(item)) for item in raw_list]

    @staticmethod
    def get_json_list_from_response(response: str) -> str:
        return DataClassGPTJsonMixin._get_json_from_response(response, r'\[[\s\S]+\]')

    @staticmethod
    def get_json_from_response(response: str) -> str:
        return DataClassGPTJsonMixin._get_json_from_response(response, r'\{[\s\S]+\}')

    @staticmethod
    def _get_json_from_response(response: str, json_pattern: str) -> str:
        match = re.search(json_pattern, response)
        if match is None:
            raise ValueError(f"Response does not contain JSON: {response}")
        return match.group(0)

    @staticmethod
    def fix_multiline_str(json_str: str) -> str:
        in_str = False
        result = ""
        for x in json_str:
            if not in_str and (x == "\""):
                in_str = True
                result += x
            elif in_str and (x == "\""):
                in_str = False
                result += x
            elif in_str and x == "\n":
                result += "\\n"
            else:
                result += x
        return result


ExtendsDataClassGPTJsonMixin = TypeVar("ExtendsDataClassGPTJsonMixin", bound=DataClassGPTJsonMixin)


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

    def get_last(self, role: Optional[ChatRole] = None) -> ChatMessage:
        if role is None:
            return self.messages[-1]
        else:
            return [message for message in self.messages if message.role == role][-1]

    def remove(self, count: int) -> Self:
        self.messages = self.messages[:-count]
        return self


@dataclasses.dataclass
class ChatSession(DataClassJsonMixin):
    chat: Chat
    usage: CompletionUsage

    @classmethod
    def generate(cls) -> Self:
        raise NotImplementedError

    def send(self, content: str) -> str:
        self.chat.add(ChatRole.USER, content)

        model: str = "gpt-3.5-turbo"

        # No types are provided but for Chat Completion at least a Dict with this hierarchy is expected
        completion_dict: Dict[str, Any] = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
            model=model,
            messages=self.chat.to_list()
        )

        completion = from_dict(data_class=Completion, data=completion_dict)

        logger.debug(completion)

        response_content: str = completion.choices[0].message.content

        self.chat.add(ChatRole.ASSISTANT, response_content)
        self.usage.add(completion.usage)

        return response_content

    def regenerate(self) -> str:
        prompt = self.chat.get_last(ChatRole.USER).content
        self.chat.remove(2)
        return self.send(prompt)

    def send_structured(
            self,
            content: str,
            klass: Type[ExtendsDataClassGPTJsonMixin],
            no_retries: int = 3
    ) -> ExtendsDataClassGPTJsonMixin:
        response = self.send(content)
        for attempt in range(no_retries):
            try:
                instance = klass.from_gpt_response(response)
            except JSONDecodeError:
                logger.warning(
                    f"Retry {attempt}/{no_retries}: Failed to parse GPT response into class '{klass.__name__}': "
                    f"{response}"
                )
                response = self.regenerate()
            else:
                break
        else:
            raise Exception(
                f"All attempts to parse GPT response into class '{klass.__name__}' failed, last one: {response}")

        return instance
