import langchain
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from cblit.gpt.officer import build_officer_langchain_prompt


def main():
    llm = OpenAI(temperature=0)
    prompt = build_officer_langchain_prompt()
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationBufferMemory(
            human_prefix="Visitor",
            ai_prefix="Officer"
        ),
        prompt=prompt,
    )
    ret = conversation.predict(input="Hi there!")
    print(ret)
    ret = conversation.predict(input="Do I know you!")
    print(ret)

    for i in range(50):
        ret = conversation.predict(input="I want to register, how?")
        print(ret)


if __name__ == "__main__":
    main()