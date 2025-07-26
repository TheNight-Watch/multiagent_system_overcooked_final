"""
Order Manager Agent - 简化订单管理智能体
负责将订单分解为具体任务，只使用现有原料和工具
支持生成带依赖关系的任务队列，解决任务重复问题
"""

from typing import List, Dict, Any
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType


def generate_cooking_tasks(dish_name: str) -> List[Dict[str, Any]]:
    """
    生成带依赖关系的烹饪任务列表
    
    Args:
        dish_name: 菜品名称
        
    Returns:
        包含依赖关系的任务列表
    """
    tasks = []
    
    # 根据菜品类型生成任务
    if "西红柿炒蛋" in dish_name or "tomato" in dish_name.lower():
        tasks = [
            {
                "type": "pick_x",
                "params": ["chef_1", "vegetables"],
                "dependencies": []
            },
            {
                "type": "pick_x", 
                "params": ["chef_2", "eggs"],
                "dependencies": []
            },
            {
                "type": "cook_x",
                "params": ["chef_3", dish_name],
                "dependencies": ["task_1_pick_x", "task_2_pick_x"]
            },
            {
                "type": "serve_x",
                "params": ["chef_1", dish_name],
                "dependencies": ["task_3_cook_x"]
            }
        ]
    elif "宫保鸡丁" in dish_name or "kung pao" in dish_name.lower():
        tasks = [
            {
                "type": "pick_x",
                "params": ["chef_1", "meat"],
                "dependencies": []
            },
            {
                "type": "pick_x",
                "params": ["chef_2", "vegetables"],
                "dependencies": []
            },
            {
                "type": "pick_x",
                "params": ["chef_3", "seasonings"],
                "dependencies": []
            },
            {
                "type": "cook_x",
                "params": ["chef_1", dish_name],
                "dependencies": ["task_1_pick_x", "task_2_pick_x", "task_3_pick_x"]
            },
            {
                "type": "serve_x",
                "params": ["chef_2", dish_name],
                "dependencies": ["task_4_cook_x"]
            }
        ]
    elif "炝炒西兰花" in dish_name or "broccoli" in dish_name.lower():
        tasks = [
            {
                "type": "pick_x",
                "params": ["chef_1", "vegetables"],
                "dependencies": []
            },
            {
                "type": "pick_x",
                "params": ["chef_2", "seasonings"],
                "dependencies": []
            },
            {
                "type": "cook_x",
                "params": ["chef_3", dish_name],
                "dependencies": ["task_1_pick_x", "task_2_pick_x"]
            },
            {
                "type": "serve_x",
                "params": ["chef_1", dish_name],
                "dependencies": ["task_3_cook_x"]
            }
        ]
    else:
        # 通用菜品模板
        tasks = [
            {
                "type": "pick_x",
                "params": ["chef_1", "meat"],
                "dependencies": []
            },
            {
                "type": "pick_x",
                "params": ["chef_2", "vegetables"],
                "dependencies": []
            },
            {
                "type": "pick_x",
                "params": ["chef_3", "seasonings"],
                "dependencies": []
            },
            {
                "type": "cook_x",
                "params": ["chef_1", dish_name],
                "dependencies": ["task_1_pick_x", "task_2_pick_x", "task_3_pick_x"]
            },
            {
                "type": "serve_x",
                "params": ["chef_2", dish_name],
                "dependencies": ["task_4_cook_x"]
            }
        ]
    
    return tasks


def make_order_manager() -> ChatAgent:
    """
    创建简化的订单管理智能体
    
    Returns:
        ChatAgent: 配置好的订单管理智能体
    """
    
    system_message = """你是订单管理专家，负责分析菜品需求并生成任务队列。

🔧 可用工具：pick_x, cook_x, serve_x
🥘 可用原料：vegetables, meat, eggs, rice, seasonings
👥 三位厨师：chef_1, chef_2, chef_3

📋 **任务队列系统**：
现在使用任务队列系统避免重复工作。系统会自动生成带依赖关系的任务列表，确保：
1. 每个任务只执行一次
2. 按正确顺序执行（依赖关系）
3. 避免多个chef重复取同样的原料

**分析要求**：
1. 识别菜品所需的原料类型
2. 确定合理的制作步骤顺序
3. 分配给合适的厨师
4. 输出简洁的任务分析

输出格式：简洁描述菜品制作要求和厨师分工。"""
    
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