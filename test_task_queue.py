#!/usr/bin/env python3
"""
测试任务队列系统的依赖关系和防重复机制
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import SharedKitchenState
from agents import generate_cooking_tasks

def test_task_queue_system():
    """测试任务队列系统"""
    print("🧪 测试任务队列系统")
    print("=" * 50)
    
    # 初始化厨房状态
    kitchen_state = SharedKitchenState()
    
    # 测试1：生成宫保鸡丁任务列表
    print("\n📋 测试1: 生成宫保鸡丁任务列表")
    dish_name = "宫保鸡丁"
    task_list = generate_cooking_tasks(dish_name)
    
    print(f"生成了 {len(task_list)} 个任务:")
    for i, task in enumerate(task_list, 1):
        deps_str = f" (依赖: {task['dependencies']})" if task['dependencies'] else " (无依赖)"
        print(f"  {i}. {task['type']}({', '.join(map(str, task['params']))}) {deps_str}")
    
    # 测试2：添加任务到队列
    print(f"\n📋 测试2: 将任务添加到队列")
    kitchen_state.add_cooking_tasks(dish_name, task_list)
    print(kitchen_state.get_task_queue_summary())
    
    # 测试3：获取可用任务（测试依赖关系）
    print(f"\n📋 测试3: 获取各chef可用任务")
    for agent_id in ['chef_1', 'chef_2', 'chef_3']:
        available_task = kitchen_state.get_next_available_task(agent_id)
        if available_task:
            print(f"  {agent_id}: {available_task['type']}({', '.join(map(str, available_task['params']))})")
        else:
            print(f"  {agent_id}: 无可用任务")
    
    # 测试4：模拟执行第一阶段任务（并行取料）
    print(f"\n📋 测试4: 模拟执行第一阶段任务")
    
    # chef_1 开始执行 pick_x(chef_1, meat)
    task = kitchen_state.get_next_available_task('chef_1')
    if task and kitchen_state.start_task_execution(task['id'], 'chef_1'):
        print(f"✅ chef_1 开始执行: {task['type']}")
        kitchen_state.complete_task_execution(task['id'], 'chef_1')
        print(f"✅ chef_1 完成: {task['type']}")
    
    # chef_2 开始执行 pick_x(chef_2, vegetables)  
    task = kitchen_state.get_next_available_task('chef_2')
    if task and kitchen_state.start_task_execution(task['id'], 'chef_2'):
        print(f"✅ chef_2 开始执行: {task['type']}")
        kitchen_state.complete_task_execution(task['id'], 'chef_2')
        print(f"✅ chef_2 完成: {task['type']}")
    
    # chef_3 开始执行 pick_x(chef_3, seasonings)
    task = kitchen_state.get_next_available_task('chef_3')
    if task and kitchen_state.start_task_execution(task['id'], 'chef_3'):
        print(f"✅ chef_3 开始执行: {task['type']}")
        kitchen_state.complete_task_execution(task['id'], 'chef_3')
        print(f"✅ chef_3 完成: {task['type']}")
    
    print("\n📊 第一阶段完成后的状态:")
    print(kitchen_state.get_task_queue_summary())
    
    # 测试5：检查第二阶段任务是否解锁
    print(f"\n📋 测试5: 检查第二阶段任务（cook_x）是否解锁")
    for agent_id in ['chef_1', 'chef_2', 'chef_3']:
        available_task = kitchen_state.get_next_available_task(agent_id)
        if available_task:
            print(f"  {agent_id}: {available_task['type']}({', '.join(map(str, available_task['params']))})")
        else:
            print(f"  {agent_id}: 无可用任务")
    
    # 测试6：执行烹饪任务
    print(f"\n📋 测试6: 执行烹饪任务")
    task = kitchen_state.get_next_available_task('chef_1')
    if task and task['type'] == 'cook_x':
        if kitchen_state.start_task_execution(task['id'], 'chef_1'):
            print(f"✅ chef_1 开始烹饪: {task['params'][1]}")
            kitchen_state.complete_task_execution(task['id'], 'chef_1')
            print(f"✅ chef_1 完成烹饪: {task['params'][1]}")
    
    # 测试7：检查最后的交付任务是否解锁
    print(f"\n📋 测试7: 检查交付任务是否解锁")
    for agent_id in ['chef_1', 'chef_2', 'chef_3']:
        available_task = kitchen_state.get_next_available_task(agent_id)
        if available_task:
            print(f"  {agent_id}: {available_task['type']}({', '.join(map(str, available_task['params']))})")
            
            # 执行交付任务
            if kitchen_state.start_task_execution(available_task['id'], agent_id):
                print(f"✅ {agent_id} 开始交付: {available_task['params'][1]}")
                kitchen_state.complete_task_execution(available_task['id'], agent_id)
                print(f"✅ {agent_id} 完成交付: {available_task['params'][1]}")
            break
    
    # 测试8：检查是否所有任务完成
    print(f"\n📋 测试8: 检查最终状态")
    print(kitchen_state.get_task_queue_summary())
    
    if kitchen_state.is_all_tasks_completed():
        print("🎉 所有任务已完成！任务队列系统运行正常！")
    else:
        print("⚠️ 还有任务未完成")
    
    # 测试9：防重复机制测试
    print(f"\n📋 测试9: 测试防重复机制")
    print("尝试再次获取任务...")
    for agent_id in ['chef_1', 'chef_2', 'chef_3']:
        available_task = kitchen_state.get_next_available_task(agent_id)
        if available_task:
            print(f"  {agent_id}: {available_task['type']} (应该为空)")
        else:
            print(f"  {agent_id}: 无可用任务 ✅")

if __name__ == "__main__":
    test_task_queue_system()