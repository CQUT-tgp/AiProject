
from typing import List
from pydantic import BaseModel
class Xiaohongshu(BaseModel):
    title: List[str]
    content: str # 修改此处

