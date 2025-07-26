"""
Toio 集成演示 - 模拟 toio 机器人与状态空间的集成

演示 toio 机器人如何通过移动到特定位置来触发任务完成和状态更新
"""

import time
import asyncio
from core import SharedKitchenState


def demo_toio_position_callbacks():
    """演示 toio 位置回调机制"""
    print("=" * 80)
    print("🤖 Toio 位置回调演示")
    print("=" * 80)
    
    # 创建状态空间
    kitchen_state = SharedKitchenState()
    
    print("📋 初始状态:")
    print(kitchen_state.get_summary())
    
    # 模拟设置 toio 任务执行
    available_task = kitchen_state.available_tasks[0]  # 获取第一个可用任务
    agent_id = "chef_2"
    
    print(f"\n🚀 为 {agent_id} 设置 toio 任务:")
    print(f"  任务: {available_task['task']}")
    print(f"  目标位置: {available_task['location']}")
    
    success = kitchen_state.setup_toio_task_execution(agent_id, available_task)
    
    if success:
        print("\n📊 任务设置后的状态:")
        print(kitchen_state.get_summary())
        
        print("\n🗺️ Toio 导航信息:")
        nav_info = kitchen_state.get_toio_navigation_info(agent_id)
        if nav_info:
            print(f"  当前位置: {nav_info['current_position']}")
            print(f"  目标位置: {nav_info['target_position']}")
            print(f"  路径: {nav_info['path']}")
            print(f"  预计时间: {nav_info['estimated_time']} 秒")
        
        # 模拟 toio 移动过程
        print(f"\n🏃 模拟 {agent_id} 移动到目标位置...")
        current_pos = kitchen_state.agents[agent_id]['position']
        target_pos = available_task['location']
        
        # 模拟移动过程
        path = kitchen_state._calculate_simple_path(current_pos, target_pos)
        for i, pos in enumerate(path):
            print(f"  步骤 {i+1}: 移动到 {pos}")
            # 模拟每步移动
            task_completed = kitchen_state.on_toio_position_update(agent_id, pos)
            
            if task_completed:
                print("✅ 任务自动完成!")
                break
            
            time.sleep(0.5)  # 模拟移动时间
        
        print("\n📊 任务完成后的状态:")
        print(kitchen_state.get_summary())
    
    return kitchen_state


def demo_toio_status_monitoring():
    """演示 toio 状态监控"""
    print("\n" + "=" * 80)
    print("📊 Toio 状态监控演示")
    print("=" * 80)
    
    kitchen_state = SharedKitchenState()
    
    # 为多个 agent 设置任务
    tasks = kitchen_state.available_tasks[:3]  # 取前3个任务
    agents = ["chef_1", "chef_2", "chef_3"]
    
    print("🚀 为多个 toio 机器人设置任务:")
    for i, (agent_id, task) in enumerate(zip(agents, tasks)):
        if kitchen_state.setup_toio_task_execution(agent_id, task):
            print(f"  ✅ {agent_id}: {task['task']} @ {task['location']}")
        else:
            print(f"  ❌ {agent_id}: 任务设置失败")
    
    print(f"\n{kitchen_state.get_toio_status_summary()}")
    
    # 模拟部分 agent 完成任务
    print("\n🏃 模拟部分机器人完成任务...")
    
    # chef_2 完成任务
    target_pos = tasks[1]['location']
    kitchen_state.on_toio_position_update("chef_2", target_pos)
    
    print(f"\n{kitchen_state.get_toio_status_summary()}")
    
    return kitchen_state


def demo_toio_mqtt_simulation():
    """演示 toio MQTT 通信模拟"""
    print("\n" + "=" * 80)
    print("📡 Toio MQTT 通信模拟")
    print("=" * 80)
    
    kitchen_state = SharedKitchenState()
    
    # 模拟 MQTT 消息处理
    def simulate_mqtt_position_message(agent_id: str, position: tuple):
        """模拟接收到 MQTT 位置消息"""
        print(f"📡 接收 MQTT 消息: {agent_id} @ {position}")
        
        # 处理位置更新
        task_completed = kitchen_state.on_toio_position_update(agent_id, position)
        
        if task_completed:
            print(f"🎯 {agent_id} 任务完成!")
        
        return task_completed
    
    # 设置任务
    task = kitchen_state.available_tasks[0]
    agent_id = "chef_1"
    kitchen_state.setup_toio_task_execution(agent_id, task)
    
    print(f"📋 为 {agent_id} 设置任务: {task['task']} @ {task['location']}")
    print(f"🎯 目标位置: {task['location']}")
    
    # 模拟接收 MQTT 位置消息
    print(f"\n📡 模拟 MQTT 位置消息流:")
    
    # 模拟移动路径上的位置消息
    current_pos = kitchen_state.agents[agent_id]['position']
    target_pos = task['location']
    path = kitchen_state._calculate_simple_path(current_pos, target_pos)
    
    for i, pos in enumerate(path):
        print(f"\n--- MQTT 消息 {i+1} ---")
        completed = simulate_mqtt_position_message(agent_id, pos)
        
        if completed:
            break
        
        time.sleep(0.3)  # 模拟消息间隔
    
    print(f"\n📊 最终状态:")
    print(kitchen_state.get_summary())
    
    return kitchen_state


async def demo_async_toio_control():
    """演示异步 toio 控制"""
    print("\n" + "=" * 80)
    print("⚡ 异步 Toio 控制演示")
    print("=" * 80)
    
    kitchen_state = SharedKitchenState()
    
    async def simulate_toio_movement(agent_id: str, task_info: dict):
        """模拟异步 toio 移动"""
        print(f"🤖 {agent_id} 开始异步移动到 {task_info['location']}")
        
        current_pos = kitchen_state.agents[agent_id]['position']
        target_pos = task_info['location']
        path = kitchen_state._calculate_simple_path(current_pos, target_pos)
        
        for i, pos in enumerate(path):
            await asyncio.sleep(0.5)  # 模拟移动时间
            print(f"  {agent_id}: 步骤 {i+1}/{len(path)} -> {pos}")
            
            task_completed = kitchen_state.on_toio_position_update(agent_id, pos)
            if task_completed:
                print(f"✅ {agent_id} 任务完成!")
                return True
        
        return False
    
    # 为多个 agent 设置任务并并行执行
    tasks = kitchen_state.available_tasks[:2]
    agents = ["chef_1", "chef_2"]
    
    print("🚀 设置并行任务:")
    movement_tasks = []
    
    for agent_id, task in zip(agents, tasks):
        if kitchen_state.setup_toio_task_execution(agent_id, task):
            print(f"  ✅ {agent_id}: {task['task']} @ {task['location']}")
            movement_tasks.append(simulate_toio_movement(agent_id, task))
        else:
            print(f"  ❌ {agent_id}: 任务设置失败")
    
    if movement_tasks:
        print(f"\n🏃 启动 {len(movement_tasks)} 个并行移动任务...")
        results = await asyncio.gather(*movement_tasks)
        print(f"📊 完成情况: {sum(results)}/{len(results)} 个任务成功完成")
    
    print(f"\n📊 最终状态:")
    print(kitchen_state.get_summary())
    
    return kitchen_state


def main():
    """主演示程序"""
    print("🤖 Toio 集成演示程序")
    print("=" * 80)
    
    try:
        # 演示1: 位置回调机制
        kitchen_state1 = demo_toio_position_callbacks()
        
        # 演示2: 状态监控
        kitchen_state2 = demo_toio_status_monitoring()
        
        # 演示3: MQTT 通信模拟
        kitchen_state3 = demo_toio_mqtt_simulation()
        
        # 演示4: 异步控制
        print("\n🔄 启动异步演示...")
        asyncio.run(demo_async_toio_control())
        
        print("\n" + "=" * 80)
        print("🎉 Toio 集成演示完成!")
        print("✅ 位置回调机制：toio 到达目标位置自动触发任务完成")
        print("✅ 状态监控：实时跟踪多个 toio 机器人状态")
        print("✅ MQTT 通信：模拟真实的消息处理流程")
        print("✅ 异步控制：支持多个 toio 机器人并行操作")
        print("✅ 路径规划：简单的导航和路径计算")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()