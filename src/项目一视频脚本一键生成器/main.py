from utils import generate_script
import streamlit as st
def video_script_generator(st):
    st.title('视频脚本生成器')

    title = st.text_input('请输入标题')
    viodeo_length = st.number_input('请输入视频长度', min_value=1, max_value=60)
    creativity = st.slider('请选择创造力(越小越严谨)', max_value=1.0, min_value=0.1, step=0.01)
    # 默认密钥为 hk-0dhw9e1000055841f30e44fcb77836135617c3dcbfe8b084

    api_key = st.text_input('请输入密钥', value='hk-0dhw9e1000055841f30e44fcb77836135617c3dcbfe8b084', type='password')
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
