"""CamelAI-Based Multi-Agent Overcooked System - Final Main Program
基于CamelAI框架的多智能体Overcooked烹饪协作系统 - 最终主程序

集成了状态感知、物理机器人控制和工具包功能的完整系统
Integrated system with state awareness, physical robot control, and toolkit functionality
"""

import os
import textwrap
from dotenv import load_dotenv
from camel.societies.workforce import Workforce
from camel.tasks import Task

# 导入核心组件
from core import SharedKitchenState
from toio import ToioController, CookingToolkit
from agents import (
    make_order_manager, 
    make_state_aware_chef_team,
    make_toolkit_enabled_chef_team,
    get_agent_task_recommendation
)

# 加载环境变量
load_dotenv()


def demo_state_awareness():
    """演示状态感知功能"""
    print("=" * 80)
    print("🧠 状态感知演示：智能体查询厨房状态并选择任务")
    print("=" * 80)
    
    # 1. 创建共享状态空间
    kitchen_state = SharedKitchenState()
    print("✅ 创建共享厨房状态空间")
    print(kitchen_state.get_summary())
    
    # 2. 创建状态感知的厨师团队
    chef_team = make_state_aware_chef_team(kitchen_state)
    print("\n🤖 创建状态感知厨师团队:")
    for agent_id, agent in chef_team.items():
        print(f"  - {agent_id}: 位置 {agent.position}, 专长 {agent.specialization}")
    
    # 3. 演示每个厨师的任务推荐
    print("\n🎯 为每个厨师推荐最佳任务:")
    print("-" * 60)
    
    for agent_id, agent in chef_team.items():
        print(f"\n🔍 {agent_id} 的任务推荐:")
        recommendation = get_agent_task_recommendation(agent)
        
        # 让 agent 分析状态并选择任务
        response = agent.step(recommendation)
        print(f"💭 {agent_id} 的分析:")
        print(response.msg.content)
        print("-" * 40)
    
    return kitchen_state, chef_team


def demo_task_execution():
    """演示任务执行和状态更新"""
    print("\n" + "=" * 80)
    print("⚡ 任务执行演示：模拟实际的任务分配和状态更新")
    print("=" * 80)
    
    # 1. 创建状态空间和团队
    kitchen_state = SharedKitchenState()
    chef_team = make_state_aware_chef_team(kitchen_state)
    
    print("📋 初始状态:")
    print(kitchen_state.get_summary())
    
    # 2. 模拟任务分配过程
    print("\n🎲 模拟任务分配过程:")
    
    # 让 chef_2 (备菜专家) 获取并执行一个切菜任务
    available_tasks = kitchen_state.available_tasks
    if available_tasks:
        # 选择第一个切菜任务
        selected_task = None
        for task in available_tasks:
            if task['task'] == 'cut_tomato':
                selected_task = task
                break
        
        if selected_task:
            agent = chef_team['chef_2']  # 备菜专家
            print(f"\n🔄 {agent.agent_id} 尝试执行任务: {selected_task['task']}")
            
            # 分配任务
            success = kitchen_state.assign_task(selected_task, agent.agent_id)
            if success:
                print(f"✅ 任务分配成功!")
                
                # 更新 agent 位置（模拟移动到任务位置）
                kitchen_state.update_agent(agent.agent_id, selected_task['location'], selected_task['task'])
                
                print("\n📊 任务分配后的状态:")
                print(kitchen_state.get_summary())
                
                # 模拟任务完成
                print(f"\n⏳ 模拟 {agent.agent_id} 完成任务...")
                kitchen_state.complete_task(selected_task['task'], selected_task['dish_id'], agent.agent_id)
                
                print("\n📊 任务完成后的状态:")
                print(kitchen_state.get_summary())
            else:
                print(f"❌ 任务分配失败")
    
    return kitchen_state, chef_team


def demo_toolkit_integration():
    """演示工具包集成功能"""
    print("\n" + "=" * 80)
    print("🔧 工具包集成演示：Agents 使用物理机器人执行真实烹饪动作")
    print("=" * 80)
    
    # 1. 创建底层控制器和工具包
    print("🤖 初始化 Toio 控制器和烹饪工具包...")
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    kitchen_state = SharedKitchenState()
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    # 2. 创建具备工具包功能的厨师团队
    toolkit_chef_team = make_toolkit_enabled_chef_team(kitchen_state, cooking_toolkit)
    
    print("\n👥 创建具备物理控制能力的厨师团队:")
    for agent_id, agent in toolkit_chef_team.items():
        tools_count = len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 0
        print(f"  - {agent_id}: 位置 {agent.position}, 专长 {agent.specialization}, 可用工具: {tools_count}")
    
    # 3. 演示单个智能体使用工具包
    print("\n🎯 演示 chef_2 (备菜专家) 使用工具包执行烹饪任务:")
    chef = toolkit_chef_team['chef_2']
    
    instruction = """
    你好！请帮我完成制作西红柿炒蛋的准备工作：
    1. 首先检查你的机器人状态
    2. 拾取西红柿
    3. 切好西红柿
    4. 拾取鸡蛋
    
    请使用你的工具来完成这些物理操作。记住你的机器人ID是 chef_2。
    """
    
    print("💭 发送指令给智能体...")
    response = chef.step(instruction)
    
    print("\n🗣️ 智能体回应:")
    print(response.msg.content)
    
    return toio_controller, kitchen_state, cooking_toolkit, toolkit_chef_team


def demo_full_workflow():
    """演示完整的工作流程"""
    print("\n" + "=" * 80)
    print("🚀 完整工作流程演示：CamelAI Workforce + 状态感知 + 物理控制")
    print("=" * 80)
    
    # 1. 创建完整的控制栈
    print("🔧 初始化完整的控制栈...")
    toio_controller = ToioController(simulation_mode=True)
    toio_controller.connect()
    kitchen_state = SharedKitchenState()
    cooking_toolkit = CookingToolkit(toio_controller, kitchen_state)
    
    # 2. 创建 Workforce 和具备工具包的 agents
    workforce = Workforce('Toolkit-Enabled Kitchen Team')
    order_manager = make_order_manager()
    
    # 使用具备工具包功能的厨师团队
    chef_team = make_toolkit_enabled_chef_team(kitchen_state, cooking_toolkit)
    
    print("✅ 创建了具备物理控制能力的完整系统")
    
    # 3. 添加 agents 到 workforce
    workforce.add_single_agent_worker(
        '订单管理专家：分析订单需求，制定烹饪计划',
        worker=order_manager,
    ).add_single_agent_worker(
        'Chef_1 (物理控制炒菜专家)：使用toio机器人执行炒菜任务，具备pick_x/slice_x/cook_x/serve_x能力',
        worker=chef_team['chef_1'],
    ).add_single_agent_worker(
        'Chef_2 (物理控制备菜专家)：使用toio机器人执行备菜任务，具备pick_x/slice_x/cook_x/serve_x能力',
        worker=chef_team['chef_2'],
    ).add_single_agent_worker(
        'Chef_3 (物理控制辅助料理)：使用toio机器人执行辅助任务，具备pick_x/slice_x/cook_x/serve_x能力',
        worker=chef_team['chef_3'],
    )
    
    # 4. 创建包含物理控制指令的任务
    kitchen_layout = cooking_toolkit.get_kitchen_layout()
    task_content = f"""
    处理客户订单：制作2份西红柿炒蛋
    
    当前厨房状态信息：
    {kitchen_state.get_summary()}
    
    厨房布局信息：
    - 储藏区 (8,5)：存放所有原料 (tomato, eggs)
    - 准备台 (1,5)：配备切菜板，用于切割
    - 灶台区 (1,1)：用于烹饪
    - 装盘台 (3,3)：最终装盘
    - 交付窗口 (5,1)：交付给顾客
    
    请各位智能体协作完成订单，现在你们具备了真实的物理控制能力：
    
    1. 订单管理专家：分析订单和当前状态，制定详细的物理执行计划
    
    2. 各位厨师：使用你们的工具包执行真实的烹饪动作：
       - pick_x(robot_id, ingredient) - 拾取原料
       - slice_x(robot_id, ingredient) - 切割原料
       - cook_x(robot_id, dish) - 烹饪菜品
       - serve_x(robot_id, dish) - 交付菜品
    
    你们的机器人ID分别是：chef_1, chef_2, chef_3
    
    请根据位置优势和专长分工合作：
    - chef_1 (炒菜专家，位置1,1)：负责烹饪环节
    - chef_2 (备菜专家，位置1,5)：负责原料准备和切割
    - chef_3 (辅助料理，位置8,5)：负责原料拾取和最终交付
    
    重要：请实际使用工具执行物理动作，不要只是描述！
    """
    
    task = Task(
        content=task_content,
        additional_info={
            "kitchen_state": kitchen_state.get_state(),
            "state_summary": kitchen_state.get_summary()
        },
        id="state_aware_cooking_001",
    )
    
    # 5. 执行任务
    print("🚀 开始物理控制的多智能体协作...")
    print("💡 Agents 现在可以控制真实的 toio 机器人执行烹饪动作！")
    workforce.process_task(task)
    
    # 6. 显示结果
    print("\n📊 最终结果:")
    print("=" * 50)
    print(task.result)
    print("=" * 50)
    
    # 7. 显示最终状态
    print("\n📊 最终厨房状态:")
    print(kitchen_state.get_summary())
    
    # 8. 显示最终机器人状态
    print("\n🤖 最终机器人状态:")
    for robot_id in ['chef_1', 'chef_2', 'chef_3']:
        status = toio_controller.get_robot_status(robot_id)
        if status:
            print(f"  {robot_id}: 位置 {status['position']}, 状态 {status['status']}")
    
    # 9. 保存状态
    kitchen_state.save_state("final_kitchen_state.json")
    
    return workforce, kitchen_state, toio_controller, cooking_toolkit


def main():
    """主演示程序"""
    print("🍳 CamelAI 多智能体 Overcooked 系统演示")
    print("=" * 80)
    
    try:
        # 演示1: 状态感知功能
        kitchen_state1, chef_team1 = demo_state_awareness()
        
        # 演示2: 任务执行和状态更新
        kitchen_state2, chef_team2 = demo_task_execution()
        
        # 演示3: 工具包集成
        toio_controller, kitchen_state_toolkit, cooking_toolkit, toolkit_team = demo_toolkit_integration()
        
        # 演示4: 完整工作流程（最终演示）
        workforce, kitchen_state3, final_toio, final_toolkit = demo_full_workflow()
        
        print("\n" + "=" * 80)
        print("🎉 CamelAI 多智能体 Overcooked 系统演示完成！")
        print("✅ 状态感知功能：agents 能够查询和分析厨房状态")
        print("✅ 智能任务选择：agents 根据状态信息选择最优任务")
        print("✅ 状态同步更新：任务执行后状态实时更新")
        print("✅ 物理机器人控制：toio机器人执行真实烹饪动作")
        print("✅ 工具包集成：agents 可调用 pick_x/slice_x/cook_x/serve_x")
        print("✅ 完整协作流程：从订单分析到物理执行的全流程")
        print("✅ 多智能体协调：避免冲突，提高协作效率")
        print("=" * 80)
        print("🚀 系统已准备好进行真实 toio 机器人集成！")
        print("💡 只需将 ToioController 的 simulation_mode 设为 False 即可")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()