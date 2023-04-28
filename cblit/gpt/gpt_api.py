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
from openai import InvalidRequestError

from cblit.errors.errors import CblitOpenaiError
from cblit.gpt.completion import Completion, CompletionUsage

openai.api_key = os.getenv("OPENAI_API_KEY")

CRITICAL_PRIORITY = 999
FORGET_PRIORITY = -1
NORMAL_PRIORITY = 100

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
    priority: int

    def to_openai_dict(self) -> Dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }

    # @classmethod
    # def from_dict(cls, d: Dict[str, str]) -> Self:
    #     return cls(
    #         role=ChatRole.from_role(d["role"]),
    #         content=d["content"],
    #         priority=d["priority"]
    #     )


@dataclass_json
@dataclasses.dataclass
class Chat:
    full_history: List[ChatMessage]
    messages: List[ChatMessage]

    @classmethod
    def initialise_with_system(cls: Type["Chat"], system_prompt: Optional[str] = None) -> "Chat":
        if system_prompt is not None:
            system_msg = ChatMessage(
                role=ChatRole.SYSTEM,
                content=system_prompt,
                priority=CRITICAL_PRIORITY
            )
            return cls(
                messages=[system_msg],
                full_history=[system_msg],
            )
        else:
            return cls(messages=[], full_history=[])

    def add(self, role: ChatRole, content: str, priority: int) -> Self:
        self.messages += [ChatMessage(role, content, priority)]
        self.full_history += [ChatMessage(role, content, priority)]
        return self

    def to_list(self) -> List[Dict[str, str]]:
        return [message.to_openai_dict() for message in self.messages]

    def get_last(self, role: Optional[ChatRole] = None) -> ChatMessage:
        if role is None:
            return self.messages[-1]
        else:
            return [message for message in self.messages if message.role == role][-1]

    def remove(self, count: int) -> Self:
        self.messages = self.messages[:-count]
        return self

    def remove_priority(self) -> Self:
        lowest_priority = CRITICAL_PRIORITY + 1
        lowest_start_index = -1
        lowest_stop_index = -1
        is_current_span = False

        for index, message in enumerate(self.messages):
            if not is_current_span:
                if message.role == ChatRole.USER and message.priority < lowest_priority:
                    lowest_priority = message.priority
                    lowest_start_index = index
                    is_current_span = True
            else:
                if message.role == ChatRole.USER:
                    if message.priority < lowest_priority:
                        lowest_priority = message.priority
                        lowest_start_index = index
                    else:
                        lowest_stop_index = index - 1
                        is_current_span = False

        if is_current_span:
            lowest_stop_index = len(self.messages) - 1

        logger.debug(
            f"Removing these lowest priority messages: {self.messages[lowest_start_index:lowest_stop_index+1]}"
        )
        self.messages = self.messages[:lowest_start_index] + self.messages[lowest_stop_index+1:]

        return self


@dataclasses.dataclass
class ChatSession(DataClassJsonMixin):
    chat: Chat
    usage: CompletionUsage

    @classmethod
    async def generate(cls) -> Self:
        raise NotImplementedError

    async def _send(self, chat: Chat) -> str:
        model: str = "gpt-3.5-turbo"

        try:
            # No types are provided but for Chat Completion at least a Dict with this hierarchy is expected
            completion_dict: Dict[str, Any] = await openai.ChatCompletion.acreate(  # type: ignore[no-untyped-call]
                model=model,
                messages=chat.to_list()
            )
        except InvalidRequestError as e:
            if "This model's maximum context length" in e._message:
                raise CblitOpenaiError("The request was marked invalid, because of the context length")
            else:
                raise e

        completion = from_dict(data_class=Completion, data=completion_dict)

        logger.debug(completion)

        if completion.choices[0].finish_reason == "length":
            raise CblitOpenaiError("The response was not finished, because the length was exceeded")

        response_content: str = completion.choices[0].message.content
        self.usage.add(completion.usage)

        return response_content

    async def send(self, content: str, priority: int) -> str:
        logger.debug(f"Sending (priority={priority}): {content}")
        self.chat.add(ChatRole.USER, content, priority)

        while True:
            try:
                response_content = await self._send(self.chat)
                break
            except CblitOpenaiError as e:
                logger.warning(e)
                logger.warning("Removing chat messages from the based on priority")
                self.chat.remove_priority()
                logger.warning("Retrying...")

        if priority >= 0:
            self.chat.add(ChatRole.ASSISTANT, response_content, priority)

        if priority < 0:
            self.chat.remove(1)

        return response_content

    async def next(self, priority: int) -> str:
        logger.debug(f"Getting next (priority={priority})")
        response_content = await self._send(self.chat)

        if priority >= 0:
            self.chat.add(ChatRole.ASSISTANT, response_content, priority)

        return response_content

    async def regenerate(self) -> str:
        last = self.chat.get_last(ChatRole.USER)
        prompt = last.content
        priority = last.priority
        logger.debug(f"Regenerating (priority={priority}): {prompt}")
        self.chat.remove(2)
        return await self.send(prompt, priority)

    async def send_structured(
            self,
            content: str,
            klass: Type[ExtendsDataClassGPTJsonMixin],
            priority: int,
            no_retries: int = 3
    ) -> ExtendsDataClassGPTJsonMixin:
        response = await self.send(content, priority)
        for attempt in range(no_retries):
            try:
                instance = klass.from_gpt_response(response)
            except JSONDecodeError:
                logger.warning(
                    f"Retry {attempt}/{no_retries}: Failed to parse GPT response into class '{klass.__name__}': "
                    f"{response}"
                )
                response = await self.regenerate()
            else:
                break
        else:
            raise Exception(
                f"All attempts to parse GPT response into class '{klass.__name__}' failed, last one: {response}")

        return instance
