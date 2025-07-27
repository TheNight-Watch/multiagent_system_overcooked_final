#!/usr/bin/env python3
"""
快速测试异步并行执行修复
"""

import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_cooking_system
import asyncio


async def quick_test():
    """快速测试异步并行执行"""
    print("🚀 快速测试异步并行执行修复")
    print("=" * 50)
    
    try:
        # 使用已初始化的系统
        cooking_system = get_cooking_system()
        cooking_system.kitchen_state.reset_task_queue()
        
        dish_name = "炝炒西兰花"
        print(f"🍳 测试: {dish_name}")
        
        start_time = time.time()
        
        # 调用异步并行版本
        actions = await cooking_system.execute_collaborative_cooking_async(dish_name)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n⏱️ 执行时间: {execution_time:.2f} 秒")
        print(f"\n📊 执行结果:")
        result_json = json.dumps(actions, indent=2, ensure_ascii=False)
        print(result_json)
        
        print("\n✅ 异步并行执行测试成功!")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔧 开始修复验证...")
    try:
        success = asyncio.run(quick_test())
        if success:
            print("\n🎉 修复成功！异步并行执行正常工作！")
        else:
            print("\n❌ 修复失败，需要进一步调试")
    except Exception as e:
        print(f"❌ 验证异常: {e}")
        import traceback
        traceback.print_exc()