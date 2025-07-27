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
    
    system_message = """你是订单管理专家，分解订单为烹饪任务。

约束条件：
- 原料只能用：vegetables, meat, eggs, rice, seasonings
- 工具只能用：pick_x, slice_x, cook_x, serve_x
- 将具体食材映射到5种基础分类
- 无法映射的食材则省略

简洁分析订单，提供可执行的烹饪步骤。

重要：输出信息尽可能简洁高效，不要输出冗余信息。"""
    
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