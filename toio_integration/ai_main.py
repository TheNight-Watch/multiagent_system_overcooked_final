#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example script demonstrating how to use the ToioAIAgent high-level API
for AI agents to control toio core cubes using semantic commands
"""

import time
from ai_agent import ToioAIAgent


def main():
    """
    Main function demonstrating how to use the ToioAIAgent for AI systems
    """
    print("🤖 Toio AI Agent High-Level API Demo")
    print("-" * 50)
    
    # 方式1: 初始化时直接为cubes指定名称
    print("方式1: 初始化时为cubes指定名称...")
    agent = ToioAIAgent(
        num_cubes=2, 
        simulation_mode=False,  # 使用仿真模式进行演示
        cube_names=["taro", "jiro"]  # 为两个cube指定固定名称
    )
    
    try:
        # 获取所有连接的cubes
        cubes = agent.get_cubes()
        if not cubes:
            print("No cubes connected. Exiting.")
            return
        
        # 显示cube名称分配
        print("\nCube名称分配:")
        for name, cube_id in agent.get_all_cube_names().items():
            print(f"- 名称 '{name}' 分配给 cube {cube_id}")
        
        # 方式2: 使用cube名称来分配角色（明确且可预测）
        print("\n方式2: 使用cube名称分配角色...")
        success1 = agent.assign_role_by_name("robot", "taro")
        success2 = agent.assign_role_by_name("assistant", "jiro")
        
        print(f"角色分配结果: robot -> taro: {success1}, assistant -> jiro: {success2}")
        
        # 方式3: 批量角色分配
        print("\n方式3: 批量角色分配...")
        role_assignments = {
            "main_worker": "taro",
            "helper": "jiro"
        }
        batch_success = agent.assign_roles_with_names(role_assignments)
        print(f"批量分配结果: {batch_success}")
        
        # 显示最终的角色分配
        print("\n最终角色分配:")
        for role_name, cube_id in agent.get_all_roles().items():
            # 查找cube的名称
            cube_name = None
            for name, cid in agent.get_all_cube_names().items():
                if cid == cube_id:
                    cube_name = name
                    break
            print(f"- 角色 '{role_name}' 分配给 cube {cube_id} (名称: {cube_name})")
        
        # 显示可用的位置、灯光和声音
        print("\n可用位置:")
        for name, (x, y) in list(agent.get_all_locations().items())[:5]:  # 显示前5个
            print(f"- {name}: ({x}, {y})")
        print("... 还有更多")
        
        print("\n可用灯光预设:")
        for name, (r, g, b) in list(agent.get_all_lights().items())[:5]:  # 显示前5个
            print(f"- {name}: RGB({r}, {g}, {b})")
        print("... 还有更多")
        
        print("\n可用声音预设:")
        for name, sound_id in list(agent.get_all_sounds().items())[:5]:  # 显示前5个
            print(f"- {name}: 声音ID {sound_id}")
        print("... 还有更多")
        
        # 使用明确的角色控制演示
        print("\n=== 使用角色进行控制演示 ===")
        
        # 为两个角色设置不同的初始灯光以便识别
        agent.set_light_by_role("main_worker", "blue")
        agent.set_light_by_role("helper", "green")
        time.sleep(1)
        
        # 将main_worker移动到厨房
        print("\n将 'main_worker' 移动到厨房...")
        success = agent.go_to_by_role("main_worker", "kitchen")
        
        if success:
            print("移动成功!")
            agent.set_light_by_role("main_worker", "green")
            agent.play_sound_by_role("main_worker", "success")
            location = agent.get_position_name_by_role("main_worker")
            print(f"Main worker当前位置: {location}")
        else:
            print("移动失败!")
            agent.set_light_by_role("main_worker", "red")
            agent.play_sound_by_role("main_worker", "error")
        
        time.sleep(2)
        
        # 将helper移动到客厅
        print("\n将 'helper' 移动到客厅...")
        success = agent.go_to_by_role("helper", "living_room")
        if success:
            print("移动成功!")
            agent.set_light_by_role("helper", "purple")
            agent.play_sound_by_role("helper", "notification")
            location = agent.get_position_name_by_role("helper")
            print(f"Helper当前位置: {location}")
        
        # 演示同时控制两个角色
        print("\n=== 同时控制演示 ===")
        
        # 设置不同的灯光
        agent.set_light_by_role("main_worker", "yellow")
        agent.set_light_by_role("helper", "cyan")
        
        # 移动到不同位置
        print("\n将 'main_worker' 移动到卧室，'helper' 移动到入口...")
        
        success1 = agent.go_to_by_role("main_worker", "bedroom")
        success2 = agent.go_to_by_role("helper", "entrance")
        
        print(f"移动结果: main_worker: {success1}, helper: {success2}")
        
        # 播放不同声音
        agent.play_sound_by_role("main_worker", "happy")
        agent.play_sound_by_role("helper", "chime")
        
        # 显示当前位置
        main_worker_location = agent.get_position_name_by_role("main_worker")
        helper_location = agent.get_position_name_by_role("helper")
        print(f"当前位置 - main_worker: {main_worker_location}, helper: {helper_location}")
        
        # 添加自定义位置和灯光预设
        print("\n=== 自定义设置演示 ===")
        print("添加自定义位置 'playground' 在 (300, 300)")
        agent.add_location("playground", 300, 300)
        
        print("添加自定义灯光预设 'aqua' (0, 200, 200)")
        agent.add_light("aqua", 0, 200, 200)
        
        # 使用新的自定义位置和灯光
        print("\n将 'main_worker' 移动到playground并设置aqua灯光...")
        agent.set_light_by_role("main_worker", "aqua")
        success = agent.go_to_by_role("main_worker", "playground")
        if success:
            agent.play_sound_by_role("main_worker", "happy")
            print(f"Main worker当前位置: {agent.get_position_name_by_role('main_worker')}")
        
        print("\n演示完成!")
        
    finally:
        # 总是关闭agent以正确断开连接
        print("\n断开与cubes的连接...")
        agent.close()
        print("已断开连接。再见!")



if __name__ == "__main__":
    main()
