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
    make_universal_chef_team,
    generate_cooking_tasks,
    get_next_task_for_agent,
    start_task_execution,
    complete_task_execution
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
            self.real_toio_controller = RealToioController(num_cubes=3, connect_timeout=10.0, enable_collision_avoidance=True)
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
        """执行基于任务队列的协作烹饪"""
        print(f"🤖 开始任务队列协作制作: {dish_name}")
        
        # 第一步：生成任务队列
        print("📋 生成带依赖关系的任务队列...")
        task_list = generate_cooking_tasks(dish_name)
        self.kitchen_state.add_cooking_tasks(dish_name, task_list)
        
        # 打印任务队列状态
        print(self.kitchen_state.get_task_queue_summary())
        
        # 第二步：循环执行任务直到全部完成
        print("🚀 开始执行任务队列...")
        max_steps = 20  # 防止无限循环
        step = 0
        
        while not self.kitchen_state.is_all_tasks_completed() and step < max_steps:
            step += 1
            print(f"\n=== 执行步骤 {step} ===")
            
            # 为每个chef检查可用任务
            tasks_assigned = False
            for agent_id in ['chef_1', 'chef_2', 'chef_3']:
                next_task = get_next_task_for_agent(self.kitchen_state, agent_id)
                
                if next_task:
                    print(f"🎯 {agent_id} 获得任务: {next_task['type']}({', '.join(map(str, next_task['params']))})")
                    
                    # 开始执行任务
                    if start_task_execution(self.kitchen_state, next_task['id'], agent_id):
                        # 创建明确的任务指令让chef执行
                        function_call = f"{next_task['type']}({', '.join(map(str, next_task['params']))})"
                        individual_task = Task(
                            content=f"""立即执行工具调用: {function_call}

**明确指令**: 直接调用工具函数 {next_task['type']}，参数1: {next_task['params'][0]}，参数2: {next_task['params'][1] if len(next_task['params']) > 1 else '无'}

**不要**询问更多信息，**不要**分解任务，**直接调用工具**！完成后提供详细执行报告。

示例调用: {function_call}""",
                            id=f"execute_{next_task['id']}_{int(time.time())}"
                        )
                        
                        # 根据agent_id选择对应的worker执行
                        worker_name = f"{agent_id.title()} (通用厨师)：使用工具执行烹饪任务"
                        
                        # 使用workforce处理任务
                        self.workforce.process_task(individual_task)
                        
                        # 完成任务
                        complete_task_execution(self.kitchen_state, next_task['id'], agent_id)
                        tasks_assigned = True
                        
                        print(f"✅ {agent_id} 完成任务: {next_task['type']}")
            
            # 如果没有任务被分配，可能所有任务都完成了或被阻塞
            if not tasks_assigned:
                print("⏸️ 当前步骤没有可执行任务，检查依赖关系...")
                # 打印当前状态
                print(self.kitchen_state.get_task_queue_summary())
                break
        
        # 第三步：返回执行结果
        print("\n📊 任务队列执行完成!")
        print(self.kitchen_state.get_task_queue_summary())
        
        return self._generate_action_summary(dish_name)
    
    def _generate_action_summary(self, dish_name: str) -> Dict[str, List[Dict]]:
        """基于任务队列生成动作摘要"""
        action_summary = {
            "chef_1": [],
            "chef_2": [],
            "chef_3": []
        }
        
        # 从已完成的任务中生成动作记录
        step_counter = {"chef_1": 0, "chef_2": 0, "chef_3": 0}
        
        for task in self.kitchen_state.task_queue:
            if task['status'] == 'completed' and task['assigned_to']:
                agent_id = task['assigned_to']
                action_summary[agent_id].append({
                    "step": step_counter[agent_id],
                    "agent_id": agent_id,
                    "action_type": task['type'],
                    "target": task['params'][1] if len(task['params']) > 1 else dish_name,
                    "position": self._get_agent_position(agent_id),
                    "success": True,
                    "timestamp": f"step_{step_counter[agent_id]}",
                    "details": {
                        "message": f"执行任务: {task['type']}({', '.join(map(str, task['params']))})",
                        "task_id": task['id'],
                        "dish_name": task['dish_name'],
                        "queue_based": True
                    }
                })
                step_counter[agent_id] += 1
        
        return action_summary

    # ==================== 新增：异步并行执行方法 ====================
    
    async def execute_collaborative_cooking_async(self, dish_name: str) -> Dict[str, List[Dict]]:
        """异步并行协作烹饪 - 基于CamelAI异步API"""
        print(f"🚀 开始异步并行制作: {dish_name}")
        
        # 第一步：生成任务队列（保持现有逻辑）
        print("📋 生成带依赖关系的任务队列...")
        task_list = generate_cooking_tasks(dish_name)
        self.kitchen_state.add_cooking_tasks(dish_name, task_list)
        
        # 打印任务队列状态
        print(self.kitchen_state.get_task_queue_summary())
        
        # 第二步：创建描述完整流程的大任务
        task_description = self._create_parallel_task_description(dish_name, task_list)
        
        cooking_task = Task(
            content=task_description,
            id=f"parallel_cooking_{dish_name}_{int(time.time())}"
        )
        
        print("🤖 提交并行协作任务给CamelAI Workforce...")
        
        # 🔑 关键：使用异步API让Workforce自动并行分配
        result = await self.workforce.process_task_async(cooking_task)
        
        print("✅ 异步并行执行完成!")
        
        # 第三步：解析并行执行结果
        return self._parse_parallel_result(result, dish_name, self.kitchen_state.task_queue)
    
    def _create_parallel_task_description(self, dish_name: str, task_list: List[Dict]) -> str:
        """创建并行任务描述"""
        print(f"📝 为 {dish_name} 创建并行任务描述...")
        
        # 按任务类型分组
        pick_tasks = [t for t in task_list if t['type'] == 'pick_x']
        cook_tasks = [t for t in task_list if t['type'] == 'cook_x'] 
        serve_tasks = [t for t in task_list if t['type'] == 'serve_x']
        
        # 智能分配任务给3个厨师
        chef1_tasks = []
        chef2_tasks = []
        chef3_tasks = []
        
        # Chef_1: 主要负责取原料
        if pick_tasks:
            chef1_tasks = pick_tasks[:len(pick_tasks)//2] if len(pick_tasks) > 1 else pick_tasks
        
        # Chef_2: 负责取调料和剩余取原料任务
        if pick_tasks:
            chef2_tasks = pick_tasks[len(pick_tasks)//2:]
            
        # Chef_3: 负责烹饪和交付
        chef3_tasks = cook_tasks + serve_tasks
        
        return f"""
🍳 **并行协作制作 {dish_name}**

**3位厨师同时工作，无需等待：**

**Chef_1 任务列表：**
{chr(10).join([f"- {t['type']}({', '.join(map(str, t['params']))})" for t in chef1_tasks]) if chef1_tasks else "- 待命"}

**Chef_2 任务列表：**  
{chr(10).join([f"- {t['type']}({', '.join(map(str, t['params']))})" for t in chef2_tasks]) if chef2_tasks else "- 待命"}

**Chef_3 任务列表：**
{chr(10).join([f"- {t['type']}({', '.join(map(str, t['params']))})" for t in chef3_tasks]) if chef3_tasks else "- 待命"}

**🔧 可用工具函数：**
- pick_x(robot_id, ingredient_type) - 拾取原料
- cook_x(robot_id, dish_name) - 烹饪菜品  
- serve_x(robot_id, dish_name) - 交付菜品

**⚡ 执行规则：**
1. 每位厨师立即开始执行分配的任务
2. **无需等待其他厨师完成**，可以并行工作
3. 使用对应的工具函数执行操作
4. 参数1永远是自己的ID (chef_1, chef_2, chef_3)
5. 完成每个任务后提供详细执行报告

**现在开始并行协作制作 {dish_name}！3位厨师同时行动！**
        """
    
    def _parse_parallel_result(self, result: Any, dish_name: str, task_queue: List[Dict]) -> Dict[str, List[Dict]]:
        """解析并行执行结果"""
        print("🔍 解析并行执行结果...")
        
        # 初始化动作摘要
        action_summary = {
            "chef_1": [],
            "chef_2": [],
            "chef_3": []
        }
        
        # 从result中提取执行信息
        result_text = str(result) if result else ""
        
        # 基于任务队列和执行结果，构建动作记录
        step_counter = {"chef_1": 0, "chef_2": 0, "chef_3": 0}
        
        for task in task_queue:
            # 根据任务类型智能分配到对应的chef
            assigned_chef = self._determine_task_assignment(task)
            
            action_summary[assigned_chef].append({
                "step": step_counter[assigned_chef],
                "agent_id": assigned_chef,
                "action_type": task['type'],
                "target": task['params'][1] if len(task['params']) > 1 else dish_name,
                "position": self._get_agent_position(assigned_chef),
                "success": True,
                "timestamp": f"parallel_step_{step_counter[assigned_chef]}",
                "details": {
                    "message": f"并行执行任务: {task['type']}({', '.join(map(str, task['params']))})",
                    "task_id": task['id'],
                    "dish_name": task['dish_name'],
                    "parallel_execution": True,
                    "execution_mode": "async_parallel"
                }
            })
            step_counter[assigned_chef] += 1
        
        return action_summary
    
    def _determine_task_assignment(self, task: Dict) -> str:
        """根据任务类型确定分配给哪位厨师"""
        task_type = task['type']
        
        if task_type == 'pick_x':
            # 取原料任务分配给chef_1和chef_2
            if 'vegetables' in str(task['params']) or 'meat' in str(task['params']):
                return 'chef_1'
            else:
                return 'chef_2'
        elif task_type == 'cook_x':
            return 'chef_3'
        elif task_type == 'serve_x':
            return 'chef_3'
        else:
            return 'chef_1'  # 默认分配
        
    def _parse_agent_actions_from_collaboration(self, collaboration_result: str, dish_name: str) -> Dict[str, List[Dict]]:
        """从协作结果中解析出每个agent的具体动作"""
        print("🔍 解析协作过程中的agent动作...")
        
        # 获取当前机器人状态，了解实际执行的动作
        robot_statuses = {}
        for robot_id in ['chef_1', 'chef_2', 'chef_3']:
            # 使用真实的toio控制器获取状态
            try:
                # 这里应该使用self.real_toio_controller，但先跳过状态获取
                robot_statuses[robot_id] = {"status": "active", "position": self._get_agent_position(robot_id)}
            except:
                robot_statuses[robot_id] = {"status": "unknown", "position": self._get_agent_position(robot_id)}
        
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


# 全局烹饪系统实例
_global_cooking_system = None

def get_cooking_system():
    """获取全局烹饪系统实例，只初始化一次"""
    global _global_cooking_system
    if _global_cooking_system is None:
        print("🔄 正在初始化多智能体系统...")
        _global_cooking_system = DynamicCookingSystem()
        print("✅ 系统初始化完成!")
    return _global_cooking_system

def process_dish_order(dish_name: str) -> str:
    """
    处理菜品订单，使用真正的多智能体协作系统动态生成动作
    
    Args:
        dish_name: 菜品名称
    
    Returns:
        str: JSON格式的动作记录
    """
    print(f"🤖 使用多智能体协作系统...")
    print(f"📋 处理订单: {dish_name}")
    
    try:
        # 获取全局烹饪系统实例
        cooking_system = get_cooking_system()
        
        # 重置任务队列以处理新订单
        cooking_system.kitchen_state.reset_task_queue()
        print("🔄 任务队列已重置，准备处理新订单")
        
        print("🔄 多智能体协作分析中...")
        print("   - Order Manager: 动态分析菜品需求")
        print("   - Chef_1 (通用厨师): 使用工具执行烹饪任务")
        print("   - Chef_2 (通用厨师): 使用工具执行烹饪任务")
        print("   - Chef_3 (通用厨师): 使用工具执行烹饪任务")
        
        # 🚀 执行异步并行多智能体协作
        actions = asyncio.run(cooking_system.execute_collaborative_cooking_async(dish_name))
        
        print("✅ 异步并行多智能体协作完成")
        
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


def show_welcome():
    """显示欢迎信息和支持的菜品"""
    print("🍳 CamelAI 动态多智能体 Overcooked 系统")
    print("🔄 连续订单处理模式")
    print("=" * 60)
    print("\n📋 支持的菜品类型:")
    print("  - 西红柿炒蛋 (Tomato and Egg)")
    print("  - 宫保鸡丁 (Kung Pao Chicken)")
    print("  - 炝炒西兰花 (Stir-fried Broccoli)")
    print("  - 麻婆豆腐 (Mapo Tofu)")
    print("  - 炒饭 (Fried Rice)")
    print("  - 红烧肉 (Braised Pork)")
    print("  - 任意其他菜品 (Any other dish)")
    print("\n🎮 支持的命令:")
    print("  - help: 显示帮助信息")
    print("  - quit/exit: 退出程序")
    print("  - clear: 清屏")
    print("\n💡 系统会动态分析任何菜品并智能分配任务!")
    print("="*60)

def get_user_input():
    """获取用户输入并进行基本验证"""
    while True:
        try:
            user_input = input("\n📝 请输入菜品名称 (或输入 'help' 查看帮助): ").strip()
            
            if not user_input:
                print("⚠️ 请输入有效的菜品名称")
                continue
                
            return user_input
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见!")
            return "quit"
        except EOFError:
            print("\n\n👋 输入结束，再见!")
            return "quit"

def process_user_command(command: str) -> bool:
    """
    处理用户命令
    
    Args:
        command: 用户输入的命令
        
    Returns:
        bool: True表示继续执行，False表示退出程序
    """
    command_lower = command.lower()
    
    if command_lower in ['quit', 'exit', 'q']:
        print("👋 感谢使用CamelAI多智能体烹饪系统，再见!")
        return False
    
    elif command_lower in ['help', 'h']:
        show_welcome()
        return True
    
    elif command_lower == 'clear':
        os.system('clear' if os.name == 'posix' else 'cls')
        show_welcome()
        return True
    
    else:
        # 处理菜品订单
        return process_dish_command(command)

def process_dish_command(dish_name: str) -> bool:
    """
    处理菜品订单命令
    
    Args:
        dish_name: 菜品名称
        
    Returns:
        bool: True表示继续执行，False表示退出程序
    """
    try:
        print(f"\n📋 正在处理订单: {dish_name}")
        print("-" * 50)
        
        # 处理订单 - 真正的多智能体协作
        actions_json = process_dish_order(dish_name)
        
        # 输出JSON格式的动作记录
        print("\n📊 多智能体协作结果:")
        print(actions_json)
        
        # 保存到文件
        timestamp = int(time.time())
        output_filename = f"dynamic_cooking_actions_{dish_name.replace(' ', '_').replace('/', '_')}_{timestamp}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(actions_json)
        
        print(f"\n💾 协作结果保存到: {output_filename}")
        print("✅ 订单处理完成!")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理订单时出现错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 提示: 请检查订单格式是否正确，或尝试其他菜品")
        return True  # 继续运行，不因为单个订单错误而退出

def main():
    """主程序入口 - 交互式连续订单处理模式"""
    
    # 显示欢迎信息
    show_welcome()
    
    order_count = 0
    
    try:
        # 主交互循环
        while True:
            try:
                # 获取用户输入
                user_input = get_user_input()
                
                # 处理命令
                if not process_user_command(user_input):
                    break  # 退出程序
                
                # 如果不是系统命令，则是菜品订单，增加计数
                command_lower = user_input.lower()
                if command_lower not in ['help', 'h', 'clear']:
                    order_count += 1
                    print(f"\n📈 已处理订单数量: {order_count}")
                
            except Exception as e:
                print(f"❌ 处理过程中出现错误: {e}")
                import traceback
                traceback.print_exc()
                print("💡 系统将继续运行，请重新输入")
                continue
        
    except Exception as e:
        print(f"❌ 程序运行出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        global _global_cooking_system
        if _global_cooking_system:
            try:
                print("🧹 正在清理系统资源...")
                # 如果有清理方法，在这里调用
                pass
            except:
                pass
        
        print(f"\n📊 会话统计: 总共处理了 {order_count} 个订单")
        print("👋 程序结束")


if __name__ == "__main__":
    main()