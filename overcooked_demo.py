"""
CamelAI-Based Multi-Agent Overcooked Cooking Collaboration System
基于 CamelAI 的多智能体 Overcooked 烹饪协作系统

This demo showcases a simplified multi-agent cooking system using CamelAI's Workforce pattern.
演示基于 CamelAI Workforce 模式的简化多智能体烹饪系统。
"""

import os
import textwrap
from dotenv import load_dotenv
from camel.societies.workforce import Workforce
from camel.tasks import Task
from agents import make_order_manager, make_chef_team

# Load environment variables from .env file
load_dotenv()


def main():
    """
    主演示程序
    
    演示流程：
    1. 创建 Workforce 厨房团队
    2. 添加订单管理者和多个厨师
    3. 处理"制作2份西红柿炒蛋"的订单
    4. 展示团队协作过程
    5. 输出结果和性能指标
    """
    
    print("=" * 80)
    print("🍳 CamelAI 多智能体 Overcooked 烹饪协作系统演示")
    print("=" * 80)
    
    # 1. 创建 Workforce 厨房团队
    workforce = Workforce('Overcooked Kitchen Team')
    print("✅ 创建厨房团队成功")
    
    # 2. 创建各个智能体
    print("\n🤖 正在创建智能体团队...")
    
    # 创建订单管理者
    order_manager = make_order_manager()
    print("  - 订单管理者：负责分解客户订单")
    
    # 创建厨师团队
    chef_team = make_chef_team()
    print("  - Chef_1 (炒菜专家): 位置 (1,1) - 靠近灶台")
    print("  - Chef_2 (备菜专家): 位置 (1,5) - 靠近准备台") 
    print("  - Chef_3 (辅助料理): 位置 (8,5) - 靠近储藏区")
    
    # 3. 按顺序添加智能体到 Workforce
    print("\n🔗 正在组建协作团队...")
    
    workforce.add_single_agent_worker(
        '订单管理专家：负责解析客户订单，将自然语言需求分解为具体的烹饪任务序列，'
        '确定所需食材和工具，规划任务执行顺序',
        worker=order_manager,
    ).add_single_agent_worker(
        'Chef_1 (炒菜专家)：位置在厨房坐标(1,1)，靠近灶台区域，'
        '专长炒菜料理，负责热菜制作和炒制工作',
        worker=chef_team['chef_1'],
    ).add_single_agent_worker(
        'Chef_2 (备菜专家)：位置在厨房坐标(1,5)，靠近准备台，'
        '专长食材准备和预处理，负责切菜、调料准备等工作',
        worker=chef_team['chef_2'],
    ).add_single_agent_worker(
        'Chef_3 (辅助料理)：位置在厨房坐标(8,5)，靠近储藏区，'
        '专长辅助料理和收尾工作，负责取料、清洁和装盘等',
        worker=chef_team['chef_3'],
    )
    
    print("✅ 团队组建完成")
    
    # 4. 创建烹饪任务
    print("\n📋 创建烹饪任务...")
    
    order_content = "制作2份西红柿炒蛋"
    additional_info = {
        "customer_requirements": "客户要求：西红柿要出汁，鸡蛋要嫩滑，口味适中",
        "kitchen_layout": {
            "灶台区域": "(1,1) - (3,3)",
            "准备台": "(1,5) - (3,7)",
            "储藏区": "(8,5) - (10,7)",
            "清洗区": "(8,1) - (10,3)"
        },
        "available_ingredients": [
            "鸡蛋", "西红柿", "葱", "蒜", "盐", "糖", "生抽", "食用油"
        ]
    }
    
    task = Task(
        content=f"处理客户订单：{order_content}。"
               f"请订单管理者首先分析订单并制定详细的烹饪计划，"
               f"然后各位厨师根据自己的位置和专长，协作完成这道菜。"
               f"最终输出完整的制作过程和团队协作方案。",
        additional_info=additional_info,
        id="overcooked_task_001",
    )
    
    print(f"📝 任务内容：{order_content}")
    print("✅ 任务创建成功")
    
    # 5. 开始处理任务
    print("\n🚀 开始多智能体协作...")
    print("-" * 50)
    
    # 处理任务（这里会自动按顺序调用各个智能体）
    workforce.process_task(task)
    
    print("-" * 50)
    print("✅ 任务处理完成！")
    
    # 6. 显示结果
    print("\n📊 任务执行结果：")
    print("=" * 50)
    print(task.result)
    print("=" * 50)
    
    # 7. 显示团队协作日志（类似 hackathon_judges.py）
    print("\n📈 团队协作日志树：")
    print("-" * 80)
    workforce_log = workforce.get_workforce_log_tree()
    print(workforce_log)
    
    # 8. 显示性能指标
    print("\n📊 团队绩效指标：")
    print("-" * 80)
    kpis = workforce.get_workforce_kpis()
    for key, value in kpis.items():
        print(f"{key}: {value}")
    
    # 9. 保存详细日志
    log_file_path = "overcooked_cooking_logs.json"
    print(f"\n💾 保存详细日志到 {log_file_path}")
    workforce.dump_workforce_logs(log_file_path)
    print(f"✅ 日志已保存：{log_file_path}")
    
    print("\n" + "=" * 80)
    print("🎉 CamelAI 多智能体烹饪协作演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()