#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立的碰撞避免测试demo

此demo直接使用ToioController来演示碰撞避免功能，
不依赖于AI agent或main.py的其他组件。
"""

import time
import threading
from typing import List
from controller import ToioController


def demo_collision_avoidance():
    """
    演示碰撞避免功能的主要demo
    """
    print("🚗 Toio 碰撞避免演示")
    print("=" * 50)
    
    # 初始化控制器，连接3个cube
    print("📡 初始化控制器并连接cubes...")
    controller = ToioController(num_cubes=3)
    
    try:
        cubes = controller.get_cube_ids()
        if len(cubes) < 2:
            print("⚠️  至少需要2个cube来演示碰撞避免功能")
            print(f"当前只有 {len(cubes)} 个cube连接")
            if len(cubes) == 0:
                print("将以仿真模式运行demo...")
                return demo_simulation_mode()
        
        print(f"✅ 成功连接 {len(cubes)} 个cubes: {cubes}")
        
        # 设置初始位置和不同颜色用于区分
        initial_positions = [
            (100, 100),  # 左上角
            (400, 100),  # 右上角
            (250, 400),  # 底部中央
        ]
        
        colors = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
        ]
        
        print("\n🎨 设置cube初始位置和颜色...")
        for i, cube_id in enumerate(cubes):
            if i < len(initial_positions):
                x, y = initial_positions[i]
                r, g, b = colors[i]
                
                print(f"  {cube_id}: 移动到 ({x}, {y}), 设置颜色 RGB({r}, {g}, {b})")
                controller.move_to_safe(cube_id, x, y)
                controller.set_led(cube_id, r, g, b)
                time.sleep(1)
        
        # 等待所有cube到达初始位置
        print("\n⏰ 等待所有cube到达初始位置...")
        time.sleep(3)
        
        # 演示1: 两个cube朝对方移动（会发生碰撞）
        # if len(cubes) >= 2:
        #     demo_1_head_on_collision(controller, cubes[:2])
        
        # 演示2: 三个cube同时移动到中央（会发生多重碰撞）
        if len(cubes) >= 3:
            demo_2_converging_movement(controller, cubes[:3])
        
        # 演示3: 比较安全模式vs普通模式
        if len(cubes) >= 2:
            demo_3_safe_vs_direct_mode(controller, cubes[:2])
        
        print("\n🎉 所有演示完成!")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
    finally:
        print("\n🔌 关闭连接...")
        controller.close()


def demo_1_head_on_collision(controller: ToioController, cubes: List[str]):
    """
    演示1: 两个cube正面相撞的情况
    """
    print("\n" + "="*50)
    print("📍 演示1: 正面相撞碰撞避免")
    print("="*50)
    
    cube1, cube2 = cubes[0], cubes[1]
    
    # 重置位置
    print(f"🔄 重置 {cube1} 到左侧 (100, 200)")
    controller.move_to_safe(cube1, 100, 200)
    controller.set_led(cube1, 255, 0, 0)  # 红色
    
    print(f"🔄 重置 {cube2} 到右侧 (400, 200)")
    controller.move_to_safe(cube2, 400, 200)
    controller.set_led(cube2, 0, 255, 0)  # 绿色
    
    time.sleep(3)
    
    # 显示当前位置
    print("\n📍 当前位置:")
    positions = controller.get_all_positions()
    for cube_id, pos in positions.items():
        if cube_id in [cube1, cube2]:
            print(f"  {cube_id}: {pos}")
    
    # 让两个cube朝对方移动（使用安全模式）
    print(f"\n🚀 使用安全模式: {cube1} 和 {cube2} 同时朝对方移动...")
    
    # 创建线程同时移动两个cube
    def move_cube1():
        success = controller.move_to_safe(cube1, 350, 200)
        if success:
            controller.set_led(cube1, 0, 255, 255)  # 青色表示成功
            controller.play_sound(cube1, 1, 80)
        else:
            controller.set_led(cube1, 255, 255, 0)  # 黄色表示失败
    
    def move_cube2():
        time.sleep(0.5)  # 稍微延迟以避免完全同步
        success = controller.move_to_safe(cube2, 150, 200)
        if success:
            controller.set_led(cube2, 255, 0, 255)  # 紫色表示成功
            controller.play_sound(cube2, 1, 80)
        else:
            controller.set_led(cube2, 255, 255, 0)  # 黄色表示失败
    
    # 启动线程
    thread1 = threading.Thread(target=move_cube1)
    thread2 = threading.Thread(target=move_cube2)
    
    thread1.start()
    thread2.start()
    
    # 等待两个线程完成
    thread1.join()
    thread2.join()
    
    print("✅ 演示1完成 - 检查cube是否成功避免碰撞")
    time.sleep(2)


def demo_2_converging_movement(controller: ToioController, cubes: List[str]):
    """
    演示2: 三个cube同时向中央移动
    """
    print("\n" + "="*50)
    print("📍 演示2: 多cube向中央汇聚")
    print("="*50)
    
    cube1, cube2, cube3 = cubes[0], cubes[1], cubes[2]
    
    # 重置到三角形位置
    positions = [
        (150, 150),  # 左上
        (350, 150),  # 右上
        (250, 350),  # 底部
    ]
    
    colors = [
        (255, 0, 0),    # 红色
        (0, 255, 0),    # 绿色
        (0, 0, 255),    # 蓝色
    ]
    
    print("🔄 重置cube位置...")
    for i, cube_id in enumerate([cube1, cube2, cube3]):
        x, y = positions[i]
        r, g, b = colors[i]
        print(f"  {cube_id}: 移动到 ({x}, {y})")
        controller.move_to(cube_id, x, y)
        controller.set_led(cube_id, r, g, b)
        time.sleep(1)
    
    time.sleep(2)
    
    # 显示当前位置
    print("\n📍 当前位置:")
    current_positions = controller.get_all_positions()
    for cube_id, pos in current_positions.items():
        if cube_id in [cube1, cube2, cube3]:
            print(f"  {cube_id}: {pos}")
    
    # 所有cube同时移动到中央
    target_center = (250, 250)
    print(f"\n🎯 所有cube同时移动到中央 {target_center}...")
    
    def move_to_center(cube_id, delay=0):
        if delay > 0:
            time.sleep(delay)
        success = controller.move_to_safe(cube_id, target_center[0], target_center[1])
        if success:
            controller.set_led(cube_id, 255, 255, 255)  # 白色表示成功
            controller.play_sound(cube_id, 4, 80)
        else:
            controller.set_led(cube_id, 255, 255, 0)  # 黄色表示失败
    
    # 创建线程，稍微错开启动时间
    threads = []
    for i, cube_id in enumerate([cube1, cube2, cube3]):
        thread = threading.Thread(target=move_to_center, args=(cube_id, i * 0.3))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("✅ 演示2完成 - 检查cube是否成功避免在中央碰撞")
    time.sleep(3)


def demo_3_safe_vs_direct_mode(controller: ToioController, cubes: List[str]):
    """
    演示3: 比较安全模式和直接模式
    """
    print("\n" + "="*50)
    print("📍 演示3: 安全模式 vs 直接模式对比")
    print("="*50)
    
    cube1, cube2 = cubes[0], cubes[1]
    
    # # 第一轮：直接模式（可能碰撞）
    # print("🔴 第一轮: 使用直接模式 (可能发生碰撞)")
    
    # # 重置位置
    # controller.move_to(cube1, 100, 250)
    # controller.set_led(cube1, 255, 0, 0)  # 红色
    # controller.move_to(cube2, 200, 250)
    # controller.set_led(cube2, 255, 100, 0)  # 橙色
    # time.sleep(2)
    
    # print("⚠️  cube1 将直接穿过 cube2 的位置移动...")
    
    # def direct_move():
    #     # cube1 直接移动穿过 cube2
    #     success = controller.move_to(cube1, 350, 250)  # 直接模式
    #     if success:
    #         controller.set_led(cube1, 255, 255, 0)  # 黄色表示成功
    #     else:
    #         controller.set_led(cube1, 255, 0, 0)    # 红色表示失败
    
    # thread = threading.Thread(target=direct_move)
    # thread.start()
    # thread.join()
    
    # time.sleep(3)
    
    # 第二轮：安全模式（避免碰撞）
    print("\n🟢 第二轮: 使用安全模式 (避免碰撞)")
    
    # 重置位置
    controller.move_to(cube1, 100, 300)
    controller.set_led(cube1, 0, 255, 0)  # 绿色
    controller.move_to(cube2, 200, 300)
    controller.set_led(cube2, 0, 255, 100)  # 青绿色
    time.sleep(2)
    
    print("✅ cube1 将使用安全路径绕过 cube2...")
    
    def safe_move():
        # cube1 安全移动绕过 cube2
        success = controller.move_to_safe(cube1, 350, 300)
        if success:
            controller.set_led(cube1, 0, 255, 255)  # 青色表示成功
            controller.play_sound(cube1, 1, 100)
        else:
            controller.set_led(cube1, 255, 255, 0)  # 黄色表示失败
    
    thread = threading.Thread(target=safe_move)
    thread.start()
    thread.join()
    
    print("✅ 演示3完成 - 观察两种模式的区别")
    time.sleep(2)


def demo_simulation_mode():
    """
    仿真模式演示（无真实硬件时）
    """
    print("\n🎮 仿真模式演示")
    print("=" * 50)
    
    # 创建仿真控制器
    controller = ToioController(num_cubes=0)  # 不连接真实硬件
    
    # 手动创建仿真cube
    from controller import CubeState
    from toio.cube.api.motor import CubeLocation, Point
    
    sim_cubes = []
    initial_positions = [(100, 100), (400, 100), (250, 400)]
    
    for i in range(3):
        cube_id = f"sim_cube_{i+1}"
        cube_state = CubeState(
            id=cube_id,
            cube=None,
            position=CubeLocation(point=Point(x=initial_positions[i][0], y=initial_positions[i][1]), angle=0),
            connected=True
        )
        controller._cubes[cube_id] = cube_state
        sim_cubes.append(cube_id)
        print(f"📱 创建仿真cube: {cube_id} 在位置 {initial_positions[i]}")
    
    try:
        # 演示碰撞检测逻辑
        print("\n🧪 测试碰撞检测算法...")
        
        # 测试1: 直线路径碰撞检测
        start_pos = (100, 200)
        end_pos = (400, 200)
        exclude_cube = sim_cubes[0]
        
        print(f"\n测试路径: {start_pos} → {end_pos}")
        print(f"排除cube: {exclude_cube}")
        
        collision = controller._check_path_collision(start_pos, end_pos, exclude_cube)
        print(f"碰撞检测结果: {'⚠️ 检测到碰撞' if collision else '✅ 路径安全'}")
        
        if collision:
            waypoint = controller._find_waypoint(start_pos, end_pos, exclude_cube)
            print(f"建议绕行点: {waypoint}")
        
        # 测试2: 演示完整的安全移动
        print(f"\n🎯 演示安全移动: {sim_cubes[0]} 从 {start_pos} 到 {end_pos}")
        
        # 更新起始位置
        controller._cubes[sim_cubes[0]].position = CubeLocation(
            point=Point(x=start_pos[0], y=start_pos[1]), angle=0
        )
        
        success = controller.move_to_safe(sim_cubes[0], end_pos[0], end_pos[1])
        print(f"移动结果: {'✅ 成功' if success else '❌ 失败'}")
        
        # 显示最终位置
        final_positions = controller.get_all_positions()
        print(f"\n📍 最终位置:")
        for cube_id, pos in final_positions.items():
            print(f"  {cube_id}: {pos}")
        
        print("\n🎉 仿真演示完成!")
        
    finally:
        controller.close()


if __name__ == "__main__":
    print("🤖 启动Toio碰撞避免演示程序")
    print("此程序将演示多个toio cube的智能碰撞避免功能")
    print()
    
    try:
        demo_collision_avoidance()
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断程序")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
    
    print("\n👋 演示程序结束")
