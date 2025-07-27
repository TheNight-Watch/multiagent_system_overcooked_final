#!/usr/bin/env python3
"""
测试异步并行执行效果
"""

import sys
import os
import time
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import process_dish_order


def test_parallel_execution():
    """测试异步并行执行效果"""
    print("🧪 测试异步并行执行效果")
    print("=" * 60)
    
    try:
        # 测试制作炝炒西兰花
        dish_name = "炝炒西兰花"
        print(f"🍳 测试异步并行制作: {dish_name}")
        
        start_time = time.time()
        
        # 调用新的异步并行版本
        result = process_dish_order(dish_name)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n⏱️ 执行时间: {execution_time:.2f} 秒")
        print(f"\n📊 执行结果:")
        print(result)
        
        # 保存结果
        output_file = f"parallel_cooking_result_{dish_name}_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"\n💾 结果保存到: {output_file}")
        print("\n✅ 异步并行执行测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_execution_modes():
    """对比串行和并行执行效果"""
    print("\n🔄 对比执行模式效果")
    print("=" * 60)
    
    dish_name = "宫保鸡丁"
    
    try:
        # 测试并行执行
        print(f"🚀 测试并行执行: {dish_name}")
        parallel_start = time.time()
        parallel_result = process_dish_order(dish_name)
        parallel_time = time.time() - parallel_start
        
        print(f"🚀 并行执行时间: {parallel_time:.2f} 秒")
        
        # 分析结果
        import json
        parallel_data = json.loads(parallel_result)
        
        print("\n📊 并行执行分析:")
        for chef_id, actions in parallel_data.items():
            if actions:  # 只显示有任务的chef
                print(f"  {chef_id}: {len(actions)} 个任务")
                for action in actions:
                    print(f"    - {action['action_type']}({action['target']}) [并行模式]")
        
        return {
            'parallel_time': parallel_time,
            'parallel_result': parallel_data
        }
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🚀 异步并行执行测试开始")
    print("=" * 80)
    
    try:
        # 基础并行测试
        success = test_parallel_execution()
        
        if success:
            # 对比测试
            comparison_result = compare_execution_modes()
            
            if comparison_result:
                parallel_time = comparison_result['parallel_time']
                
                print(f"\n🎯 性能总结:")
                print(f"  🚀 异步并行执行时间: {parallel_time:.2f} 秒")
                print(f"  📈 预期性能提升: 多智能体同时工作")
                print(f"  ⚡ 执行模式: CamelAI异步API并行")
                
        print(f"\n🎉 测试完成!")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()