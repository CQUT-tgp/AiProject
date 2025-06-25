import os
from langchain import hub
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

# 定义生成Blender长方体脚本的工具
class BlenderBoxTool(BaseTool):
    name: str = "Blender长方体生成工具"
    description: str = "根据输入的长宽高（格式：长,宽,高），生成Blender可用的长方体建模脚本"

    def _run(self, size: str) -> str:
        try:
            if isinstance(size, dict):
                if "size" in size:
                    size = size["size"]
                elif "dimensions" in size:
                    size = size["dimensions"]
            
            x, y, z = map(float, str(size).split(","))
        except:
            return "输入格式错误，应为形如 '2,3,4' 的数字字符串。"

        script_content = f"""
import bpy

# 删除所有对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 创建长方体
bpy.ops.mesh.primitive_cube_add(size=1)
obj = bpy.context.active_object
obj.scale = ({x / 2}, {y / 2}, {z / 2})
obj.name = "CustomBox_{x}x{y}x{z}"

print(f"已创建长方体: 长={x}, 宽={y}, 高={z}")
        """.strip()

        # 保存到当前目录
        save_path = os.path.join(os.getcwd(), "generated_box.py")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return f"长方体脚本已生成，尺寸：{x}×{y}×{z}，保存在：{save_path}"

    async def _arun(self, size: str) -> str:
        return self._run(size)

# 定义生成Blender球体脚本的工具
class BlenderSphereTool(BaseTool):
    name: str = "Blender球体生成工具"
    description: str = "根据输入的半径，生成Blender可用的球体建模脚本"

    def _run(self, radius: str) -> str:
        try:
            if isinstance(radius, dict):
                if "radius" in radius:
                    radius = radius["radius"]
                elif "size" in radius:
                    radius = radius["size"]
            
            r = float(str(radius))
        except:
            return "输入格式错误，应为数字字符串，如 '2.5'"

        script_content = f"""
import bpy

# 删除所有对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 创建球体
bpy.ops.mesh.primitive_uv_sphere_add(radius={r})
obj = bpy.context.active_object
obj.name = "CustomSphere_r{r}"

print(f"已创建球体: 半径={r}")
        """.strip()

        save_path = os.path.join(os.getcwd(), "generated_sphere.py")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return f"球体脚本已生成，半径：{r}，保存在：{save_path}"

    async def _arun(self, radius: str) -> str:
        return self._run(radius)

# 定义生成Blender圆柱体脚本的工具
class BlenderCylinderTool(BaseTool):
    name: str = "Blender圆柱体生成工具"
    description: str = "根据输入的半径和高度（格式：半径,高度），生成Blender可用的圆柱体建模脚本"

    def _run(self, dimensions: str) -> str:
        try:
            if isinstance(dimensions, dict):
                if "dimensions" in dimensions:
                    dimensions = dimensions["dimensions"]
                elif "size" in dimensions:
                    dimensions = dimensions["size"]
            
            radius, height = map(float, str(dimensions).split(","))
        except:
            return "输入格式错误，应为形如 '2,5' 的数字字符串（半径,高度）。"

        script_content = f"""
import bpy

# 删除所有对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 创建圆柱体
bpy.ops.mesh.primitive_cylinder_add(radius={radius}, depth={height})
obj = bpy.context.active_object
obj.name = "CustomCylinder_r{radius}_h{height}"

print(f"已创建圆柱体: 半径={radius}, 高度={height}")
        """.strip()

        save_path = os.path.join(os.getcwd(), "generated_cylinder.py")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return f"圆柱体脚本已生成，半径：{radius}，高度：{height}，保存在：{save_path}"

    async def _arun(self, dimensions: str) -> str:
        return self._run(dimensions)

# 定义Blender材质添加工具
class BlenderMaterialTool(BaseTool):
    name: str = "Blender材质添加工具"
    description: str = "为当前选中的对象添加材质，输入格式：颜色名称或RGB值（如 'red' 或 '1,0,0'）"

    def _run(self, color: str) -> str:
        try:
            if isinstance(color, dict):
                if "color" in color:
                    color = color["color"]
            
            color = str(color).lower().strip()
            
            # 预定义颜色
            color_map = {
                'red': (1, 0, 0),
                'green': (0, 1, 0),
                'blue': (0, 0, 1),
                'yellow': (1, 1, 0),
                'purple': (1, 0, 1),
                'cyan': (0, 1, 1),
                'white': (1, 1, 1),
                'black': (0, 0, 0),
                'gray': (0.5, 0.5, 0.5),
                'orange': (1, 0.5, 0)
            }
            
            if color in color_map:
                r, g, b = color_map[color]
            else:
                # 尝试解析RGB值
                r, g, b = map(float, color.split(","))
                
        except:
            return "颜色格式错误，请使用颜色名称（如 'red'）或RGB值（如 '1,0,0'）"

        script_content = f"""
import bpy

# 获取当前选中的对象
obj = bpy.context.active_object
if obj is None:
    print("错误：没有选中的对象")
else:
    # 创建新材质
    material = bpy.data.materials.new(name="CustomMaterial_{color}")
    material.use_nodes = True
    
    # 获取材质节点
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        # 设置基础颜色
        bsdf.inputs[0].default_value = ({r}, {g}, {b}, 1.0)
    
    # 将材质分配给对象
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
    
    print(f"已为对象 '{{obj.name}}' 添加颜色：RGB({r}, {g}, {b})")
        """.strip()

        save_path = os.path.join(os.getcwd(), "generated_material.py")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return f"材质脚本已生成，颜色：RGB({r}, {g}, {b})，保存在：{save_path}"

    async def _arun(self, color: str) -> str:
        return self._run(color)

# 定义Blender场景清理工具
class BlenderCleanTool(BaseTool):
    name: str = "Blender场景清理工具"
    description: str = "清理Blender场景中的所有对象"

    def _run(self, confirm: str = "yes") -> str:
        script_content = """
import bpy

# 删除所有网格对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 删除所有材质
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

print("场景已清理完成")
        """.strip()

        save_path = os.path.join(os.getcwd(), "generated_clean.py")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return f"场景清理脚本已生成，保存在：{save_path}"

    async def _arun(self, confirm: str = "yes") -> str:
        return self._run(confirm)

def create_blender_agent(api_key):
    """创建Blender代理"""
    # 设置环境变量确保编码正确
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 初始化OpenAI模型
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=api_key,
        openai_api_base='https://api.deepseek.com',
        temperature=0
    )

    # 创建工具列表
    tools = [
        BlenderBoxTool(),
        BlenderSphereTool(), 
        BlenderCylinderTool(),
        BlenderMaterialTool(),
        BlenderCleanTool()
    ]

    # 从LangChain Hub获取预定义的结构化聊天代理提示模板
    try:
        prompt = hub.pull("hwchase17/structured-chat-agent")
    except Exception as e:
        # 如果无法从hub获取，使用备用提示模板
        from langchain.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant with access to tools. Use the available tools to help the user with their requests. Always respond in Chinese."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

    # 创建结构化聊天代理
    agent = create_structured_chat_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # 初始化对话内存
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )

    # 创建代理执行器
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True
    )
    
    return agent_executor

def blender_agent_interface(api_key, user_input):
    """Blender代理接口函数，供main.py调用"""
    try:
        # 创建代理
        agent = create_blender_agent(api_key)
        
        # 执行用户请求
        response = agent.invoke({"input": user_input})
        
        return {
            "success": True,
            "output": response['output'],
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)
        # 处理编码错误
        if 'ascii' in error_msg:
            error_msg = "处理中文字符时出现编码错误，请检查系统编码设置"
        
        return {
            "success": False,
            "output": None,
            "error": error_msg
        } 