"""
Toio 烹饪工具包演示程序

演示 agents 如何使用 toio 机器人执行真实的烹饪动作：
pick_x, slice_x, cook_x, serve_x
"""

import os
import asyncio
from dotenv import load_dotenv

# 导入核心组件
from core import SharedKitchenState
from toio import ToioController, CookingToolkit
from agents import make_toolkit_enabled_chef_team

# 加载环境变量
load_dotenv()


def demo_basic_toolkit_functions():
    """演示基本的工具包功能"""
    print("=" * 80)
    print("🔧 基本工具包功能演示")
    print("=" * 80)
    
    # 1. 创建 toio 控制器（模拟模式）
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    
    # 2. 创建状态空间
    kitchen_state = SharedKitchenState()
    
    # 3. 创建烹饪工具包
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    print("✅ 所有组件创建完成")
    print(f"📊 初始机器人状态:")
    for robot_id, status in toio_controller.get_all_robots_status().items():
        print(f"  {robot_id}: {status}")
    
    # 4. 测试各种烹饪动作
    robot_id = "chef_1"
    
    print(f"\n🎬 开始 {robot_id} 的烹饪动作演示:")
    print("-" * 60)
    
    # 测试拾取原料
    print("\n1️⃣ 测试拾取原料:")
    result1 = cooking_toolkit.pick_x(robot_id, "tomato")
    print(f"结果: {result1}")
    
    # 测试切割原料
    print("\n2️⃣ 测试切割原料:")
    result2 = cooking_toolkit.slice_x(robot_id, "tomato")
    print(f"结果: {result2}")
    
    # 测试烹饪菜品
    print("\n3️⃣ 测试烹饪菜品:")
    result3 = cooking_toolkit.cook_x(robot_id, "tomato_egg")
    print(f"结果: {result3}")
    
    # 测试交付菜品
    print("\n4️⃣ 测试交付菜品:")
    result4 = cooking_toolkit.serve_x(robot_id, "tomato_egg")
    print(f"结果: {result4}")
    
    # 检查最终状态
    print(f"\n📊 最终机器人状态:")
    final_status = toio_controller.get_robot_status(robot_id)
    print(f"  {robot_id}: {final_status}")
    
    # 获取厨房布局
    print(f"\n🏠 厨房布局信息:")
    layout = cooking_toolkit.get_kitchen_layout()
    print(f"  原料位置: {layout['ingredient_positions']}")
    print(f"  工具位置: {layout['tool_positions']}")
    
    return toio_controller, kitchen_state, cooking_toolkit


def demo_cooking_sequence():
    """演示完整的烹饪序列"""
    print("\n" + "=" * 80)
    print("🍳 完整烹饪序列演示")
    print("=" * 80)
    
    # 创建组件
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    kitchen_state = SharedKitchenState()
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    # 定义烹饪序列：制作西红柿炒蛋
    cooking_sequence = [
        {"action": "pick", "target": "tomato"},
        {"action": "slice", "target": "tomato"},
        {"action": "pick", "target": "eggs"},
        {"action": "cook", "target": "tomato_egg"},
        {"action": "serve", "target": "tomato_egg"}
    ]
    
    print("🎬 执行完整烹饪序列: 制作西红柿炒蛋")
    print(f"📋 序列包含 {len(cooking_sequence)} 个步骤")
    
    # 执行序列
    result = cooking_toolkit.execute_cooking_sequence("chef_2", cooking_sequence)
    
    print(f"\n📊 序列执行结果:")
    print(f"  总步骤: {result['total_actions']}")
    print(f"  已完成: {result['completed_actions']}")
    print(f"  成功率: {result['completed_actions']/result['total_actions']*100:.1f}%")
    print(f"  整体成功: {'✅' if result['success'] else '❌'}")
    
    return toio_controller, kitchen_state, cooking_toolkit


def demo_agent_with_tools():
    """演示具备工具包的智能体"""
    print("\n" + "=" * 80)
    print("🤖 智能体工具包集成演示")
    print("=" * 80)
    
    # 创建组件
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    kitchen_state = SharedKitchenState()
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    # 创建具备工具包的厨师团队
    chef_team = make_toolkit_enabled_chef_team(kitchen_state, cooking_toolkit)
    
    print("👥 创建具备工具包功能的厨师团队:")
    for agent_id, agent in chef_team.items():
        tools_count = len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 0
        print(f"  {agent_id}: {agent.specialization}, 可用工具数: {tools_count}")
    
    # 让一个智能体执行烹饪任务
    chef = chef_team['chef_2']  # 备菜专家
    
    print(f"\n🎯 让 {chef.agent_id} (备菜专家) 执行切菜任务:")
    
    # 给智能体一个简单的切菜指令
    instruction = """
    你好！请帮我完成以下任务：
    1. 首先检查你的机器人状态
    2. 然后拾取西红柿
    3. 最后切好西红柿
    
    请使用你的工具来完成这些操作。
    """
    
    print("💭 发送指令给智能体...")
    response = chef.step(instruction)
    
    print("🗣️ 智能体回应:")
    print(response.msg.content)
    
    print(f"\n📊 任务执行后的机器人状态:")
    final_status = toio_controller.get_robot_status(chef.agent_id)
    print(f"  {chef.agent_id}: {final_status}")
    
    return chef_team, toio_controller, kitchen_state, cooking_toolkit


def demo_multi_agent_coordination():
    """演示多智能体协调"""
    print("\n" + "=" * 80)
    print("👥 多智能体协调演示")
    print("=" * 80)
    
    # 创建组件
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    kitchen_state = SharedKitchenState()
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    # 创建厨师团队
    chef_team = make_toolkit_enabled_chef_team(kitchen_state, cooking_toolkit)
    
    print("🎯 多智能体协作任务：同时制作2份西红柿炒蛋")
    
    # 任务分配
    tasks = {
        'chef_1': "你是炒菜专家，请负责烹饪工作。先检查状态，然后烹饪西红柿炒蛋。",
        'chef_2': "你是备菜专家，请负责准备工作。先拾取西红柿，然后切好西红柿。",
        'chef_3': "你是辅助料理，请负责最后的交付。检查状态后交付制作好的西红柿炒蛋。"
    }
    
    print("\n📋 任务分配:")
    for agent_id, task in tasks.items():
        agent = chef_team[agent_id]
        print(f"\n🎯 {agent_id} ({agent.specialization}):")
        print(f"  任务: {task}")
        
        print(f"  执行中...")
        response = agent.step(task)
        
        print(f"  回应: {response.msg.content[:100]}...")  # 只显示前100字符
    
    print(f"\n📊 所有智能体执行完毕后的状态:")
    for robot_id in ['chef_1', 'chef_2', 'chef_3']:
        status = toio_controller.get_robot_status(robot_id)
        print(f"  {robot_id}: 位置 {status['position']}, 状态 {status['status']}")
    
    return chef_team, toio_controller, kitchen_state, cooking_toolkit


async def demo_async_operations():
    """演示异步操作"""
    print("\n" + "=" * 80)
    print("⚡ 异步操作演示")
    print("=" * 80)
    
    # 创建组件
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    kitchen_state = SharedKitchenState()
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    print("🚀 同时执行多个异步烹饪动作:")
    
    # 定义异步任务
    async def async_cooking_task(robot_id: str, actions: list):
        print(f"🤖 {robot_id} 开始异步烹饪任务")
        for action in actions:
            if action['type'] == 'pick':
                result = cooking_toolkit.pick_x(robot_id, action['target'])
            elif action['type'] == 'slice':
                result = cooking_toolkit.slice_x(robot_id, action['target'])
            elif action['type'] == 'cook':
                result = cooking_toolkit.cook_x(robot_id, action['target'])
            elif action['type'] == 'serve':
                result = cooking_toolkit.serve_x(robot_id, action['target'])
            
            await asyncio.sleep(0.5)  # 模拟动作间隔
            print(f"  {robot_id}: {action['type']} {action['target']} - {'✅' if result['success'] else '❌'}")
        
        print(f"✅ {robot_id} 异步任务完成")
        return robot_id
    
    # 创建并行任务
    tasks = [
        async_cooking_task("chef_1", [
            {"type": "pick", "target": "eggs"},
            {"type": "cook", "target": "tomato_egg"}
        ]),
        async_cooking_task("chef_2", [
            {"type": "pick", "target": "tomato"},
            {"type": "slice", "target": "tomato"}
        ]),
        async_cooking_task("chef_3", [
            {"type": "serve", "target": "tomato_egg"}
        ])
    ]
    
    # 并行执行
    print("⏱️ 开始并行执行...")
    results = await asyncio.gather(*tasks)
    print(f"🎉 所有异步任务完成: {results}")
    
    return toio_controller, kitchen_state, cooking_toolkit


def main():
    """主演示程序"""
    print("🤖 Toio 烹饪工具包完整演示")
    print("=" * 80)
    print("本演示将展示：")
    print("1. 基本工具包功能 (pick_x, slice_x, cook_x, serve_x)")
    print("2. 完整烹饪序列执行")
    print("3. 智能体工具集成")
    print("4. 多智能体协调")
    print("5. 异步操作")
    print("=" * 80)
    
    try:
        # 演示1: 基本功能
        toio1, state1, toolkit1 = demo_basic_toolkit_functions()
        
        # 演示2: 烹饪序列
        toio2, state2, toolkit2 = demo_cooking_sequence()
        
        # 演示3: 智能体集成
        team3, toio3, state3, toolkit3 = demo_agent_with_tools()
        
        # 演示4: 多智能体协调
        team4, toio4, state4, toolkit4 = demo_multi_agent_coordination()
        
        # 演示5: 异步操作
        print("\n🔄 启动异步演示...")
        asyncio.run(demo_async_operations())
        
        print("\n" + "=" * 80)
        print("🎉 所有演示完成！")
        print("✅ 底层 toio 控制：move_to, play_sound, stop")
        print("✅ 高级烹饪动作：pick_x, slice_x, cook_x, serve_x")  
        print("✅ 智能体工具集成：agents 可以调用物理动作")
        print("✅ 完整烹饪流程：从拾取到交付的全过程")
        print("✅ 多机器人协调：并行执行不同任务")
        print("✅ 异步操作支持：提高执行效率")
        print("=" * 80)
        print("🚀 系统已准备好进行真实 toio 机器人集成！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()