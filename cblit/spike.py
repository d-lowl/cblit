from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.memory import VectorStoreRetrieverMemory


import faiss

from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS


def memory() -> VectorStoreRetrieverMemory:
    OpenAI(temperature=0.7)  # type: ignore [call-arg]
    phrasebook = [
        {"english": "Hello", "translation": "Finigutixa"},
        {"english": "Goodbye", "translation": "Nuyetetega"},
        {"english": "Thank you", "translation": "Karanigovu"},
        {"english": "Please", "translation": "Meranuvu"},
        {"english": "Sorry", "translation": "Kaploxa"},
        {"english": "What is your name?", "translation": "Ceil faglix?"},
        {"english": "My name is ____", "translation": "Faglix _____"},
        {"english": "Passport", "translation": "Sidcanivu"},
        {"english": "Document", "translation": "Zeketira"},
        {"english": "Work", "translation": "Lakotofix"},
        {"english": "Immigration office", "translation": "Jogolaladixme"},
        {"english": "I want to register", "translation": "Lakotoxauta gorfabe"},
        {"english": "Required", "translation": "Taxicubora"},
        {"english": "I do not understand", "translation": "Gorfanate ciuxpaceit"},
        {"english": "Too fast", "translation": "Huragupanga"},
        {"english": "Orchard", "translation": "Tolorraxo"},
        {"english": "The flowers are blooming in the meadow.", "translation": "Prec na ca ceh tiôplox."}
    ]
    embedding_size = 1536  # Dimensions of the OpenAIEmbeddings
    index = faiss.IndexFlatL2(embedding_size)
    embedding_fn = OpenAIEmbeddings().embed_query  # type: ignore [call-arg]
    vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {})

    # In actual usage, you would set `k` to be a higher value, but we use k=1 to show that
    # the vector lookup still returns the semantically relevant information
    retriever = vectorstore.as_retriever(search_kwargs=dict(k=3))
    memory = VectorStoreRetrieverMemory(retriever=retriever)

    for phrase in phrasebook:
        memory.save_context(phrase, {})

    return memory




if __name__ == "__main__":
    # main()
    ...
