import streamlit as st
from utils import generate_xiaohongshu
st.title('小红书文案生成器🎞')

with st.sidebar:
    api_key = st.text_input('请输入密钥', value='hk-0dhw9e1000055841f30e44fcb77836135617c3dcbfe8b084', type='password')
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
