from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

def qa_agent(openai_api_key,memory,upload_file, question):
    '''

    :param openai_api_key:
    :param memory:
    :param upload_file:
    :param question:
    :return:
    '''
    model = ChatOpenAI(
        model='gpt-3.5-turbo',
        base_url="https://api.chatanywhere.tech/v1",
        openai_api_key="sk-dycuAgES7nzKMgVPtsP0cO65bwrhTKJ5sWS8KUdO0lt3vdVT"

    )

    #读取上传pdf内容
    file_content = upload_file.read()

    #临时保存pdf到本地
    #由于langchain的pdf加载器需要文件路径，需要先保存到本地
    temp_file_path='temp.pdf'
    with open(temp_file_path,'wb') as temp_file:
        temp_file.write(file_content)

    loader = PyPDFLoader(temp_file_path)
    docs=loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n\n","\n","。", "!","?","、"," "])

    texts=text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key,
                                  base_url='https://api.chatanywhere.tech/v1',
                                  model='text-embedding-3-large',)

    db=FAISS.from_documents(texts,embeddings)

    retriever = db.as_retriever()
    #创建对话链
    #该对话链结合llm，检索其对话内容，实现基于文档的回答
    qa=ConversationalRetrievalChain.from_llm(llm=model,retriever=retriever,memory= memory)
    print(qa)
    #调用对话链处理用户问题，链会自动检索数据库相应的文本并生成回答
    response=qa.invoke({'chat_history':memory,'question':question})
    return response