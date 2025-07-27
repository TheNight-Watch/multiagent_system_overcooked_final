#!/usr/bin/env python3
"""
测试修复后的完整系统
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import process_dish_order


def test_complete_system():
    """测试完整的多智能体系统"""
    print("🧪 测试修复后的完整多智能体系统")
    print("=" * 50)
    
    try:
        # 测试制作炝炒西兰花
        dish_name = "炝炒西兰花"
        print(f"🍳 测试制作: {dish_name}")
        
        result = process_dish_order(dish_name)
        
        print(f"\n📊 执行结果:")
        print(result)
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_system()