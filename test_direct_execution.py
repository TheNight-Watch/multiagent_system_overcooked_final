#!/usr/bin/env python3
"""
直接测试agent工具调用，绕过CamelAI Workforce的复杂性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import SharedKitchenState
from agents import generate_cooking_tasks, make_universal_chef_team
from toio_integration.cooking_toolkit import CookingToolkit

# 模拟控制器（为了测试）
class MockToioController:
    def __init__(self):
        self.connected = True
        
    def get_cubes(self):
        return ["cube_1", "cube_2", "cube_3"]
    
    def get_cube_ids(self):
        return ["cube_1", "cube_2", "cube_3"]
    
    def move_to(self, cube_id, x, y):
        print(f"🚶 移动 {cube_id} 到位置 ({x}, {y})")
        return True
    
    def set_led(self, cube_id, r, g, b):
        print(f"💡 设置 {cube_id} LED颜色: RGB({r}, {g}, {b})")
        return True
    
    def play_sound(self, cube_id, sound_id, volume=80):
        print(f"🔊 {cube_id} 播放声音 {sound_id}，音量 {volume}")
        return True
    
    def get_position(self, cube_id):
        positions = {"cube_1": (100, 100), "cube_2": (150, 150), "cube_3": (200, 200)}
        return positions.get(cube_id, (0, 0))

def test_direct_agent_execution():
    """测试直接agent执行"""
    print("🧪 测试直接agent工具调用")
    print("=" * 50)
    
    # 初始化组件
    kitchen_state = SharedKitchenState()
    mock_toio = MockToioController()
    cooking_toolkit = CookingToolkit(mock_toio, kitchen_state)
    chef_team = make_universal_chef_team(cooking_toolkit)
    
    # 生成任务
    dish_name = "宫保鸡丁"
    task_list = generate_cooking_tasks(dish_name)
    kitchen_state.add_cooking_tasks(dish_name, task_list)
    
    print("📋 任务队列:")
    print(kitchen_state.get_task_queue_summary())
    
    # 测试直接调用chef_1的工具
    print("\n🧪 测试chef_1直接调用pick_x工具")
    chef_1 = chef_team['chef_1']
    
    # 获取可用工具
    tools = cooking_toolkit.get_tools()
    print(f"可用工具: {[tool.get_function_name() for tool in tools]}")
    
    # 尝试直接调用pick_x
    try:
        # 找到pick_x工具
        pick_x_tool = None
        for tool in tools:
            if tool.get_function_name() == 'pick_x':
                pick_x_tool = tool
                break
        
        if pick_x_tool:
            print(f"找到pick_x工具: {pick_x_tool}")
            # 直接调用工具
            result = pick_x_tool.func("chef_1", "meat")
            print(f"工具调用结果: {result}")
        else:
            print("未找到pick_x工具")
            
    except Exception as e:
        print(f"工具调用出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_agent_execution()