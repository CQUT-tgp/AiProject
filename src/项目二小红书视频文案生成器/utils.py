from prompt_template import system_template_text, user_template_text
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from xiaohongshu_model import Xiaohongshu

def generate_xiaohongshu(theme, openai_api_key):
    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        base_url='https://twapi.openai-hk.com/v1/',
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
