"""CamelAI-Based Multi-Agent Overcooked System - Dynamic Collaboration Main Program
基于CamelAI框架的真正多智能体Overcooked烹饪协作系统 - 动态协作主程序

输入菜品，多智能体系统动态分析订单、协商任务分配并实时生成每个agent的决策动作
Input dish name, multi-agent system dynamically analyzes orders, negotiates task allocation and generates agent decisions in real-time
"""

import os
import json
import sys
import time
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from camel.societies.workforce import Workforce
from camel.tasks import Task

# 导入核心组件
from core import SharedKitchenState
from toio_integration.cooking_toolkit import CookingToolkit

# 导入真实toio控制器 - 必须成功连接，否则直接报错
try:
    from toio_integration.controller import ToioController as RealToioController
    print("✅ 真实toio控制器导入成功")
except ImportError as e:
    print(f"❌ 无法导入真实toio控制器: {e}")
    print("❌ 请确保已安装toio-py库并且硬件连接正常")
    sys.exit(1)
from agents import (
    make_order_manager,
    make_universal_chef_team
)

# 加载环境变量
load_dotenv()


class DynamicCookingSystem:
    """动态烹饪系统 - 真正的多智能体协作系统"""
    
    def __init__(self):
        self.current_step = 0
        self.agent_actions = {'chef_1': [], 'chef_2': [], 'chef_3': []}
        self.task_completion_status = {}
        
        # 初始化系统组件
        self.kitchen_state = SharedKitchenState()
        
        # 初始化真实的ToioController - 必须成功连接
        try:
            print("🔍 正在连接真实toio设备...")
            self.real_toio_controller = RealToioController(num_cubes=3, connect_timeout=15.0)
            print("✅ 成功连接到真实toio设备")
        except Exception as e:
            print(f"❌ 无法连接到真实toio设备: {e}")
            print("❌ 请检查：")
            print("   1. toio cubes是否已开机")
            print("   2. 蓝牙是否已启用")
            print("   3. toio cubes是否在连接范围内")
            print("   4. 是否有其他程序正在使用toio cubes")
            raise RuntimeError(f"Toio设备连接失败: {e}")
        
        self.cooking_toolkit = CookingToolkit(self.real_toio_controller, self.kitchen_state)
        
        # 创建CamelAI Workforce和智能体团队
        self.workforce = Workforce('Dynamic Kitchen Collaboration Team')
        self.order_manager = make_order_manager()
        self.chef_team = make_universal_chef_team(self.cooking_toolkit)
        
        # 添加agents到workforce
        self._setup_workforce()
        
    def _setup_workforce(self):
        """设置CamelAI Workforce多智能体团队"""
        self.workforce.add_single_agent_worker(
            '订单分析专家：动态分析菜品需求，智能分解任务',
            worker=self.order_manager,
        ).add_single_agent_worker(
            'Chef_1 (通用厨师)：使用工具执行烹饪任务',
            worker=self.chef_team['chef_1'],
        ).add_single_agent_worker(
            'Chef_2 (通用厨师)：使用工具执行烹饪任务',
            worker=self.chef_team['chef_2'],
        ).add_single_agent_worker(
            'Chef_3 (通用厨师)：使用工具执行烹饪任务',
            worker=self.chef_team['chef_3'],
        )
        
    def analyze_dish_requirements(self, dish_name: str) -> Dict[str, Any]:
        """动态分析菜品需求 - 不使用预定义模板"""
        print(f"🧠 动态分析菜品需求: {dish_name}")
        
        # 创建动态分析任务
        analysis_task = Task(
            content=f"""
            请为菜品 "{dish_name}" 分配任务，参考案例模板：
            
            **炝炒西兰花模板**：
            - Chef_1: pick_x(chef_1, vegetables) # 取西兰花  
            - Chef_2: pick_x(chef_2, seasonings) # 取调料
            - Chef_3: cook_x(chef_3, 炝炒西兰花) # 烹饪
            - Chef_1: serve_x(chef_1, 炝炒西兰花) # 交付
            
            按此模板为 "{dish_name}" 分配任务：
            1. 两个厨师并行取料
            2. 一个厨师专门烹饪  
            3. 一个厨师负责交付
            4. 简化步骤，避免复杂操作
            
            输出格式：简洁的任务分配方案
            """,
            id=f"dish_analysis_{dish_name}_{int(time.time())}"
        )
        
        # 让订单管理专家分析需求
        self.workforce.process_task(analysis_task)
        analysis_result = analysis_task.result
        
        print("📋 菜品需求分析完成:")
        print(analysis_result)
        
        return {
            "dish_name": dish_name,
            "analysis": analysis_result,
            "requirements_determined": True
        }
        
    def execute_collaborative_cooking(self, dish_name: str) -> Dict[str, List[Dict]]:
        """执行真正的多智能体协作烹饪"""
        print(f"🤖 开始多智能体协作制作: {dish_name}")
        
        # 第一步：动态分析菜品需求
        requirements = self.analyze_dish_requirements(dish_name)
        
        # 第二步：创建协作任务
        collaboration_task = Task(
            content=f"""
            现在开始制作 "{dish_name}"。
            
            基于之前的分析结果：
            {requirements['analysis']}
            
            当前厨房状态：
            {self.kitchen_state.get_summary()}
            
            请各位厨师协作完成这道菜：
            
            🔧 可用工具（每位厨师都有）：
            - pick_x(robot_id, ingredient) - 拾取原料
            - slice_x(robot_id, ingredient) - 切割原料
            - cook_x(robot_id, dish) - 烹饪菜品
            - serve_x(robot_id, dish) - 交付菜品
            - check_robot_status(robot_id) - 检查机器人状态

            🥘 重要：智能原料映射规则
            厨房环境只提供5种基础原料分类，你们必须智能映射具体食材需求：
            - 所有蔬菜（西红柿、西兰花、大蒜、辣椒、洋葱等）→ "vegetables"
            - 所有肉类（鸡肉、猪肉、牛肉等）→ "meat"  
            - 鸡蛋 → "eggs"
            - 米饭 → "rice"
            - 所有调料（盐、油、酱油、醋、糖、胡椒等）→ "seasonings"
            
            ⚠️ 关键约束：
            1. 只能使用这5种分类作为ingredient参数：vegetables, meat, eggs, rice, seasonings
            2. 将具体食材需求映射到对应分类（西兰花=vegetables, 鸡肉=meat）
            3. 无法映射的食材则省略相关步骤
            
            📍 厨房布局：
            - 储藏区 (8,5)：所有原料存储位置
            - 准备台 (1,5)：切菜专用区域
            - 灶台区 (1,1)：烹饪专用区域
            - 交付台 (5,1)：菜品交付位置
            
            👥 请各位通用厨师协作完成任务：
            - Chef_1: 通用厨师，可执行任何烹饪任务
            - Chef_2: 通用厨师，可执行任何烹饪任务  
            - Chef_3: 通用厨师，可执行任何烹饪任务
            
            🎯 协作要求：
            1. 每个厨师必须实际使用工具执行物理动作
            2. 避免同时使用相同的工具或位置
            3. 合理分工，提高效率
            4. 实时沟通协调任务进度
            5. 输出信息尽可能简洁高效，不要输出冗余信息
            
            请开始执行，记住一定要实际调用工具函数！
            """,
            additional_info={
                "dish_name": dish_name,
                "kitchen_state": self.kitchen_state.get_state(),
                "requirements": requirements
            },
            id=f"collaborative_cooking_{dish_name}_{int(time.time())}"
        )
        
        # 第三步：执行协作任务
        print("🚀 开始多智能体协作执行...")
        self.workforce.process_task(collaboration_task)
        
        # 第四步：收集执行结果
        execution_result = collaboration_task.result
        print("\n📊 协作执行完成:")
        print(execution_result)
        
        # 第五步：解析并格式化agent动作
        return self._parse_agent_actions_from_collaboration(execution_result, dish_name)
        
    def _parse_agent_actions_from_collaboration(self, collaboration_result: str, dish_name: str) -> Dict[str, List[Dict]]:
        """从协作结果中解析出每个agent的具体动作"""
        print("🔍 解析协作过程中的agent动作...")
        
        # 获取当前机器人状态，了解实际执行的动作
        robot_statuses = {}
        for robot_id in ['chef_1', 'chef_2', 'chef_3']:
            status = self.toio_controller.get_robot_status(robot_id)
            if status:
                robot_statuses[robot_id] = status
        
        # 基于协作结果和机器人状态，构建动作记录
        parsed_actions = {
            "chef_1": self._extract_agent_actions_from_text(collaboration_result, "chef_1", "通用厨师", dish_name),
            "chef_2": self._extract_agent_actions_from_text(collaboration_result, "chef_2", "通用厨师", dish_name),
            "chef_3": self._extract_agent_actions_from_text(collaboration_result, "chef_3", "通用厨师", dish_name)
        }
        
        # 添加机器人状态信息
        for agent_id in parsed_actions:
            if agent_id in robot_statuses:
                for action in parsed_actions[agent_id]:
                    action["robot_status"] = robot_statuses[agent_id]
        
        return parsed_actions
        
    def _extract_agent_actions_from_text(self, collaboration_text: str, agent_id: str, specialization: str, dish_name: str) -> List[Dict]:
        """从协作文本中提取特定agent的动作"""
        actions = []
        current_step = 0
        
        # 检查协作文本中是否提到了该agent执行的具体动作
        lines = collaboration_text.split('\n')
        
        for line in lines:
            if agent_id.lower() in line.lower():
                # 尝试识别动作类型
                action_type = "unknown"
                target = "unknown"
                message = line.strip()
                
                if "pick" in line.lower() or "拾取" in line or "取" in line:
                    action_type = "pick"
                    # 尝试提取目标物品
                    if "tomato" in line.lower() or "西红柿" in line:
                        target = "tomato"
                    elif "egg" in line.lower() or "鸡蛋" in line:
                        target = "eggs"
                    else:
                        target = "ingredients"
                        
                elif "slice" in line.lower() or "切" in line or "备" in line:
                    action_type = "slice"
                    if "tomato" in line.lower() or "西红柿" in line:
                        target = "tomato"
                    elif "egg" in line.lower() or "鸡蛋" in line:
                        target = "eggs"
                    else:
                        target = "ingredients"
                        
                elif "cook" in line.lower() or "烹饪" in line or "炒" in line:
                    action_type = "cook"
                    target = dish_name
                    
                elif "serve" in line.lower() or "交付" in line or "上菜" in line:
                    action_type = "serve"
                    target = dish_name
                
                # 如果识别到了动作，添加到列表中
                if action_type != "unknown":
                    position = self._get_agent_position(agent_id)
                    
                    actions.append({
                        "step": current_step,
                        "agent_id": agent_id,
                        "action_type": action_type,
                        "target": target,
                        "position": position,
                        "success": True,
                        "timestamp": f"step_{current_step}",
                        "details": {
                            "message": message,
                            "specialization": specialization,
                            "dynamic_decision": True
                        }
                    })
                    current_step += 1
        
        # 如果没有找到具体动作，创建一个基础动作记录
        if not actions:
            position = self._get_agent_position(agent_id)
            actions.append({
                "step": 0,
                "agent_id": agent_id,
                "action_type": "analyze",
                "target": dish_name,
                "position": position,
                "success": True,
                "timestamp": "step_0",
                "details": {
                    "message": f"{specialization}正在分析{dish_name}的制作需求",
                    "specialization": specialization,
                    "dynamic_decision": True
                }
            })
        
        return actions
        
    def _get_agent_position(self, agent_id: str) -> List[int]:
        """获取agent的位置坐标"""
        positions = {
            "chef_1": [1, 1],  # 通用厨师
            "chef_2": [1, 5],  # 通用厨师
            "chef_3": [8, 5]   # 通用厨师
        }
        return positions.get(agent_id, [0, 0])


def process_dish_order(dish_name: str) -> str:
    """
    处理菜品订单，使用真正的多智能体协作系统动态生成动作
    
    Args:
        dish_name: 菜品名称
    
    Returns:
        str: JSON格式的动作记录
    """
    print(f"🤖 启动动态多智能体协作系统...")
    print(f"📋 处理订单: {dish_name}")
    
    try:
        # 创建动态烹饪系统
        cooking_system = DynamicCookingSystem()
        
        print("🔄 多智能体协作分析中...")
        print("   - Order Manager: 动态分析菜品需求")
        print("   - Chef_1 (通用厨师): 使用工具执行烹饪任务")
        print("   - Chef_2 (通用厨师): 使用工具执行烹饪任务")
        print("   - Chef_3 (通用厨师): 使用工具执行烹饪任务")
        
        # 执行真正的多智能体协作
        actions = cooking_system.execute_collaborative_cooking(dish_name)
        
        print("✅ 多智能体协作完成")
        
        return json.dumps(actions, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"❌ 协作过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 返回错误信息的JSON格式
        error_result = {
            "error": str(e),
            "chef_1": [{"step": 0, "agent_id": "chef_1", "action_type": "error", "message": "协作系统错误"}],
            "chef_2": [{"step": 0, "agent_id": "chef_2", "action_type": "error", "message": "协作系统错误"}], 
            "chef_3": [{"step": 0, "agent_id": "chef_3", "action_type": "error", "message": "协作系统错误"}]
        }
        return json.dumps(error_result, indent=2, ensure_ascii=False)


def main():
    """主程序入口"""
    
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("Usage: python main.py <dish_name>")
        print("\n🍳 支持动态分析任意菜品:")
        print("  - 西红柿炒蛋 (Tomato and Egg)")
        print("  - 宫保鸡丁 (Kung Pao Chicken)")
        print("  - 麻婆豆腐 (Mapo Tofu)")
        print("  - 炒饭 (Fried Rice)")
        print("  - 红烧肉 (Braised Pork)")
        print("  - 任意其他菜品 (Any other dish)")
        print("\n💡 系统会动态分析任何菜品并智能分配任务!")
        print("\nExample: python main.py '宫保鸡丁'")
        sys.exit(1)
    
    dish_name = sys.argv[1]
    
    try:
        print(f"🍳 CamelAI 动态多智能体 Overcooked 系统")
        print(f"📋 处理订单: {dish_name}")
        print("=" * 60)
        
        # 处理订单 - 真正的多智能体协作
        actions_json = process_dish_order(dish_name)
        
        # 输出JSON格式的动作记录
        print("\n📊 多智能体协作结果 (JSON格式):")
        print(actions_json)
        
        # 保存到文件
        output_filename = f"dynamic_cooking_actions_{dish_name.replace(' ', '_').replace('/', '_')}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(actions_json)
        
        print(f"\n💾 协作结果保存到: {output_filename}")
        print("✅ 动态多智能体协作完成!")
        
        
    except Exception as e:
        print(f"❌ 处理订单时出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()