#!/usr/bin/env python3
"""
诊断toio碰撞问题的调试脚本
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toio_integration.controller import ToioController


def debug_collision_system():
    """调试碰撞避障系统"""
    print("🔍 诊断toio避障系统问题")
    print("=" * 50)
    
    try:
        # 创建带避障的控制器
        print("🔌 初始化ToioController (避障启用)...")
        controller = ToioController(num_cubes=3, connect_timeout=10.0, enable_collision_avoidance=True)
        
        time.sleep(3)  # 等待系统初始化
        
        # 获取cube列表
        cubes = controller.get_cubes()
        cube_ids = list(cubes.keys())
        print(f"📱 检测到 {len(cube_ids)} 个cube: {cube_ids}")
        
        if len(cube_ids) < 2:
            print("❌ 需要至少2个cube来测试碰撞避障")
            return
        
        # 检查避障系统状态
        status = controller.get_collision_avoidance_status()
        print(f"🛡️ 避障系统状态: {status}")
        
        if not status.get('enabled'):
            print("❌ 避障系统未启用")
            return
        
        # 获取当前位置
        print("\n📍 当前位置:")
        current_positions = {}
        for cube_id in cube_ids:
            pos = controller.get_position(cube_id)
            if pos and hasattr(pos, 'point'):
                current_positions[cube_id] = (pos.point.x, pos.point.y)
                print(f"  {cube_id}: ({pos.point.x}, {pos.point.y})")
            else:
                print(f"  {cube_id}: 位置未知")
        
        # 测试场景1: 让两个cube移动到相近位置
        print("\n🧪 测试场景1: 相近目标位置")
        cube1, cube2 = cube_ids[0], cube_ids[1]
        
        target1 = (200, 200)
        target2 = (210, 210)  # 非常接近的位置
        
        print(f"让 {cube1} 移动到 {target1}")
        print(f"让 {cube2} 移动到 {target2}")
        
        # 同时发送移动命令
        result1 = controller.safe_move_to(cube1, target1[0], target1[1])
        result2 = controller.safe_move_to(cube2, target2[0], target2[1])
        
        print(f"{cube1} 移动结果: {result1}")
        print(f"{cube2} 移动结果: {result2}")
        
        # 监控5秒
        print("\n⏱️ 监控移动过程 (5秒)...")
        for i in range(5):
            time.sleep(1)
            print(f"--- 第{i+1}秒 ---")
            
            for cube_id in [cube1, cube2]:
                pos = controller.get_position(cube_id)
                if pos and hasattr(pos, 'point'):
                    print(f"  {cube_id}: ({pos.point.x}, {pos.point.y})")
                else:
                    print(f"  {cube_id}: 位置未知")
        
        # 获取最终状态
        print("\n📊 最终避障系统状态:")
        final_status = controller.get_collision_avoidance_status()
        print(f"避障系统: {final_status}")
        
        # 测试场景2: 交叉路径
        print("\n🧪 测试场景2: 交叉路径")
        if len(cube_ids) >= 3:
            cube3 = cube_ids[2]
            
            # 让cube1和cube3交换位置
            pos1 = current_positions.get(cube1)
            pos3 = current_positions.get(cube3)
            
            if pos1 and pos3:
                print(f"让 {cube1} 从 {pos1} 移动到 {pos3}")
                print(f"让 {cube3} 从 {pos3} 移动到 {pos1}")
                
                result1 = controller.safe_move_to(cube1, pos3[0], pos3[1])
                result3 = controller.safe_move_to(cube3, pos1[0], pos1[1])
                
                print(f"{cube1} 移动结果: {result1}")
                print(f"{cube3} 移动结果: {result3}")
                
                time.sleep(5)  # 等待移动完成
        
        print("\n✅ 碰撞诊断完成")
        
    except Exception as e:
        print(f"❌ 诊断过程中出现异常: {e}")
        import traceback
        traceback.print_exc()


def debug_simple_collision():
    """简单的碰撞测试"""
    print("🔍 简单碰撞测试")
    print("=" * 50)
    
    try:
        # 不启用避障系统进行对比
        print("🔌 测试1: 不启用避障系统")
        controller1 = ToioController(num_cubes=3, connect_timeout=5.0, enable_collision_avoidance=False)
        
        cubes = controller1.get_cubes()
        cube_ids = list(cubes.keys())
        
        if len(cube_ids) >= 2:
            cube1, cube2 = cube_ids[0], cube_ids[1]
            
            print(f"不带避障: {cube1} -> (150, 150), {cube2} -> (160, 160)")
            controller1.move_to(cube1, 150, 150)
            controller1.move_to(cube2, 160, 160)
            
            time.sleep(3)
            
            # 检查最终位置
            for cube_id in [cube1, cube2]:
                pos = controller1.get_position(cube_id)
                if pos and hasattr(pos, 'point'):
                    print(f"  {cube_id} 最终位置: ({pos.point.x}, {pos.point.y})")
        
        time.sleep(2)
        
        print("\n🔌 测试2: 启用避障系统")
        controller2 = ToioController(num_cubes=3, connect_timeout=5.0, enable_collision_avoidance=True)
        
        time.sleep(3)  # 等待避障系统初始化
        
        cubes2 = controller2.get_cubes()
        cube_ids2 = list(cubes2.keys())
        
        if len(cube_ids2) >= 2:
            cube1, cube2 = cube_ids2[0], cube_ids2[1]
            
            print(f"带避障: {cube1} -> (250, 250), {cube2} -> (260, 260)")
            controller2.safe_move_to(cube1, 250, 250)
            controller2.safe_move_to(cube2, 260, 260)
            
            time.sleep(5)
            
            # 检查最终位置
            for cube_id in [cube1, cube2]:
                pos = controller2.get_position(cube_id)
                if pos and hasattr(pos, 'point'):
                    print(f"  {cube_id} 最终位置: ({pos.point.x}, {pos.point.y})")
                    
            # 检查避障状态
            status = controller2.get_collision_avoidance_status()
            print(f"避障系统状态: {status.get('enabled', False)}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 toio碰撞问题诊断开始")
    print("=" * 60)
    
    try:
        # 运行详细诊断
        debug_collision_system()
        
        print("\n" + "="*60)
        
        # 运行简单对比测试
        debug_simple_collision()
        
    except KeyboardInterrupt:
        print("\n⏹️ 诊断被用户中断")
    except Exception as e:
        print(f"\n❌ 诊断异常: {e}")
        import traceback
        traceback.print_exc()