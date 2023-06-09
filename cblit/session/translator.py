"""Langchain conlang translator module."""
import json
from typing import Self, cast

import faiss
from langchain import FAISS, InMemoryDocstore, LLMChain, PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms.base import BaseLLM
from langchain.memory import VectorStoreRetrieverMemory
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import Document
from pydantic import BaseModel, Field

from cblit.cli.session_wrapper import wrap_session_method
from cblit.llm.llm import get_llm
from cblit.session.session import BaseSession

TRANSLATION_TEMPLATE = """
You are a translator, who knows a conlang named {conlang_name} perfectly.
You can translate anything from English to {conlang_name}, and from {conlang_name} to English.

Relevant already known translations are provided here:
{phrasebook}

(You do not need to use these pieces of information if not relevant)

{format_instructions}

Translate from {from_language} to {to_language}: "{phrase}"
""".strip()


class ConlangEntry(BaseModel):
    """Entry in a conlang dictionary."""
    english: str = Field(description="This sentence in English")
    conlang: str = Field(description="This sentence in Conlang")

    def to_dict(self) -> dict[str, str]:
        """Turn entry into a dict.

        Returns:
            dict[str, str]: Dictionary with ConlangEntry fields
        """
        return cast(dict[str, str], json.loads(self.json()))


class TranslatorMemory(VectorStoreRetrieverMemory):
    """Translator memory."""
    def __init__(self) -> None:
        """Initialise translator's memory."""
        embedding_size = 1536  # Dimensions of the OpenAIEmbeddings
        index = faiss.IndexFlatL2(embedding_size)
        embedding_fn = OpenAIEmbeddings().embed_query  # type: ignore [call-arg]
        vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {})

        # In actual usage, you would set `k` to be a higher value, but we use k=1 to show that
        # the vector lookup still returns the semantically relevant information
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        super().__init__(retriever=retriever, memory_key="phrasebook")

    def save_entry(self, entry: ConlangEntry) -> None:
        """Save conlang entry to the memory.

        Args:
            entry (ConlangEntry): entry to save
        """
        self.save_context(entry.dict(), {})

    def get_entries(self, language: str, phrase: str) -> dict[str, list[Document] | str]:
        """Get entries that are relevant.

        Args:
            language (str): language of query
            phrase (str): query phrase

        Returns:
            dict[str, list[Document] | str]: relevant memory entries
        """
        return self.load_memory_variables({language: phrase})


class TranslatorSession(BaseSession):
    """Translator session."""
    conlang_name: str
    llm: BaseLLM
    memory: TranslatorMemory
    translation_parser: PydanticOutputParser[ConlangEntry]
    translator_chain: LLMChain

    def __init__(self, conlang_name: str, initial_entry: ConlangEntry) -> None:
        """Initialise Langchain translator.

        Args:
            conlang_name (str): name of the constructed language
            initial_entry (str): initial entry in the translators memory
        """
        self.conlang_name = conlang_name
        self.memory = TranslatorMemory()
        self.memory.save_context({}, initial_entry.to_dict())
        self.llm = get_llm(temperature=0.7)
        self.translation_parser = PydanticOutputParser(pydantic_object=ConlangEntry)
        prompt = PromptTemplate(
            template=TRANSLATION_TEMPLATE,
            input_variables=[
                "phrasebook",
                "from_language",
                "to_language",
                "phrase"
            ],
            partial_variables={
                "conlang_name": self.conlang_name,
                "format_instructions": self.translation_parser.get_format_instructions()
            }
        )
        self.translator_chain = LLMChain(
            llm=self.llm,
            verbose=True,
            prompt=prompt,
        )

    async def generate(self) -> Self:
        """Nothing to explicitly generate."""
        return self

    @wrap_session_method()
    async def translate(self, from_language: str, to_language: str, phrase: str) -> ConlangEntry:
        """Translate phrases from one language to another.

        Args:
            from_language (str): language to translate from
            to_language (str): language to translate to
            phrase (str): phrase to translate

        Returns:
            ConlangEntry: entry in conlang dictionary with the phrase in English and Conlang
        """
        phrasebook = self.memory.get_entries(from_language, phrase)["phrasebook"]
        entry = self.translation_parser.parse(await self.translator_chain.arun(
            phrasebook=phrasebook,
            from_language=from_language,
            to_language=to_language,
            phrase=phrase
        ))
        self.memory.save_entry(entry)

        return entry

    @wrap_session_method()
    async def translate_to_conlang(self, phrase: str) -> str:
        """Translate a phrase from English to Conlang.

        Args:
            phrase (str): phrase to translate

        Returns:
            str: phrase in English
        """
        return cast(str, (await self.translate("English", self.conlang_name, phrase)).conlang)

    @wrap_session_method()
    async def translate_from_conlang(self, phrase: str) -> str:
        """Translate a phrase from Conlang to English.

        Args:
            phrase (str): phrase to translate

        Returns:
            str: phrase in Conlang
        """
        return cast(str, (await self.translate(self.conlang_name, "English", phrase)).english)
