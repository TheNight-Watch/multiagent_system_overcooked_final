#!/usr/bin/env python3
"""
测试修复后的避障系统
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toio_integration.controller import ToioController


def test_fixed_collision_system():
    """测试修复后的避障系统"""
    print("🧪 测试修复后的避障系统")
    print("=" * 50)
    
    try:
        # 创建控制器（启用避障）
        print("🔌 初始化带避障系统的ToioController...")
        controller = ToioController(num_cubes=3, connect_timeout=8.0, enable_collision_avoidance=True)
        
        # 等待系统完全初始化
        time.sleep(3)
        
        # 获取cube列表
        cubes = controller.get_cubes()
        cube_ids = list(cubes.keys())
        print(f"📱 检测到 {len(cube_ids)} 个cube: {cube_ids}")
        
        if len(cube_ids) < 2:
            print("❌ 需要至少2个cube来测试")
            return
        
        cube1, cube2 = cube_ids[0], cube_ids[1]
        
        # 获取当前位置
        print("\n📍 当前位置:")
        pos1 = controller.get_position(cube1)
        pos2 = controller.get_position(cube2)
        
        if pos1 and hasattr(pos1, 'point'):
            print(f"  {cube1}: ({pos1.point.x}, {pos1.point.y})")
        if pos2 and hasattr(pos2, 'point'):
            print(f"  {cube2}: ({pos2.point.x}, {pos2.point.y})")
        
        # 测试修复：让两个cube移动到相近但不冲突的位置
        print("\n🧪 测试场景：相近目标位置 (50mm+ 距离)")
        target1 = (200, 200)
        target2 = (260, 260)  # 距离约85mm，应该安全
        
        print(f"🎯 让 {cube1} 移动到 {target1}")
        print(f"🎯 让 {cube2} 移动到 {target2}")
        
        # 同时发送移动命令
        result1 = controller.safe_move_to(cube1, target1[0], target1[1])
        time.sleep(0.3)  # 短暂间隔
        result2 = controller.safe_move_to(cube2, target2[0], target2[1])
        
        print(f"📊 {cube1} 移动结果: {result1}")
        print(f"📊 {cube2} 移动结果: {result2}")
        
        # 监控5秒钟
        print("\n⏱️ 监控移动过程 (5秒)...")
        for i in range(5):
            time.sleep(1)
            print(f"--- 第{i+1}秒 ---")
            
            pos1 = controller.get_position(cube1)
            pos2 = controller.get_position(cube2)
            
            if pos1 and hasattr(pos1, 'point'):
                dist1 = ((pos1.point.x - target1[0]) ** 2 + (pos1.point.y - target1[1]) ** 2) ** 0.5
                print(f"  {cube1}: ({pos1.point.x}, {pos1.point.y}) [距目标 {dist1:.1f}mm]")
            
            if pos2 and hasattr(pos2, 'point'):
                dist2 = ((pos2.point.x - target2[0]) ** 2 + (pos2.point.y - target2[1]) ** 2) ** 0.5
                print(f"  {cube2}: ({pos2.point.x}, {pos2.point.y}) [距目标 {dist2:.1f}mm]")
        
        # 测试场景2：真正冲突的位置
        print("\n🧪 测试场景2：真正冲突的位置 (<50mm 距离)")
        target3 = (300, 300)
        target4 = (320, 320)  # 距离约28mm，应该被阻止
        
        if len(cube_ids) >= 3:
            cube3 = cube_ids[2]
            print(f"🎯 让 {cube1} 移动到 {target3}")
            print(f"🎯 让 {cube3} 移动到 {target4}")
            
            result3 = controller.safe_move_to(cube1, target3[0], target3[1])
            time.sleep(0.3)
            result4 = controller.safe_move_to(cube3, target4[0], target4[1])
            
            print(f"📊 {cube1} 移动结果: {result3}")
            print(f"📊 {cube3} 移动结果 (应该被阻止): {result4}")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fixed_collision_system()