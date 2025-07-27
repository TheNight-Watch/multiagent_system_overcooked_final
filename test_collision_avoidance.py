#!/usr/bin/env python3
"""
toio避障系统测试脚本

测试A*算法路径规划和多机器人避障功能
"""

import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from toio_integration.collision_avoidance import CollisionAvoidanceSystem, Position
from toio_integration.position_tracker import PositionTracker
from toio_integration.path_planner import PathPlanner, PlanningPriority


class MockToioController:
    """模拟toio控制器，用于测试"""
    
    def __init__(self):
        self.cubes = {
            "cube_1": {"position": (100, 100)},
            "cube_2": {"position": (200, 200)}, 
            "cube_3": {"position": (300, 300)}
        }
        
    def get_cubes(self):
        return self.cubes
    
    def get_position(self, cube_id):
        if cube_id in self.cubes:
            pos = self.cubes[cube_id]["position"]
            
            # 模拟CubeLocation对象
            class MockCubeLocation:
                def __init__(self, x, y):
                    self.point = MockPoint(x, y)
            
            class MockPoint:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
            
            return MockCubeLocation(pos[0], pos[1])
        return None
    
    def move_to(self, cube_id, x, y, angle=0):
        """模拟移动"""
        if cube_id in self.cubes:
            self.cubes[cube_id]["position"] = (x, y)
            print(f"🚶 模拟移动 {cube_id} 到 ({x}, {y})")
            return True
        return False


def test_collision_avoidance_system():
    """测试避障系统核心功能"""
    print("🧪 测试避障系统核心功能")
    print("=" * 50)
    
    # 初始化避障系统
    collision_system = CollisionAvoidanceSystem(grid_size=10)
    
    # 测试1: 添加机器人位置
    print("\n📍 测试1: 添加机器人位置")
    collision_system.update_robot_position("cube_1", 100, 100)
    collision_system.update_robot_position("cube_2", 200, 200)
    collision_system.update_robot_position("cube_3", 300, 300)
    
    status = collision_system.get_system_status()
    print(f"系统状态: {status}")
    
    # 测试2: 路径规划
    print("\n🗺️ 测试2: A*路径规划")
    
    # cube_1从(100,100)移动到(400,400)
    path = collision_system.plan_path("cube_1", (100, 100), (400, 400))
    print(f"cube_1路径规划结果: {len(path)}个点")
    if path:
        print(f"路径: {path[:5]}{'...' if len(path) > 5 else ''}")
    
    # 测试3: 安全检查
    print("\n🛡️ 测试3: 移动安全检查")
    safe = collision_system.is_safe_to_move("cube_1", (150, 150))
    print(f"cube_1移动到(150,150)是否安全: {safe}")
    
    safe = collision_system.is_safe_to_move("cube_1", (200, 200))
    print(f"cube_1移动到(200,200)是否安全: {safe}")


def test_position_tracker():
    """测试位置追踪系统"""
    print("\n🧪 测试位置追踪系统")
    print("=" * 50)
    
    mock_controller = MockToioController()
    position_tracker = PositionTracker(mock_controller, update_interval=0.2)
    
    # 启动追踪
    position_tracker.start_tracking()
    
    print("📍 启动位置追踪，观察5秒...")
    time.sleep(5)
    
    # 检查追踪状态
    status = position_tracker.get_tracking_status()
    print(f"追踪状态: {status}")
    
    # 检查位置历史
    for cube_id in ["cube_1", "cube_2", "cube_3"]:
        history = position_tracker.get_position_history(cube_id)
        print(f"{cube_id}位置历史: {len(history)}个记录")
        
        if history:
            latest = history[-1]
            print(f"  最新位置: ({latest.x}, {latest.y})")
    
    # 停止追踪
    position_tracker.stop_tracking()


def test_path_planner():
    """测试路径规划器"""
    print("\n🧪 测试路径规划器")
    print("=" * 50)
    
    # 初始化组件
    mock_controller = MockToioController()
    collision_system = CollisionAvoidanceSystem(grid_size=10)
    position_tracker = PositionTracker(mock_controller, update_interval=0.1)
    path_planner = PathPlanner(collision_system, position_tracker)
    
    # 启动系统
    position_tracker.start_tracking()
    path_planner.start_planner()
    
    # 等待系统初始化
    time.sleep(1)
    
    # 同步机器人位置到避障系统
    for cube_id in ["cube_1", "cube_2", "cube_3"]:
        pos = position_tracker.get_current_position(cube_id)
        if pos:
            collision_system.update_robot_position(cube_id, pos[0], pos[1])
    
    print("🗺️ 请求路径规划...")
    
    # 测试1: 简单路径规划
    success = path_planner.request_path("cube_1", (100, 100), (400, 400), PlanningPriority.NORMAL)
    print(f"cube_1路径请求结果: {success}")
    
    # 测试2: 冲突路径规划
    success = path_planner.request_path("cube_2", (200, 200), (350, 350), PlanningPriority.NORMAL)
    print(f"cube_2路径请求结果: {success}")
    
    # 等待规划完成
    time.sleep(2)
    
    # 检查规划结果
    for cube_id in ["cube_1", "cube_2"]:
        path = path_planner.get_path(cube_id)
        if path:
            print(f"{cube_id}规划路径: {len(path)}个点")
        else:
            print(f"{cube_id}未找到路径")
    
    # 获取规划器状态
    status = path_planner.get_planner_status()
    print(f"规划器状态: {status}")
    
    # 停止系统
    path_planner.stop_planner()
    position_tracker.stop_tracking()


def test_integrated_system():
    """测试完整集成系统"""
    print("\n🧪 测试完整集成系统")
    print("=" * 50)
    
    try:
        from toio_integration.controller import ToioController
        
        # 创建控制器（启用避障）
        print("🔌 初始化带避障系统的ToioController...")
        controller = ToioController(num_cubes=3, enable_collision_avoidance=True)
        
        # 等待系统初始化
        time.sleep(2)
        
        # 获取避障系统状态
        status = controller.get_collision_avoidance_status()
        print(f"避障系统状态: {status}")
        
        # 测试安全移动
        print("\n🛡️ 测试安全移动...")
        cube_ids = list(controller.get_cubes().keys())
        
        if len(cube_ids) >= 2:
            cube1, cube2 = cube_ids[0], cube_ids[1]
            
            print(f"让 {cube1} 安全移动到 (150, 150)")
            result1 = controller.safe_move_to(cube1, 150, 150)
            print(f"移动结果: {result1}")
            
            print(f"让 {cube2} 安全移动到 (160, 160)")
            result2 = controller.safe_move_to(cube2, 160, 160)
            print(f"移动结果: {result2}")
            
            # 等待移动完成
            time.sleep(3)
            
            # 获取最终状态
            final_status = controller.get_collision_avoidance_status()
            print(f"最终状态: {final_status}")
        
        print("✅ 集成测试完成")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试函数"""
    print("🚀 toio避障系统测试开始")
    print("=" * 60)
    
    try:
        # 测试1: 避障系统核心
        test_collision_avoidance_system()
        
        # 测试2: 位置追踪
        test_position_tracker()
        
        # 测试3: 路径规划
        test_path_planner()
        
        # 测试4: 完整集成
        test_integrated_system()
        
        print("\n🎉 所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()