from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

def get_chat_response(prompt,memory,api_key):
    '''

    :param prompt:
    :param memory:
    :param api_key:
    :return:
    '''
    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        base_url='https://twapi.openai-hk.com/v1/',
        api_key=api_key
    )
    chain = ConversationChain(
        llm=model,
        memory=memory
    )
    response = chain.invoke({
        "input": prompt
    })
    return response['response']
memory = ConversationBufferMemory(return_messages=True)
