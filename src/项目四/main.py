import streamlit as st
from langchain.memory import ConversationBufferMemory
from utils import qa_agent

st.title("智能PDF问答工具")

with st.sidebar:
    openai_api_key = st.text_input("请输入OpenAI API Key",value='sk-6mLVgHQIe5WOwibRSEhCAb0ed7uipfC4QY79mKSmGVNRe2il', type="password")
    st.markdown("[获取OpenAI API Key](https://platform.openai.com/account/api-keys)")

#初始化会话状态中的对话内存
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="answer")

#上传文件
uploaded_file = st.file_uploader("上传PDF文件", type=["pdf"])
question = st.text_input("请对pdf内容进行提问",disabled=not uploaded_file)
#检查文件和问题是否存在，且api密钥是否输入
if uploaded_file and question and not openai_api_key:
    st.info("请输入OpenAI API密钥")

#处理用户提问
if uploaded_file and question and openai_api_key:
    with st.spinner("正在处理..."):
        response=qa_agent(openai_api_key,st.session_state['memory'],uploaded_file, question)

    st.write('###答案')
    st.write(response['answer'])

    st.session_state['chat_history']=response['chat_history']

#显示聊天历史
if 'chat_history' in st.session_state:
    with st.expander('历史消息'):
        #遍历聊天历史，按人机消息对显示
        for i in range(0,len(st.session_state['chat_history']),2):
            human_message=st.session_state['chat_history'][i]
            ai_message=st.session_state['chat_history'][i+1]
            st.write('###Human')
            st.write(human_message.content)
            st.write('###AI')
            st.write(ai_message.content)
            if i<len(st.session_state['chat_history'])-2:
                st.divider ()