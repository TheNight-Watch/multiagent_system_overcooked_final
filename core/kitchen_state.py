"""
SharedKitchenState - 极简化的厨房共享状态空间

提供一个简单的共享状态，让 agents 能够查看当前环境状态来自主选择任务。
状态更新通过 toio 移动到特定位置来触发。
"""

from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime


class SharedKitchenState:
    """CamelAI Society共享的厨房状态"""
    
    def __init__(self):
        self.current_step = 0
        
        # Agent状态：位置 + 当前动作
        self.agents = {
            "chef_1": {"position": (1, 1), "action": "idle"},
            "chef_2": {"position": (1, 5), "action": "idle"}, 
            "chef_3": {"position": (8, 5), "action": "idle"}
        }
        
        # 原料状态：简单基础的原料分类
        self.ingredients = {
            "vegetables": 15,    # 包含所有蔬菜：西兰花、西红柿、大蒜、辣椒等
            "meat": 8,          # 包含所有肉类：鸡肉、猪肉、牛肉等
            "eggs": 20,         # 鸡蛋
            "rice": 50,         # 米饭
            "seasonings": 100,  # 包含所有调料：盐、油、酱油、醋、糖等
        }
        
        # 工具状态：位置 + 占用者
        self.tools = {
            "cutting_board": {"location": (1, 5), "occupied_by": None},
            "stove": {"location": (1, 1), "occupied_by": None},
            "plate_station": {"location": (3, 3), "occupied_by": None}
        }
        
        # 菜品状态：步骤列表 + 完成列表
        self.dishes = {}
        
        # 可用任务：简单描述
        self.available_tasks = []
        
        # 初始化默认的西红柿炒蛋任务
        self._initialize_default_dish()
    
    def _initialize_default_dish(self):
        """初始化默认的西红柿炒蛋制作任务"""
        self.dishes = {
            "tomato_egg_1": {
                "dish_type": "西红柿炒蛋",
                "steps": ["cut_tomato", "beat_eggs", "cook_eggs", "add_tomato", "plate"],
                "completed": []
            },
            "tomato_egg_2": {
                "dish_type": "西红柿炒蛋", 
                "steps": ["cut_tomato", "beat_eggs", "cook_eggs", "add_tomato", "plate"],
                "completed": []
            }
        }
        
        self.available_tasks = [
            {"task": "cut_tomato", "dish_id": "tomato_egg_1", "location": (1, 5), "tool": "cutting_board"},
            {"task": "beat_eggs", "dish_id": "tomato_egg_1", "location": (1, 5), "tool": "cutting_board"},
            {"task": "cut_tomato", "dish_id": "tomato_egg_2", "location": (1, 5), "tool": "cutting_board"},
            {"task": "beat_eggs", "dish_id": "tomato_egg_2", "location": (1, 5), "tool": "cutting_board"}
        ]
    
    def get_state(self) -> Dict[str, Any]:
        """agents 查看状态用"""
        return {
            "current_step": self.current_step,
            "agents": self.agents.copy(),
            "tools": self.tools.copy(), 
            "available_tasks": self.available_tasks.copy(),
            "dishes": self.dishes.copy(),
            "ingredients": self.ingredients.copy()
        }
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取特定 agent 的状态"""
        return self.agents.get(agent_id)
    
    def get_available_tasks_near(self, position: Tuple[int, int], max_distance: int = 3) -> List[Dict[str, Any]]:
        """获取指定位置附近的可用任务"""
        nearby_tasks = []
        for task in self.available_tasks:
            task_pos = task["location"]
            distance = abs(task_pos[0] - position[0]) + abs(task_pos[1] - position[1])  # 曼哈顿距离
            if distance <= max_distance:
                nearby_tasks.append(task)
        return nearby_tasks
    
    def update_agent(self, agent_id: str, position: Tuple[int, int], action: str = "idle"):
        """toio 移动触发更新"""
        if agent_id in self.agents:
            self.agents[agent_id] = {"position": position, "action": action}
            print(f"🤖 {agent_id} 移动到位置 {position}，执行动作: {action}")
        else:
            print(f"⚠️ 未知的 agent ID: {agent_id}")
    
    def assign_task(self, task_info: Dict[str, Any], agent_id: str) -> bool:
        """分配任务给 agent"""
        task_tool = task_info.get("tool")
        
        # 检查工具是否可用
        if task_tool and task_tool in self.tools:
            if self.tools[task_tool]["occupied_by"] is None:
                # 占用工具
                self.tools[task_tool]["occupied_by"] = agent_id
                # 更新 agent 状态
                self.agents[agent_id]["action"] = task_info["task"]
                # 从可用任务中移除
                if task_info in self.available_tasks:
                    self.available_tasks.remove(task_info)
                print(f"✅ 任务 '{task_info['task']}' 已分配给 {agent_id}")
                return True
            else:
                print(f"❌ 工具 {task_tool} 正被 {self.tools[task_tool]['occupied_by']} 使用")
                return False
        
        print(f"❌ 任务分配失败: {task_info}")
        return False
    
    def complete_task(self, task_name: str, dish_id: str, agent_id: str):
        """任务完成更新"""
        if dish_id in self.dishes:
            # 更新菜品完成状态
            if task_name not in self.dishes[dish_id]["completed"]:
                self.dishes[dish_id]["completed"].append(task_name)
                print(f"✅ {agent_id} 完成了 {dish_id} 的步骤: {task_name}")
            
            # 释放相关工具
            for tool_name, tool_info in self.tools.items():
                if tool_info["occupied_by"] == agent_id:
                    tool_info["occupied_by"] = None
                    print(f"🔓 释放工具: {tool_name}")
            
            # 更新 agent 状态为空闲
            if agent_id in self.agents:
                self.agents[agent_id]["action"] = "idle"
            
            # 检查是否有新任务可用
            self._update_available_tasks()
            
            # 推进步骤
            self.current_step += 1
        else:
            print(f"❌ 未找到菜品: {dish_id}")
    
    def _update_available_tasks(self):
        """根据当前状态更新可用任务列表"""
        new_tasks = []
        
        for dish_id, dish_info in self.dishes.items():
            completed_steps = dish_info["completed"]
            all_steps = dish_info["steps"]
            
            # 找到下一个可执行的步骤
            for step in all_steps:
                if step not in completed_steps:
                    # 检查前置条件是否满足
                    step_index = all_steps.index(step)
                    if step_index == 0 or all_steps[step_index - 1] in completed_steps:
                        # 创建任务
                        task = self._create_task_from_step(step, dish_id)
                        if task and task not in new_tasks:
                            new_tasks.append(task)
                    break  # 每个菜品只添加下一个可执行步骤
        
        self.available_tasks = new_tasks
    
    def _create_task_from_step(self, step: str, dish_id: str) -> Optional[Dict[str, Any]]:
        """根据步骤名称创建任务"""
        task_mapping = {
            "cut_tomato": {"task": "cut_tomato", "location": (1, 5), "tool": "cutting_board"},
            "beat_eggs": {"task": "beat_eggs", "location": (1, 5), "tool": "cutting_board"},
            "cook_eggs": {"task": "cook_eggs", "location": (1, 1), "tool": "stove"},
            "add_tomato": {"task": "add_tomato", "location": (1, 1), "tool": "stove"},
            "plate": {"task": "plate", "location": (3, 3), "tool": "plate_station"}
        }
        
        if step in task_mapping:
            task = task_mapping[step].copy()
            task["dish_id"] = dish_id
            return task
        return None
    
    def get_summary(self) -> str:
        """获取状态摘要"""
        summary = f"📊 厨房状态摘要 (步骤 {self.current_step}):\n"
        
        # Agent 状态
        summary += "\n🤖 Chef 状态:\n"
        for agent_id, info in self.agents.items():
            summary += f"  {agent_id}: 位置 {info['position']}, 动作 {info['action']}\n"
        
        # 工具状态  
        summary += "\n🔧 工具状态:\n"
        for tool_name, info in self.tools.items():
            occupier = info['occupied_by'] or "空闲"
            summary += f"  {tool_name}: 位置 {info['location']}, 使用者 {occupier}\n"
        
        # 菜品进度
        summary += "\n🍳 菜品进度:\n"
        for dish_id, info in self.dishes.items():
            completed = len(info['completed'])
            total = len(info['steps'])
            summary += f"  {dish_id}: {completed}/{total} 步骤完成\n"
        
        # 可用任务
        summary += f"\n📋 可用任务: {len(self.available_tasks)} 个\n"
        for task in self.available_tasks:
            summary += f"  - {task['task']} (位置 {task['location']})\n"
        
        return summary
    
    def to_json(self) -> str:
        """导出状态为 JSON"""
        return json.dumps(self.get_state(), indent=2, ensure_ascii=False)
    
    def save_state(self, filepath: str):
        """保存状态到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        print(f"💾 状态已保存到: {filepath}")
    
    # ==================== TOIO 集成接口 ====================
    
    def register_toio_position_callback(self, agent_id: str, target_position: Tuple[int, int], 
                                       task_info: Dict[str, Any], callback_func=None):
        """
        注册 toio 位置回调，当 toio 到达目标位置时触发任务完成
        
        Args:
            agent_id: agent 标识
            target_position: 目标位置坐标
            task_info: 任务信息
            callback_func: 可选的自定义回调函数
        """
        if not hasattr(self, '_toio_callbacks'):
            self._toio_callbacks = {}
        
        self._toio_callbacks[agent_id] = {
            'target_position': target_position,
            'task_info': task_info,
            'callback_func': callback_func,
            'registered_time': datetime.now()
        }
        
        print(f"🤖 注册 toio 回调: {agent_id} -> 目标位置 {target_position}")
    
    def on_toio_position_update(self, agent_id: str, current_position: Tuple[int, int]) -> bool:
        """
        处理 toio 位置更新事件，检查是否到达目标位置并触发状态更新
        
        Args:
            agent_id: agent 标识
            current_position: 当前位置坐标
            
        Returns:
            bool: 是否触发了任务完成
        """
        # 更新 agent 位置
        self.update_agent(agent_id, current_position, "moving")
        
        # 检查是否有注册的回调
        if not hasattr(self, '_toio_callbacks') or agent_id not in self._toio_callbacks:
            return False
        
        callback_info = self._toio_callbacks[agent_id]
        target_pos = callback_info['target_position']
        task_info = callback_info['task_info']
        
        # 检查是否到达目标位置（允许一定误差）
        if self._is_position_reached(current_position, target_pos, tolerance=1):
            print(f"🎯 {agent_id} 到达目标位置 {target_pos}，触发任务完成!")
            
            # 执行任务完成逻辑
            if 'task' in task_info and 'dish_id' in task_info:
                self.complete_task(task_info['task'], task_info['dish_id'], agent_id)
            
            # 执行自定义回调
            if callback_info.get('callback_func'):
                callback_info['callback_func'](agent_id, current_position, task_info)
            
            # 清除回调
            del self._toio_callbacks[agent_id]
            return True
        
        return False
    
    def _is_position_reached(self, current: Tuple[int, int], target: Tuple[int, int], tolerance: int = 1) -> bool:
        """检查是否到达目标位置"""
        distance = abs(current[0] - target[0]) + abs(current[1] - target[1])
        return distance <= tolerance
    
    def setup_toio_task_execution(self, agent_id: str, task_info: Dict[str, Any]) -> bool:
        """
        设置 toio 任务执行，包括分配任务和注册位置回调
        
        Args:
            agent_id: agent 标识
            task_info: 任务信息
            
        Returns:
            bool: 设置是否成功
        """
        # 首先尝试分配任务
        if self.assign_task(task_info, agent_id):
            # 分配成功后注册位置回调
            target_position = task_info.get('location', (0, 0))
            self.register_toio_position_callback(agent_id, target_position, task_info)
            
            print(f"🚀 为 {agent_id} 设置 toio 任务执行: {task_info['task']} @ {target_position}")
            return True
        else:
            print(f"❌ toio 任务设置失败: 无法分配任务给 {agent_id}")
            return False
    
    def get_toio_navigation_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取 toio 导航信息
        
        Args:
            agent_id: agent 标识
            
        Returns:
            dict: 导航信息，包括当前位置、目标位置、路径规划等
        """
        if agent_id not in self.agents:
            return None
        
        current_pos = self.agents[agent_id]['position']
        navigation_info = {
            'agent_id': agent_id,
            'current_position': current_pos,
            'target_position': None,
            'path': [],
            'estimated_time': 0,
            'obstacles': []
        }
        
        # 如果有注册的回调，添加目标位置信息
        if hasattr(self, '_toio_callbacks') and agent_id in self._toio_callbacks:
            target_pos = self._toio_callbacks[agent_id]['target_position']
            navigation_info['target_position'] = target_pos
            navigation_info['path'] = self._calculate_simple_path(current_pos, target_pos)
            navigation_info['estimated_time'] = len(navigation_info['path']) * 2  # 估算：每步2秒
        
        return navigation_info
    
    def _calculate_simple_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """计算简单的直线路径"""
        path = []
        x1, y1 = start
        x2, y2 = end
        
        # 简单的曼哈顿距离路径
        while x1 != x2 or y1 != y2:
            if x1 < x2:
                x1 += 1
            elif x1 > x2:
                x1 -= 1
            elif y1 < y2:
                y1 += 1
            elif y1 > y2:
                y1 -= 1
            path.append((x1, y1))
        
        return path
    
    def get_toio_status_summary(self) -> str:
        """获取 toio 状态摘要"""
        summary = "🤖 Toio 机器人状态摘要:\n"
        
        for agent_id, agent_info in self.agents.items():
            current_pos = agent_info['position']
            current_action = agent_info['action']
            
            summary += f"\n  {agent_id}:\n"
            summary += f"    当前位置: {current_pos}\n"
            summary += f"    当前动作: {current_action}\n"
            
            # 如果有目标位置，显示导航信息
            if hasattr(self, '_toio_callbacks') and agent_id in self._toio_callbacks:
                target_pos = self._toio_callbacks[agent_id]['target_position']
                task_name = self._toio_callbacks[agent_id]['task_info'].get('task', 'unknown')
                distance = abs(current_pos[0] - target_pos[0]) + abs(current_pos[1] - target_pos[1])
                
                summary += f"    目标位置: {target_pos}\n"
                summary += f"    执行任务: {task_name}\n"
                summary += f"    剩余距离: {distance} 步\n"
            else:
                summary += f"    状态: 空闲中\n"
        
        return summary
    
    def clear_toio_callbacks(self):
        """清除所有 toio 回调"""
        if hasattr(self, '_toio_callbacks'):
            count = len(self._toio_callbacks)
            self._toio_callbacks.clear()
            print(f"🧹 清除了 {count} 个 toio 回调")