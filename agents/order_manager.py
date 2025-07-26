"""
Order Manager Agent - 简化订单管理智能体
负责将订单分解为具体任务，只使用现有原料和工具
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType


def make_order_manager() -> ChatAgent:
    """
    创建简化的订单管理智能体
    
    Returns:
        ChatAgent: 配置好的订单管理智能体
    """
    
    system_message = """你是订单管理专家，基于案例模板简化任务分配。

🔧 可用工具：pick_x, slice_x, cook_x, serve_x
🥘 可用原料：vegetables, meat, eggs, rice, seasonings
👥 三位厨师：chef_1, chef_2, chef_3

📋 **任务分配案例模板**：

**炝炒西兰花**：
- Chef_1: pick_x(chef_1, vegetables) # 取西兰花
- Chef_2: pick_x(chef_2, seasonings) # 取调料
- Chef_3: 等待Chef_1和Chef_2完成后，cook_x(chef_3, 炝炒西兰花) # 烹饪
- Chef_1: 在Chef_3完成烹饪后，serve_x(chef_1, 炝炒西兰花) # 交付

**西红柿炒蛋**：
- Chef_1: pick_x(chef_1, vegetables) # 取西红柿
- Chef_2: pick_x(chef_2, eggs) # 取鸡蛋
- Chef_3: 等待Chef_1和Chef_2完成后，cook_x(chef_3, 西红柿炒蛋) # 烹饪
- Chef_1: 在Chef_3完成烹饪后，serve_x(chef_1, 西红柿炒蛋) # 交付

**原则**：
1. 简化为4个基本步骤：取料→烹饪→交付
2. 两个厨师并行取料，一个厨师专门烹饪，一个厨师负责交付
3. 避免复杂的中间步骤（热锅、切菜、调味等）
4. 确保任务分配均匀，三个厨师都有事做

按照以上案例模板，为新订单分配任务。输出简洁的分工方案。"""
    
    sys_msg = BaseMessage.make_assistant_message(
        role_name="Order Manager",
        content=system_message,
    )
    
    model = ModelFactory.create(
        model_platform=ModelPlatformType.DEFAULT,
        model_type=ModelType.DEFAULT,
    )
    
    agent = ChatAgent(
        system_message=sys_msg,
        model=model,
    )
    
    return agent