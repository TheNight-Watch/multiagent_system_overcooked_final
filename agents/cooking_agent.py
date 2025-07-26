"""
Cooking Agent - 通用烹饪智能体
简化的通用型厨师，具备工具调用功能和智能原料映射能力
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType


def make_universal_chef(agent_id: str, tools=None) -> ChatAgent:
    """
    创建通用型厨师智能体
    
    Args:
        agent_id: 智能体ID（如 "chef_1"）
        tools: 工具列表（CookingToolkit的工具）
    
    Returns:
        ChatAgent: 配置好的通用厨师
    """
    
    system_message = f"""你是通用厨师 {agent_id}。使用工具完成烹饪任务。

工具：pick_x, slice_x, cook_x, serve_x, get_kitchen_layout, check_robot_status, set_robot_light, get_connection_status
原料只能用：vegetables, meat, eggs, rice, seasonings
具体食材映射到这5类，无法映射则省略。

地图坐标 (toio真实坐标):
- 储藏区: (229,70) (270,70) - pick_x操作
- 切菜区: (147,70) - slice_x操作  
- 烹饪区: (188,274) - cook_x操作
- 交付区: (352,70) - serve_x操作

🤖 Toio机器人控制:
- 可用颜色: red, green, blue, yellow, purple, cyan, white, off
- set_robot_light 设置工作状态指示
- 支持真实硬件和仿真模式

第一个参数永远是 "{agent_id}"。

重要：输出信息尽可能简洁高效，不要输出冗余信息。"""

    sys_msg = BaseMessage.make_assistant_message(
        role_name=f"Universal Chef {agent_id}",
        content=system_message,
    )
    
    model = ModelFactory.create(
        model_platform=ModelPlatformType.DEFAULT,
        model_type=ModelType.DEFAULT,
    )
    
    agent = ChatAgent(
        system_message=sys_msg,
        model=model,
        tools=tools or []  # 传入工具列表
    )
    
    agent.agent_id = agent_id
    return agent


def make_universal_chef_team(cooking_toolkit):
    """
    创建通用厨师团队
    
    Args:
        cooking_toolkit: CookingToolkit实例
    
    Returns:
        dict: 包含三名通用厨师
    """
    tools = cooking_toolkit.get_tools() if cooking_toolkit else []
    
    team = {
        'chef_1': make_universal_chef("chef_1", tools),
        'chef_2': make_universal_chef("chef_2", tools),
        'chef_3': make_universal_chef("chef_3", tools)
    }
    
    return team