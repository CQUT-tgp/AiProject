from typing import List

from  langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# from langchain_community.utilities import WikipediaAPIWrapper
from prompt_template import system_template_text, user_template_text
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
# 从LangChain导入必要的模块
from langchain import hub  # 用于获取预定义的提示模板
from langchain.agents import create_structured_chat_agent, AgentExecutor  # 创建和执行结构化聊天代理
from langchain.memory import ConversationBufferMemory  # 对话内存，存储历史消息
from langchain.schema import HumanMessage  # 表示人类用户发送的消息
from langchain.tools import BaseTool  # 自定义工具的基类
from langchain_openai import ChatOpenAI  # OpenAI聊天模型接口
from xiaohongshu_model import Xiaohongshu

'''
生成视频标题和脚本的函数
参数：
    subject:视频主题
    video_length:视频时长（分钟）
    creativity:创造力参数（控制模型输出的随机性)
    api_key: 密钥
返回:
    包含视频标题和脚本的元组
'''
u1 = "https://twapi.openai-hk.com/v1/"
u2 = "https://api.openai-hk.com/v1/chat/completions"
url = u1

de_key = 'hk-trgwr810000562521750852117519c51d05c5a9f65f5b84b'



def generate_script(subject: str, video_length: int, creativity: float, api_key: str,model_choice: str):
    title_template = ChatPromptTemplate.from_messages(
        [
            ('human','请为{subject}这个主题的视频想出一个吸引人的标题')
        ]
    )
    script_template = ChatPromptTemplate.from_messages(
        [
            ('human','请为{subject}这个主题的视频生成一个{video_length}分钟的脚本，内容需要抓人眼球，结尾有惊喜.')

        ]
    )
    model = ChatOpenAI(
        temperature=creativity,
        model=model_choice,
        base_url=url,
        api_key=api_key
    )
    title_chain = title_template | model
    script_chain = script_template | model

    title = title_chain.invoke({'subject': subject}).content
    script = script_chain.invoke({'subject': subject, 'video_length': video_length}).content
    return title, script

def generate_xiaohongshu(theme, openai_api_key,model_choice: str):
    model = ChatOpenAI(
        model=model_choice,
        base_url=url,
        api_key=openai_api_key
    )

    parser = PydanticOutputParser(pydantic_object=Xiaohongshu)

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_template_text),
        ('human', user_template_text)
    ])

    chain = prompt | model | parser

    result = chain.invoke({
        "theme": theme,
        "parser_instructions": parser.get_format_instructions()
    })

    return result  # 返回 Xiaohongshu 对象


from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

def get_chat_response(prompt,memory,api_key,model_choice: str):
    '''

    :param prompt:
    :param memory:
    :param api_key:
    :return:
    '''
    model = ChatOpenAI(
        model=model_choice,
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

# D:\1\作业\算法分析\AiProject\src\projectall\utils.py

def qa_agent(openai_api_key, memory, upload_file, question):
    model = ChatOpenAI(
        model='gpt-3.5-turbo',
        base_url=url,
        openai_api_key=de_key  # 注意这里是否应为传入的 openai_api_key？
    )

    file_content = upload_file.read()
    temp_file_path = 'temp.pdf'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)

    loader = PyPDFLoader(temp_file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "!", "?", "、", " "]
    )

    texts = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        base_url=url,
        model='text-embedding-3-large',
    )
    db = None
    try:
        # 添加 try-except 防止 embedding 失败导致程序崩溃
        db = FAISS.from_documents(texts, embeddings)
    except Exception as e:
        print("向量化失败")
    if db is None:  # ✅ 显式检查 db 是否为 None
        return {"error": "Database initialization failed"}
    retriever = db.as_retriever()
    qa = ConversationalRetrievalChain.from_llm(llm=model, retriever=retriever, memory=memory)
    response = qa.invoke({'chat_history': memory, 'question': question})
    return response



import json  # 用于JSON数据处理
from langchain_openai import ChatOpenAI  # 导入OpenAI聊天模型接口
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent  # 导入Pandas数据框代理创建工具

# 定义提示模板，指导AI如何响应不同类型的用户请求
PROMPT_TEMPLATE = """
你是一位数据分析助手，你的回应内容取决于用户的请求内容。

1. 对于文字回答的问题，按照这样的格式回答：
   {"answer": "<你的答案写在这里>"}
例如：
   {"answer": "订单量最高的产品ID是'MNWC3-067'"}

2. 如果用户需要一个表格，按照这样的格式回答：
   {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

3. 如果用户的请求适合返回条形图，按照这样的格式回答：
   {"bar": {"columns": ["A", "B", "C", ...], "data": [34, 21, 91, ...]}}

4. 如果用户的请求适合返回折线图，按照这样的格式回答：
   {"line": {"columns": ["A", "B", "C", ...], "data": [34, 21, 91, ...]}}

5. 如果用户的请求适合返回散点图，按照这样的格式回答：
   {"scatter": {"columns": ["A", "B", "C", ...], "data": [34, 21, 91, ...]}}
注意：我们只支持三种类型的图表："bar", "line" 和 "scatter"。


请将所有输出作为JSON字符串返回。请注意要将"columns"列表和数据列表中的所有字符串都用双引号包围。
例如：{"columns": ["Products", "Orders"], "data": [["32085Lip", 245], ["76439Eye", 178]]}

你要处理的用户请求如下： 
"""


def dataframe_agent(openai_api_key, df, query):
    """
    CSV数据分析智能体核心函数

    参数:
    - openai_api_key: OpenAI API密钥
    - df: 上传的CSV数据转换为的Pandas DataFrame
    - query: 用户的分析查询

    返回:
    - 包含分析结果的字典（文字回答、表格或图表数据）
    """
    # 初始化OpenAI聊天模型
    # model="gpt-4-turbo": 使用GPT-4 Turbo模型（需确认API支持）
    # openai_api_key: 传入API密钥
    # temperature=0: 输出更确定性，减少随机性
    model = ChatOpenAI(
        # model="gpt-4-turbo",
        model='gpt-3.5-turbo',
        openai_api_key=openai_api_key,
        temperature=0,
        base_url=url
    )

    # 创建Pandas数据框代理
    # llm=model: 使用初始化的OpenAI模型
    # df=df: 传入要分析的DataFrame
    # handle_parsing_errors=True: 自动处理解析错误
    # verbose=True: 打印详细执行日志
    agent = create_pandas_dataframe_agent(
        llm=model,
        df=df,
        agent_executor_kwargs={"handle_parsing_errors": True},
        verbose=True,
        allow_dangerous_code=True  # 显式启用危险代码执行
    )

    # 组合提示模板和用户查询
    prompt = PROMPT_TEMPLATE + query

    # 调用代理处理用户查询
    response = agent.invoke({"input": prompt})

    # 将响应转换为JSON字典
    print(response)
    print("--------------------------------------------")
    response_dict = json.loads(response["output"])
    return response_dict  # 返回分析结果字典

def use_tools(query):
    # 初始化OpenAI模型，temperature=0表示输出更确定性，减少随机性
    model = ChatOpenAI(model='gpt-3.5-turbo',
                       openai_api_key=de_key,
                       temperature=0,
                       base_url=url
                       )

    # 直接使用模型测试一个问题
    # invoke方法接受一个消息列表，这里只有一个人类消息

    # 创建自定义工具：文本字数计算工具
    # 继承BaseTool类并实现必要的属性和方法
    class TextLengthTool(BaseTool):
        name = "文本字数计算工具"  # 工具名称，供Agent识别
        description = "当你被要求计算文本的字数时，使用此工具"  # 工具描述，指导Agent何时使用

        def _run(self, text):  # 工具执行的核心逻辑
            return len(text)  # 返回文本长度
    class AddTool(BaseTool):
        name = "加法工具"
        description = "当你被要求计算两个数字的和时，使用此工具"
        def _run(self, list):

            di = list['numbers']
            a = di[0]
            b = di[1]
            return f"{a + b}"
    class SubtractTool(BaseTool):
        name = "减法工具"
        description = "当你被要求计算两个数字的差时，使用此工具"

        def _run(self, list):
            di = list['numbers']
            a = di[0]
            b = di[1]
            return f"{a - b}"
    class MultiplyTool(BaseTool):
        name = "乘法工具"
        description = "当你被要求计算两个数字的积时，使用此工具"

        def _run(self, list):
            di = list['numbers']
            a = di[0]
            b = di[1]
            return f"{a * b}"
    class DivideTool(BaseTool):
        name = "除法工具"
        description = "当你被要求计算两个数字的商时，使用此工具"

        def _run(self, list):
            di = list['numbers']
            a = di[0]
            b = di[1]

            return f"{a / b}"
    # 创建工具列表，将自定义工具添加进去
    tools = [TextLengthTool(), MultiplyTool(), DivideTool(),SubtractTool(),AddTool()]

    # 从LangChain Hub获取预定义的结构化聊天代理提示模板
    # hwchase17/structured-chat-agent是一个适合结构化工具使用的提示模

    # 构造 ChatPromptTemplate
    prompt = hub.pull("hwchase17/structured-chat-agent")
    agent = create_structured_chat_agent(
        llm=model,  # 使用之前初始化的OpenAI模型
        tools=tools,  # 使用自定义的文本字数计算工具
        prompt=prompt  # 使用从Hub获取的提示模板
    )

    # 初始化对话内存
    # memory_key指定存储对话历史的键名
    # return_messages=True表示返回消息对象列表而非字符串
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )

    # 创建代理执行器
    # 将代理、工具和内存组合在一起，设置为verbose模式以便查看执行过程
    # handle_parsing_errors=True表示自动处理解析错误
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,  # 必需参数：传入已创建的代理对象（Agent）
        tools=tools,  # 必需参数：传入代理可使用的工具列表
        memory=memory,
        verbose=True,  # 可选参数：是否打印详细日志（调试用）
        handle_parsing_errors=True  # 可选参数：是否自动处理工具调用格式错误
    )

    # 代理与执行器的关系：大脑与神经系统的类比
    # 结构化聊天代理：相当于 "大脑"，负责：
    # 理解问题（自然语言处理）
    # 制定解决方案（决定是否使用工具、使用哪个工具）
    # 整合信息（将工具结果转化为自然语言回答）
    # 代理执行器：相当于 "神经系统"，负责：
    # 传递指令（将代理的工具调用请求发送给工具）
    # 管理状态（存储对话历史，保持上下文连贯）
    # 处理异常（修复格式错误、重试失败的工具调用）

    # 使用代理执行器回答问题
    # 代理会判断是否需要使用工具，并生成相应的回答

    executor = agent_executor({"input": query})
    return executor
    # 测试一个不需要工具的问题
    # 代理会直接使用语言模型回答