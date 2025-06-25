# 从LangChain导入必要的模块
from langchain import hub  # 用于获取预定义的提示模板
from langchain.agents import create_structured_chat_agent, AgentExecutor  # 创建和执行结构化聊天代理
from langchain.memory import ConversationBufferMemory  # 对话内存，存储历史消息
from langchain.schema import HumanMessage  # 表示人类用户发送的消息
from langchain.tools import BaseTool  # 自定义工具的基类
from langchain_openai import ChatOpenAI  # OpenAI聊天模型接口

# 初始化OpenAI模型，temperature=0表示输出更确定性，减少随机性
model = ChatOpenAI(
    model = 'gpt-3.5-turbo',
    openai_api_key = 'hk-trgwr810000562521750852117519c51d05c5a9f65f5b84b',
    openai_api_base = 'https://twapi.openai-hk.com/v1/',
    temperature=0
)
# 直接使用模型测试一个问题
# invoke方法接受一个消息列表，这里只有一个人类消息
model.invoke([HumanMessage(content="'君不见黄河之水天上来奔流到海不复回'，这句话的字数是多少？")])

# 创建自定义工具：文本字数计算工具
# 继承BaseTool类并实现必要的属性和方法
class TextLengthTool(BaseTool):
    name = "文本字数计算工具"  # 工具名称，供Agent识别
    description = "当你被要求计算文本的字数时，使用此工具"  # 工具描述，指导Agent何时使用

    def _run(self, text):  # 工具执行的核心逻辑
        # 处理JSON输入格式
        if isinstance(text, dict):
            if "title" in text:
                text = text["title"]
            elif "text" in text:
                text = text["text"]

        # 处理字符串输入
        if isinstance(text, str):
            return len(text)
        else:
            # 处理意外输入类型
            return f"错误：输入类型应为字符串，实际收到 {type(text).__name__}"

    async def _arun(self, text):
        return self._run(text)

# 创建工具列表，将自定义工具添加进去
tools = [TextLengthTool()]

# 从LangChain Hub获取预定义的结构化聊天代理提示模板
# hwchase17/structured-chat-agent是一个适合结构化工具使用的提示模板
prompt = hub.pull("hwchase17/structured-chat-agent")
print(prompt)  # 打印提示模板，了解其结构和内容
#
#
agent = create_structured_chat_agent(
    llm=model,  # 使用之前初始化的OpenAI模型
    tools=tools,  # 使用自定义的文本字数计算工具
    prompt=prompt  # 使用从Hub获取的提示模板
)
#
# 初始化对话内存
# memory_key指定存储对话历史的键名
# return_messages=True表示返回消息对象列表而非字符串
memory = ConversationBufferMemory(
    memory_key='chat_history',
    return_messages=True
)
#
# # 创建代理执行器
# # 将代理、工具和内存组合在一起，设置为verbose模式以便查看执行过程
# # handle_parsing_errors=True表示自动处理解析错误
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
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
print(agent_executor.invoke({"input": "君不见黄河之水天上来奔流到海不复回'，这句话的字数是多少？"}))

# 测试一个不需要工具的问题
# 代理会直接使用语言模型回答
print(agent_executor.invoke({"input": "请你充当我的物理老师，告诉我什么是量子力学"}))