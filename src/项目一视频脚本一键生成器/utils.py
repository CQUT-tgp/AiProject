from  langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# from langchain_community.utilities import WikipediaAPIWrapper

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
def generate_script(subject: str, video_length: int, creativity: float, api_key: str):
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
        model="gpt-3.5-turbo",
        base_url='https://twapi.openai-hk.com/v1/',
        api_key=api_key
    )
    title_chain = title_template | model
    script_chain = script_template | model

    title = title_chain.invoke({'subject': subject}).content
    script = script_chain.invoke({'subject': subject, 'video_length': video_length}).content
    return title, script
