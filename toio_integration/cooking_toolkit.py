"""
烹饪动作工具包

提供高级烹饪动作：pick_x, slice_x, cook_x, serve_x
每个动作由底层 toio 控制代码组成
"""

import time
from typing import Dict, Tuple, Optional, Any
from camel.toolkits import BaseToolkit, FunctionTool
from .controller import ToioController as RealToioController


class CookingToolkit(BaseToolkit):
    """
    烹饪动作工具包
    
    为 CamelAI agents 提供高级烹饪动作，每个动作通过 toio 机器人执行
    基于真实的 ToioController API
    """
    
    def __init__(self, toio_controller, kitchen_state=None):
        """
        初始化烹饪工具包
        
        Args:
            toio_controller: 真实的ToioController实例
            kitchen_state: 厨房状态管理器（可选）
        """
        self.toio_controller = toio_controller
        self.kitchen_state = kitchen_state
        
        # 使用真实toio坐标的位置映射
        self.ingredient_positions = {
            "vegetables": (229, 70),   # 储藏区1 - 所有蔬菜
            "meat": (270, 70),         # 储藏区2 - 所有肉类
            "eggs": (355, 70),         # 储藏区1 - 鸡蛋
            "rice": (311, 70),         # 储藏区2 - 米饭
            "seasonings": (188, 70)    # 储藏区1 - 所有调料
        }
        
        self.tool_positions = {
            "cutting_board": (147, 111),   # 切菜区 - cutting_board_2
            "stove": (188, 274),          # 烹饪区 - stove_2
            "counter": (270, 377),        # 通用操作台
            "serve_window": (352, 70)     # 交付区 - serving_counter
        }
        
        # 初始化工具列表
        self.tools = [
            FunctionTool(self.pick_x),
            FunctionTool(self.slice_x), 
            FunctionTool(self.cook_x),
            FunctionTool(self.serve_x),
            FunctionTool(self.get_kitchen_layout),
            FunctionTool(self.check_robot_status),
            FunctionTool(self.set_robot_light),
            FunctionTool(self.get_connection_status)
        ]
        
        print("🍳 烹饪工具包初始化完成 - 基于真实ToioController API")
    
    def pick_x(self, robot_id: str, ingredient_name: str) -> Dict[str, Any]:
        """
        拾取原料
        
        Args:
            robot_id: 机器人ID
            ingredient_name: 原料名称
            
        Returns:
            dict: 执行结果
        """
        print(f"🥬 {robot_id}: 开始拾取原料 '{ingredient_name}'")
        
        # 获取原料位置
        if ingredient_name not in self.ingredient_positions:
            return {
                "success": False,
                "message": f"未知的原料: {ingredient_name}",
                "action": "pick",
                "ingredient": ingredient_name
            }
        
        ingredient_pos = self.ingredient_positions[ingredient_name]
        
        try:
            # 获取对应的cube_id
            cube_id = self._get_cube_id_for_chef(robot_id)
            if not cube_id:
                return {
                    "success": False,
                    "message": f"无法找到{robot_id}对应的toio cube",
                    "action": "pick",
                    "ingredient": ingredient_name
                }
            
            # 1. 设置工作指示灯（蓝色）
            self.toio_controller.set_led(cube_id, 0, 0, 255)
            
            # 2. 播放开始音效
            self.toio_controller.play_sound(cube_id, 2, 80)
            
            # 3. 移动到原料位置
            print(f"🚶 {robot_id}: 移动到原料位置 {ingredient_pos}")
            success = self.toio_controller.move_to_safe(cube_id, ingredient_pos[0], ingredient_pos[1])
            
            if not success:
                return {
                    "success": False,
                    "message": f"移动到原料位置失败",
                    "action": "pick",
                    "ingredient": ingredient_name
                }
            
            # 4. 等待到达（模拟）
            time.sleep(2.0)
            
            # 5. 模拟拾取动作（停顿一下）
            print(f"✋ {robot_id}: 拾取 {ingredient_name}")
            time.sleep(1.0)  # 模拟拾取时间
            
            # 6. 设置完成指示灯（绿色）并播放完成音效
            self.toio_controller.set_led(cube_id, 0, 255, 0)
            self.toio_controller.play_sound(cube_id, 1, 100)
            
            # 7. 更新厨房状态（如果有的话）
            if self.kitchen_state:
                self.kitchen_state.update_agent(robot_id, ingredient_pos, f"picked_{ingredient_name}")
            
            return {
                "success": True,
                "message": f"成功拾取 {ingredient_name}",
                "action": "pick",
                "ingredient": ingredient_name,
                "position": ingredient_pos,
                "robot_id": robot_id
            }
            
        except Exception as e:
            print(f"❌ {robot_id}: 拾取原料失败 - {e}")
            # 设置错误指示灯（红色）
            try:
                cube_id = self._get_cube_id_for_chef(robot_id)
                if cube_id:
                    self.toio_controller.set_led(cube_id, 255, 0, 0)
                    self.toio_controller.play_sound(cube_id, 3, 100)  # 错误音效
            except:
                pass
            
            return {
                "success": False,
                "message": f"拾取失败: {str(e)}",
                "action": "pick",
                "ingredient": ingredient_name
            }
    
    def slice_x(self, robot_id: str, ingredient_name: str) -> Dict[str, Any]:
        """
        切割原料
        
        Args:
            robot_id: 机器人ID  
            ingredient_name: 原料名称
            
        Returns:
            dict: 执行结果
        """
        print(f"🔪 {robot_id}: 开始切割原料 '{ingredient_name}'")
        
        cutting_board_pos = self.tool_positions["cutting_board"]
        
        try:
            # 获取对应的cube_id
            cube_id = self._get_cube_id_for_chef(robot_id)
            if not cube_id:
                return {
                    "success": False,
                    "message": f"无法找到{robot_id}对应的toio cube",
                    "action": "slice",
                    "ingredient": ingredient_name
                }
            
            # 1. 播放开始音效
            self.toio_controller.play_sound(cube_id, 2, 80)
            
            # 2. 移动到案板位置
            print(f"🚶 {robot_id}: 移动到案板位置 {cutting_board_pos}")
            success = self.toio_controller.move_to_safe(cube_id, cutting_board_pos[0], cutting_board_pos[1])
            
            if not success:
                return {
                    "success": False,
                    "message": "移动到案板位置失败",
                    "action": "slice",
                    "ingredient": ingredient_name
                }
            
            # 3. 等待到达（模拟）
            time.sleep(2.0)
            
            # 4. 模拟切割动作
            print(f"🔪 {robot_id}: 切割 {ingredient_name}")
            
            # 模拟切割过程 - 多次短暂停顿
            for i in range(3):
                time.sleep(0.5)
                print(f"  切割进度: {(i+1)*33}%")
                if i < 2:  # 最后一次不播放音效
                    self.toio_controller.play_sound(cube_id, 3, 50)
            
            # 5. 播放完成音效
            self.toio_controller.play_sound(cube_id, 1, 100)
            
            # 6. 更新厨房状态
            if self.kitchen_state:
                self.kitchen_state.update_agent(robot_id, cutting_board_pos, f"sliced_{ingredient_name}")
            
            return {
                "success": True,
                "message": f"成功切割 {ingredient_name}",
                "action": "slice",
                "ingredient": ingredient_name,
                "position": cutting_board_pos,
                "robot_id": robot_id
            }
            
        except Exception as e:
            print(f"❌ {robot_id}: 切割原料失败 - {e}")
            return {
                "success": False,
                "message": f"切割失败: {str(e)}",
                "action": "slice",
                "ingredient": ingredient_name
            }
    
    def cook_x(self, robot_id: str, dish_name: str) -> Dict[str, Any]:
        """
        烹饪菜品
        
        Args:
            robot_id: 机器人ID
            dish_name: 菜品名称
            
        Returns:
            dict: 执行结果
        """
        print(f"🍳 {robot_id}: 开始烹饪菜品 '{dish_name}'")
        
        stove_pos = self.tool_positions["stove"]
        
        try:
            # 获取对应的cube_id
            cube_id = self._get_cube_id_for_chef(robot_id)
            if not cube_id:
                return {
                    "success": False,
                    "message": f"无法找到{robot_id}对应的toio cube",
                    "action": "cook",
                    "dish": dish_name
                }
            
            # 1. 播放开始音效
            self.toio_controller.play_sound(cube_id, 2, 80)
            
            # 2. 移动到灶台位置
            print(f"🚶 {robot_id}: 移动到灶台位置 {stove_pos}")
            success = self.toio_controller.move_to_safe(cube_id, stove_pos[0], stove_pos[1])
            
            if not success:
                return {
                    "success": False,
                    "message": "移动到灶台位置失败",
                    "action": "cook",
                    "dish": dish_name
                }
            
            # 3. 等待到达（模拟）
            time.sleep(2.0)
            
            # 4. 模拟烹饪过程
            print(f"🔥 {robot_id}: 烹饪 {dish_name}")
            
            # 根据菜品类型模拟不同的烹饪时间
            cook_times = {
                "tomato_egg": 4.0,      # 西红柿炒蛋需要4秒
                "fried_rice": 6.0,      # 炒饭需要6秒
                "soup": 8.0,            # 汤需要8秒
            }
            
            cook_time = cook_times.get(dish_name, 3.0)  # 默认3秒
            
            # 分阶段烹饪，每阶段播放音效
            stages = 4
            stage_time = cook_time / stages
            
            for i in range(stages):
                time.sleep(stage_time)
                progress = (i + 1) * 100 // stages
                print(f"  烹饪进度: {progress}%")
                
                # 烹饪过程中的音效
                if i == 0:
                    print(f"  🔥 点火加热...")
                elif i == 1:
                    print(f"  🥄 翻炒中...")
                elif i == 2:
                    print(f"  🧂 调味中...")
                else:
                    print(f"  ✨ 即将完成...")
                
                self.toio_controller.play_sound(cube_id, 3, 60)
            
            # 5. 播放完成音效
            self.toio_controller.play_sound(cube_id, 4, 100)
            print(f"✅ {robot_id}: {dish_name} 烹饪完成!")
            
            # 6. 更新厨房状态
            if self.kitchen_state:
                self.kitchen_state.update_agent(robot_id, stove_pos, f"cooked_{dish_name}")
            
            return {
                "success": True,
                "message": f"成功烹饪 {dish_name}",
                "action": "cook",
                "dish": dish_name,
                "position": stove_pos,
                "robot_id": robot_id,
                "cook_time": cook_time
            }
            
        except Exception as e:
            print(f"❌ {robot_id}: 烹饪菜品失败 - {e}")
            return {
                "success": False,
                "message": f"烹饪失败: {str(e)}",
                "action": "cook",
                "dish": dish_name
            }
    
    def serve_x(self, robot_id: str, dish_name: str) -> Dict[str, Any]:
        """
        交付菜品
        
        Args:
            robot_id: 机器人ID
            dish_name: 菜品名称
            
        Returns:
            dict: 执行结果
        """
        print(f"🍽️ {robot_id}: 开始交付菜品 '{dish_name}'")
        
        serve_pos = self.tool_positions["serve_window"]
        
        try:
            # 获取对应的cube_id
            cube_id = self._get_cube_id_for_chef(robot_id)
            if not cube_id:
                return {
                    "success": False,
                    "message": f"无法找到{robot_id}对应的toio cube",
                    "action": "serve",
                    "dish": dish_name
                }
            
            # 1. 播放开始音效
            self.toio_controller.play_sound(cube_id, 2, 80)
            
            # 2. 移动到交付窗口
            print(f"🚶 {robot_id}: 移动到交付窗口 {serve_pos}")
            success = self.toio_controller.move_to_safe(cube_id, serve_pos[0], serve_pos[1])
            
            if not success:
                return {
                    "success": False,
                    "message": "移动到交付窗口失败",
                    "action": "serve",
                    "dish": dish_name
                }
            
            # 3. 等待到达（模拟）
            time.sleep(2.0)
            
            # 4. 模拟交付过程
            print(f"🎯 {robot_id}: 交付 {dish_name}")
            
            # 小心放置菜品
            print(f"  📋 检查菜品质量...")
            time.sleep(1.0)
            
            print(f"  🍽️ 小心放置到交付窗口...")
            time.sleep(1.5)
            
            print(f"  ✅ 交付完成，等待顾客取餐...")
            time.sleep(0.5)
            
            # 5. 播放完成音效
            self.toio_controller.play_sound(cube_id, 4, 100)
            
            # 6. 更新厨房状态
            if self.kitchen_state:
                self.kitchen_state.update_agent(robot_id, serve_pos, f"served_{dish_name}")
            
            return {
                "success": True,
                "message": f"成功交付 {dish_name}",
                "action": "serve",
                "dish": dish_name,
                "position": serve_pos,
                "robot_id": robot_id
            }
            
        except Exception as e:
            print(f"❌ {robot_id}: 交付菜品失败 - {e}")
            return {
                "success": False,
                "message": f"交付失败: {str(e)}",
                "action": "serve",
                "dish": dish_name
            }
    
    def get_kitchen_layout(self) -> Dict[str, Any]:
        """
        获取厨房布局信息
        
        Returns:
            dict: 厨房布局信息
        """
        return {
            "ingredient_positions": self.ingredient_positions.copy(),
            "tool_positions": self.tool_positions.copy(),
            "layout_description": {
                "storage_area": "储藏区 (229,70) (270,70) - 存放所有5种原料分类",
                "cutting_area": "切菜区 (147,70) - slice_x操作专用",
                "cooking_area": "烹饪区 (188,274) - cook_x操作专用", 
                "serving_area": "交付区 (352,70) - serve_x操作专用",
                "counter_area": "操作台 (270,377) - 通用操作区域"
            }
        }
    
    def check_robot_status(self, robot_id: str) -> Dict[str, Any]:
        """
        检查机器人状态
        
        Args:
            robot_id: 机器人ID
            
        Returns:
            dict: 机器人状态信息
        """
        try:
            cube_id = self._get_cube_id_for_chef(robot_id)
            if not cube_id:
                return {
                    "success": False,
                    "message": f"未找到机器人: {robot_id}"
                }
            
            # 获取真实位置信息
            position = self.toio_controller.get_position(cube_id)
            if position and hasattr(position, 'point'):
                pos = (position.point.x, position.point.y)
            else:
                pos = "unknown"
            
            return {
                "success": True,
                "robot_id": robot_id,
                "cube_id": cube_id,
                "position": pos,
                "status": "connected",
                "last_command": "none"
            }
            
        except Exception as e:
            print(f"❌ 获取{robot_id}状态失败: {e}")
            return {
                "success": False,
                "message": f"获取状态失败: {str(e)}"
            }
    
    def set_robot_light(self, robot_id: str, color: str) -> Dict[str, Any]:
        """
        设置机器人灯光颜色
        
        Args:
            robot_id: 机器人ID
            color: 颜色名称 (red, green, blue, yellow, purple, cyan, white, off)
            
        Returns:
            dict: 执行结果
        """
        print(f"💡 {robot_id}: 设置灯光颜色为 '{color}'")
        
        try:
            cube_id = self._get_cube_id_for_chef(robot_id)
            if not cube_id:
                return {
                    "success": False,
                    "message": f"未找到机器人: {robot_id}"
                }
            
            # 颜色名称到RGB值的映射
            color_map = {
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "yellow": (255, 255, 0),
                "purple": (255, 0, 255),
                "cyan": (0, 255, 255),
                "white": (255, 255, 255),
                "off": (0, 0, 0)
            }
            
            rgb = color_map.get(color.lower(), (255, 255, 255))
            self.toio_controller.set_led(cube_id, rgb[0], rgb[1], rgb[2])
            
            return {
                "success": True,
                "message": f"成功设置 {robot_id} 灯光为 {color}",
                "robot_id": robot_id,
                "cube_id": cube_id,
                "color": color
            }
            
        except Exception as e:
            print(f"❌ {robot_id}: 设置灯光失败 - {e}")
            return {
                "success": False,
                "message": f"设置灯光失败: {str(e)}",
                "robot_id": robot_id,
                "color": color
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        获取toio连接状态
        
        Returns:
            dict: 连接状态信息
        """
        try:
            # 获取所有连接的cubes
            cubes = self.toio_controller.get_cubes()
            
            return {
                "success": True,
                "simulation_mode": False,  # 始终为False，因为我们只支持真实模式
                "connected_robots": {f"chef_{i+1}": {"cube_id": cube_id, "connected": cube_state.connected} 
                                   for i, (cube_id, cube_state) in enumerate(cubes.items())},
                "num_robots": len(cubes)
            }
            
        except Exception as e:
            print(f"❌ 获取连接状态失败 - {e}")
            return {
                "success": False,
                "message": f"获取连接状态失败: {str(e)}"
            }
    
    def get_tools(self):
        """返回所有可用的工具"""
        return self.tools
    
    def _get_cube_id_for_chef(self, robot_id: str) -> Optional[str]:
        """
        获取chef_id对应的cube_id
        
        Args:
            robot_id: chef ID (如 "chef_1")
            
        Returns:
            对应的cube_id，如果没找到则返回None
        """
        try:
            # 从真实控制器获取cube IDs
            cube_ids = self.toio_controller.get_cube_ids()
            if not cube_ids:
                print(f"❌ 未找到可用的toio cubes")
                return None
            
            # 解析chef索引
            chef_index = int(robot_id.split('_')[1]) - 1
            if chef_index < len(cube_ids):
                return cube_ids[chef_index]
            else:
                print(f"❌ {robot_id} 索引超出可用cube数量({len(cube_ids)})")
                return None
                
        except Exception as e:
            print(f"❌ 无法获取{robot_id}对应的cube_id: {e}")
            return None

    def execute_cooking_sequence(self, robot_id: str, actions: list) -> Dict[str, Any]:
        """
        执行一系列烹饪动作
        
        Args:
            robot_id: 机器人ID
            actions: 动作序列，格式为 [{"action": "pick", "target": "tomato"}, ...]
            
        Returns:
            dict: 执行结果
        """
        print(f"🎬 {robot_id}: 开始执行烹饪序列 ({len(actions)} 个动作)")
        
        results = []
        
        for i, action_info in enumerate(actions):
            action_type = action_info.get("action")
            target = action_info.get("target")
            
            print(f"\n--- 动作 {i+1}/{len(actions)}: {action_type} {target} ---")
            
            if action_type == "pick":
                result = self.pick_x(robot_id, target)
            elif action_type == "slice":
                result = self.slice_x(robot_id, target)
            elif action_type == "cook":
                result = self.cook_x(robot_id, target)
            elif action_type == "serve":
                result = self.serve_x(robot_id, target)
            else:
                result = {
                    "success": False,
                    "message": f"未知的动作类型: {action_type}"
                }
            
            results.append(result)
            
            # 如果动作失败，停止执行
            if not result.get("success", False):
                print(f"❌ 动作序列在第 {i+1} 步失败，停止执行")
                break
            
            # 动作间的短暂延迟
            time.sleep(0.5)
        
        success_count = sum(1 for r in results if r.get("success", False))
        
        return {
            "success": success_count == len(actions),
            "total_actions": len(actions),
            "completed_actions": success_count,
            "results": results,
            "robot_id": robot_id
        }
