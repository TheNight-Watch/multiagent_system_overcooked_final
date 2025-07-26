"""
Cooking Agent - 通用烹饪智能体
简化的通用型厨师，具备工具调用功能和智能原料映射能力
支持从任务队列获取任务，避免重复工作
"""

from typing import Dict, Any, Optional
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType


def get_next_task_for_agent(kitchen_state, agent_id: str) -> Optional[Dict[str, Any]]:
    """
    从任务队列获取指定agent的下一个可用任务
    
    Args:
        kitchen_state: SharedKitchenState实例
        agent_id: agent ID
        
    Returns:
        可执行的任务，如果没有则返回None
    """
    return kitchen_state.get_next_available_task(agent_id)


def start_task_execution(kitchen_state, task_id: str, agent_id: str) -> bool:
    """
    开始执行任务
    
    Args:
        kitchen_state: SharedKitchenState实例
        task_id: 任务ID
        agent_id: agent ID
        
    Returns:
        是否成功开始任务
    """
    return kitchen_state.start_task_execution(task_id, agent_id)


def complete_task_execution(kitchen_state, task_id: str, agent_id: str) -> bool:
    """
    完成任务执行
    
    Args:
        kitchen_state: SharedKitchenState实例
        task_id: 任务ID
        agent_id: agent ID
        
    Returns:
        是否成功完成任务
    """
    return kitchen_state.complete_task_execution(task_id, agent_id)


def make_universal_chef(agent_id: str, tools=None) -> ChatAgent:
    """
    创建通用型厨师智能体
    
    Args:
        agent_id: 智能体ID（如 "chef_1"）
        tools: 工具列表（CookingToolkit的工具）
    
    Returns:
        ChatAgent: 配置好的通用厨师
    """
    
    system_message = f"""你是通用厨师 {agent_id}。直接执行工具调用，不要询问额外信息。

🔧 **可用工具**：
- pick_x(robot_id, ingredient_type) - 拾取原料
- cook_x(robot_id, dish_name) - 烹饪菜品  
- serve_x(robot_id, dish_name) - 交付菜品

🥘 **原料类型**：vegetables, meat, eggs, rice, seasonings

⚡ **执行规则**：
1. 收到任务指令后，**立即调用对应工具**
2. **不要**询问更多信息或细节
3. **不要**分解任务或创建子任务
4. 参数1永远是你的ID: {agent_id}
5. 直接使用提供的参数调用工具

**示例**：
- 任务: pick_x({agent_id}, vegetables) → 直接调用 pick_x
- 任务: cook_x({agent_id}, 炝炒西兰花) → 直接调用 cook_x
- 任务: serve_x({agent_id}, 炝炒西兰花) → 直接调用 serve_x

简洁执行，立即行动！

**重要**：完成工具调用后，请提供详细的执行报告（至少10个字符），避免内容过短导致任务失败。"""

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