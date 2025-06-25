import streamlit as st
from utils import generate_script
from utils import generate_xiaohongshu
from utils import get_chat_response
# 从LangChain导入必要的模块
from langchain import hub  # 用于获取预定义的提示模板
from langchain.agents import create_structured_chat_agent, AgentExecutor  # 创建和执行结构化聊天代理
from langchain.memory import ConversationBufferMemory  # 对话内存，存储历史消息
from langchain.schema import HumanMessage  # 表示人类用户发送的消息
from langchain.tools import BaseTool  # 自定义工具的基类
from langchain_openai import ChatOpenAI  # OpenAI聊天模型接口

import pandas as pd  # 导入Pandas，用于数据处理
import streamlit as st  # 导入Streamlit，用于构建Web界面
from utils import dataframe_agent  # 从utils模块导入后端定义的dataframe_agent函数
from utils import use_tools
from langchain.memory import ConversationBufferMemory
from utils import qa_agent

def create_chart(input_data, chart_type):
    """
    创建数据可视化图表

    参数:
    - input_data: 包含图表数据的字典（columns和data）
    - chart_type: 图表类型（bar/line/scatter）
    """
    # 将输入数据转换为Pandas DataFrame
    df_data = pd.DataFrame(input_data["data"], columns=input_data["columns"])
    df_data.set_index(input_data["columns"][0], inplace=True)  # 设置索引列

    # 根据图表类型创建相应的可视化
    if chart_type == "bar":
        st.bar_chart(df_data)  # 创建条形图
    elif chart_type == "line":
        st.line_chart(df_data)  # 创建折线图
    elif chart_type == "scatter":
        st.scatter_chart(df_data)  # 创建散点图

# 设置默认key
k1 = 'sk-6mLVgHQIe5WOwibRSEhCAb0ed7uipfC4QY79mKSmGVNRe2il'
k2 = 'hk-trgwr810000562521750852117519c51d05c5a9f65f5b84b'

k2_2 = 'hk-pawwtk10000562536eaccec2bda1f2d56abe9527a4fa16e4'
api_key =  k2_2

# 初始化 session_state 中的页面状态
if 'page' not in st.session_state:
    st.session_state.page = ''

# 设置五个页面按钮
st.sidebar.title('AI')
if st.sidebar.button('视频脚本生成', key='video_script'):
    st.session_state.page = '视频脚本生成'
if st.sidebar.button('文案生成', key='copywriting'):
    st.session_state.page = '文案生成'
if st.sidebar.button('ChatGPT', key='chatgpt'):
    st.session_state.page = 'ChatGPT'
if st.sidebar.button('智能PDF问答', key='pdf_qa'):
    st.session_state.page = '智能PDF问答'
if st.sidebar.button('图表处理', key='chart_processing'):
    st.session_state.page = '图表处理'
if st.sidebar.button('其他工具', key='tools'):
    st.session_state.page = '其他工具'

# 点击切换后显示对应页面内容
if st.session_state.page == '视频脚本生成':
    st.title('视频脚本生成器')

    title = st.text_input('请输入标题')
    viodeo_length = st.number_input('请输入视频长度', min_value=1, max_value=60)
    creativity = st.slider('请选择创造力(越小越严谨)', max_value=1.0, min_value=0.1, step=0.01)
    # 默认密钥为 hk-0dhw9e1000055841f30e44fcb77836135617c3dcbfe8b084

    with st.sidebar:
        api_key = st.text_input('请输入密钥', value=api_key,
                                type='password')
        st.markdown('密钥获取方式：[点击获取](https://www.yunyin.org/api/key)')
    submit = st.button('提交')
    if submit and not title:
        st.info('请输入标题')
        st.stop
    if submit and not api_key:
        st.info('请输入密钥')
        st.stop
    if submit and not viodeo_length:
        st.info('请输入视频长度')
        st.stop

    # 点击按钮提交
    if submit:
        # 提示已经提交
        with st.spinner('正在生成中...'):
            title_result, script_result = generate_script(title, viodeo_length, creativity, api_key)
        st.success('生成成功')
        st.write('标题:')
        st.write(title_result)
        st.write('脚本:')
        st.write(script_result)
elif st.session_state.page == '文案生成':
    st.title('小红书文案生成器🎞')

    with st.sidebar:
        api_key = st.text_input('请输入密钥', value=api_key,
                                type='password')
        st.markdown('密钥获取方式：[点击获取](https://www.yunyin.org/api/key)')
    theme = st.text_input('请输入主题')
    submit = st.button('提交')
    if submit and not theme:
        st.info('请输入主题')
        st.stop
    if submit and not api_key:
        st.info('请输入密钥')
        st.stop
    if submit:
        # 提示已经提交
        with st.spinner('正在生成中...'):
            result = generate_xiaohongshu(theme, api_key)
        st.divider()
        left, right = st.columns(2)

        with left:
            st.markdown('### 小红书标题1')
            st.write(result.title[0])
            st.markdown('### 小红书标题2')
            st.write(result.title[1])
            st.markdown('### 小红书标题3')
            st.write(result.title[2])
            st.markdown('### 小红书标题4')
            st.write(result.title[3])
            st.markdown('### 小红书标题5')
            st.write(result.title[4])
        with right:
            st.markdown('### 小红书正文')
            st.write(result.content)

elif st.session_state.page == 'ChatGPT':

    st.title('🗨 克隆ChatGPT')

    with st.sidebar:
        openai_api_key = st.text_input('请输入OpenAI API密钥',
                                       value=api_key, type='password')
        st.markdown('[获取OpenAI API密钥](https://openai-hk.com/v3/ai/key)')

    # 管理会话状态{Session State},这是Streamlit保持页面刷新时数据不丢失的机制
    if 'memory' not in st.session_state:
        st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
        # 初始化对话历史，添加一条AI的欢迎消息
        st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以你帮你的吗？'}]

    for message in st.session_state['messages']:
        st.chat_message(message['role']).write(message['content'])

    # 获取用户输入
    prompt = st.chat_input()

    if prompt:
        if not openai_api_key:
            st.info('请输入你的OpenAI API Key')
            st.stop()

        # 添加用户消息到对话历史
        st.session_state['messages'].append({'role': 'human', 'content': prompt})
        st.chat_message(message['role']).write(prompt)

        with st.spinner('AI正在思考中，请稍等.....'):
            response = get_chat_response(prompt, st.session_state['memory'], openai_api_key)

            # 处理AI响应并添加到对话历史
            msg = {'role': 'ai', 'content': response}
            st.session_state['messages'].append(msg)
            st.chat_message('ai').write(response)

elif st.session_state.page == '智能PDF问答':
    st.title("智能PDF问答工具")

    with st.sidebar:
        openai_api_key = st.text_input("请输入OpenAI API Key",
                                       value=api_key, type="password")
        st.markdown("[获取OpenAI API Key](https://platform.openai.com/account/api-keys)")

    # 初始化会话状态中的对话内存
    if "memory" not in st.session_state:
        st.session_state["memory"] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="answer")

    # 上传文件
    uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
    question = st.text_input("请对pdf内容进行提问", disabled=not uploaded_file)
    # 检查文件和问题是否存在，且api密钥是否输入
    if uploaded_file and question and not openai_api_key:
        st.info("请输入OpenAI API密钥")

    # 处理用户提问
    if uploaded_file and question and openai_api_key:
        with st.spinner("正在处理..."):
            response = qa_agent(openai_api_key, st.session_state['memory'], uploaded_file, question)

        st.write('###答案')
        st.write(response['answer'])

        st.session_state['chat_history'] = response['chat_history']

    # 显示聊天历史
    if 'chat_history' in st.session_state:
        with st.expander('历史消息'):
            # 遍历聊天历史，按人机消息对显示
            for i in range(0, len(st.session_state['chat_history']), 2):
                human_message = st.session_state['chat_history'][i]
                ai_message = st.session_state['chat_history'][i + 1]
                st.write('###Human')
                st.write(human_message.content)
                st.write('###AI')
                st.write(ai_message.content)
                if i < len(st.session_state['chat_history']) - 2:
                    st.divider()

elif st.session_state.page == '图表处理':

    st.title("💡 CSV数据分析智能工具")  # 设置页面标题

    with st.sidebar:
        # 在侧边栏创建API密钥输入框
        openai_api_key = st.text_input("请输入OpenAI API密钥：",value=api_key, type="password")
        st.markdown("[获取OpenAI API key](https://platform.openai.com/account/api-keys)")  # 添加API密钥获取链接

    # 创建文件上传组件
    data = st.file_uploader("上传你的数据文件（CSV格式）：", type="csv")
    if data:
        # 读取CSV文件并存储到会话状态
        st.session_state["df"] = pd.read_csv(data)
        with st.expander("原始数据"):
            st.dataframe(st.session_state["df"])  # 显示原始数据表格

    # 创建查询输入区域和按钮
    query = st.text_area("请输入你关于以上表格的问题，或数据提取请求，或可视化要求：")
    button = st.button("生成回答")

    # 处理用户点击按钮事件
    if button and not openai_api_key:
        st.info("请输入你的OpenAI API密钥")  # 提示输入API密钥
    if button and "df" not in st.session_state:
        st.info("请先上传数据文件")  # 提示上传数据文件
    if button and openai_api_key and "df" in st.session_state:
        with st.spinner("AI正在思考中，请稍等..."):
            # 调用后端函数获取分析结果
            response_dict = dataframe_agent(openai_api_key, st.session_state["df"], query)

            # 根据响应类型展示结果
            if "answer" in response_dict:
                st.write(response_dict["answer"])  # 显示文字回答
            if "table" in response_dict:
                # 显示表格数据
                st.table(pd.DataFrame(response_dict["table"]["data"],
                                      columns=response_dict["table"]["columns"]))
            if "bar" in response_dict:
                create_chart(response_dict["bar"], "bar")  # 创建条形图
            if "line" in response_dict:
                create_chart(response_dict["line"], "line")  # 创建折线图
            if "scatter" in response_dict:
                create_chart(response_dict["scatter"], "scatter")  # 创建散点图
elif st.session_state.page == "其他工具":
    st.title("其他工具")

    with st.sidebar:
        openai_api_key = st.text_input("请输入OpenAI API Key",
                                       value=api_key, type="password")
        st.markdown("[获取OpenAI API Key](https://platform.openai.com/account/api-keys)")
    message = st.text_input("请输入你的问题：")
    # 在页面上显示可用哪些工具的名称
    col1, col2 = st.columns(2)

    with col1:
        st.info("字数统计")
    #
    # with col2:
    #     st.info("数据运算")

    if message:
        response = use_tools(message)
        st.write(response["output"])



