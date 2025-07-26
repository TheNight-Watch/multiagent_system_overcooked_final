──────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
│ │ CamelAI-Based Multi-Agent Overcooked System - MVP Development Plan                                   │ │
│ │                                                                                                      │ │
│ │ 项目概述                                                                                             │ │
│ │                                                                                                      │ │
│ │ 基于CamelAI框架重新构建一个简化的多智能体Overcooked烹饪协作系统，
专注于最小可行产品(MVP)             │ │
│ │ camel框架地址：https://github.com/camel-ai/camel                                                                   │ │
│                                     │ │
│ │                                                                                                      │ │
│ │ MVP架构设计                                                                                          │ │
│ │                                                                                                      │ │
│ │ 核心设计原则                                                                                         │ │
│ │                                                                                                      │ │
│ │ - 简单性第一: 最小化组件数量和交互复杂度                                                             │ │
│ │ - CamelAI原生: 完全基于CamelAI的Society和Agent模式                                                   │ │
│ │ - 状态驱动: 单一真实来源的状态空间                                                                   │ │
│ │ - 步进式执行: 明确的回合制执行模型                                                                   │ │
│ │                                                                                                      │ │
│ │ 系统组件架构                                                                                         │ │
│ │                                                                                                      │ │
│ │ CamelAI Society                                                                                      │ │
│ │ ├── OrderManager (订单管理者)                                                                        │ │
│ │ ├── CookingAgent_1 (烹饪智能体1)                                                                     │ │
│ │ ├── CookingAgent_2 (烹饪智能体2)                                                                     │ │
│ │ ├── CookingAgent_3 (烹饪智能体3)                                                                     │ │
│ │ └── SharedKitchenState (共享厨房状态)                                                                │ │
│ │                                                                                                      │ │
│ │ 实现计划                                                                                             │ │
│ │                                                                                                      │ │
│ │ Phase 1: CamelAI基础框架 (2-3天)                                                                     │ │
│ │                                                                                                      │ │
│ │ 1.1 核心状态空间 (kitchen_state.py)                                                                  │ │
│ │                                                                                                      │ │
│ │ class SharedKitchenState:                                                                            │ │
│ │     """CamelAI Society共享的厨房状态"""                                                              │ │
│ │     def __init__(self):                                                                              │ │
│ │         self.current_step = 0                                                                        │ │
│ │         self.ingredients = {}  # 原料状态                                                            │ │
│ │         self.dishes = {}       # 菜品制作状态                                                        │ │
│ │         self.agents = {}       # Agent位置和状态                                                     │ │
│ │         self.tools = {}        # 工具占用状态                                                        │ │
│ │         self.available_tasks = []  # 当前可用任务列表                                                │ │
│ │                                                                                                      │ │
│ │ 1.2 CamelAI Agent基础类 (base_agent.py)                                                              │ │
│ │                                                                                                      │ │
│ │ from camel.agents import ChatAgent                                                                   │ │
│ │ from camel.workforce import                                                  │ │
│ │                                                                                                      │ │
│ │ class KitchenAgent(ChatAgent):                                                                       │ │
│ │     """基于CamelAI的厨房智能体基类"""                                                                │ │
│ │     def __init__(self, role_name, position, kitchen_state):                                          │ │
│ │         self.position = position                                                                     │ │
│ │         self.kitchen_state = kitchen_state                                                           │ │
│ │         super().__init__(...)                                                                        │ │
│ │                                                                                                                                                                              │ │
│ │                                                                                           智能体实现 (3-4天)                                                                          │ │
│ │                                                                                                      │ │
│ │ 2.1 订单管理者 (order_manager.py)                                                                    │ │
│ │                                                                                                      │ │
│ │ class OrderManager(KitchenAgent):                                                                    │ │
│ │     """专门负责订单分解的智能体"""                                                                   │ │
│ │     def __init__(self):                                                                              │ │
│ │         super().__init__(                                                                            │ │
│ │             role_name="Order Manager",                                                               │ │
│ │             system_message="你是订单管理专家，负责将自然语言订单分解为具体的烹饪任务序列..."         │ │
│ │         )                                                                                            │ │
│ │                                                                                                      │ │
│ │     def process_order(self, order_text):                                                             │ │
│ │         """使用CamelAI处理订单"""                                                                    │ │
│ │         response = self.step(f"分解订单: {order_text}")                                              │ │
│ │         return self.parse_tasks(response)                                                            │ │
│ │                                                                                                      │ │
│ │ 2.2 烹饪智能体 (cooking_agent.py)                                                                    │ │
│ │                                                                                                      │ │
│ │ class CookingAgent(KitchenAgent):                                                                    │ │
│ │     """位置感知的烹饪智能体"""                                                                       │ │
│ │     def __init__(self, agent_id, position):                                                          │ │
│ │         super().__init__(                                                                            │ │
│ │             role_name=f"Cooking Agent {agent_id}",                                                   │ │
│ │             position=position,                                                                       │ │
│ │             system_message=f"你是位置在{position}的烹饪专家，根据距离和效率选择最优任务..."          │ │
│ │         )                                                                                            │ │
│ │                                                                                                      │ │
│ │     def select_task(self, available_tasks):                                                          │ │
│ │         """基于位置选择最优任务"""                                                                   │ │
│ │         context = self.build_position_context(available_tasks)                                       │ │
│ │         response = self.step(context)                                                                │ │
│ │         return self.parse_task_selection(response)                                                   │ │
│ │                                                                                                      │ │
│ │ Phase 3: 冲突解决和状态同步 (2-3天)                                                                  │ │
│ │                                                                                                      │ │
│ │ 3.1 顺序决策机制                                                                                     │ │
│ │                                                                                                      │ │
│ │ class SequentialDecisionManager:                                                                     │ │
│ │     """顺序决策管理器，解决并发冲突"""                                                               │ │
│ │     def __init__(self, agents):                                                                      │ │
│ │         self.agents = sorted(agents, key=lambda x: x.agent_id)                                       │ │
│ │                                                                                                      │ │
│ │     def make_decisions(self, kitchen_state):                                                         │ │
│ │         """按固定顺序进行决策"""                                                                     │ │
│ │         decisions = {}                                                                               │ │
│ │         available_tasks = kitchen_state.get_available_tasks()                                        │ │
│ │                                                                                                      │ │
│ │         for agent in self.agents:                                                                    │ │
│ │             if agent.is_available():                                                                 │ │
│ │                 task = agent.select_task(available_tasks)                                            │ │
│ │                 if task:                                                                             │ │
│ │                     decisions[agent.agent_id] = task                                                 │ │
│ │                     available_tasks.remove(task)  # 立即移除避免冲突                                 │ │
│ │                                                                                                      │ │
│ │         return decisions                                                                             │ │
│ │                                                                                                      │ │
│ │ 3.2 状态同步机制                                                                                     │ │
│ │                                                                                                      │ │
│ │ class StateSync:                                                                                     │ │
│ │     """简化的状态同步"""                                                                             │ │
│ │     @staticmethod                                                                                    │ │
│ │     def update_after_decisions(kitchen_state, decisions):                                            │ │
│ │         """决策后更新状态"""                                                                         │ │
│ │         for agent_id, task in decisions.items():                                                     │ │
│ │             kitchen_state.assign_task(agent_id, task)                                                │ │
│ │                                                                                                      │ │
│ │     @staticmethod                                                                                    │ │
│ │     def update_after_execution(kitchen_state):                                                       │ │
│ │         """执行后更新状态"""                                                                         │ │
│ │         kitchen_state.advance_step()                                                                 │ │
│ │         kitchen_state.update_task_progress()                                                         │ │
│ │                                                                                                      │ │
│ │ Phase 4: 集成和测试 (2-3天)                                                                          │ │
│ │                                                                                                      │ │
│ │ 4.1 主执行循环 (main_demo.py)                                                                        │ │
│ │                                                                                                      │ │
│ │ async def run_cooking_demo():                                                                        │ │
│ │     """主演示程序"""                                                                                 │ │
│ │     # 1. 初始化CamelAI Society                                                                       │ │
│ │     society = KitchenSociety()                                                                       │ │
│ │                                                                                                      │ │
│ │     # 2. 创建Agents                                                                                  │ │
│ │     order_manager = OrderManager()                                                                   │ │
│ │     agents = [                                                                                       │ │
│ │         CookingAgent("chef_1", (1, 1)),                                                              │ │
│ │         CookingAgent("chef_2", (1, 5)),                                                              │ │
│ │         CookingAgent("chef_3", (8, 5))                                                               │ │
│ │     ]                                                                                                │ │
│ │                                                                                                      │ │
│ │     # 3. 处理订单                                                                                    │ │
│ │     tasks = order_manager.process_order("制作2份西红柿炒蛋")                                         │ │
│ │     society.kitchen_state.add_tasks(tasks)                                                           │ │
│ │                                                                                                      │ │
│ │     # 4. 执行协作循环                                                                                │ │
│ │     for step in range(10):                                                                           │ │
│ │         print(f"=== Step {step} ===")                                                                │ │
│ │         decisions = society.make_step_decisions()                                                    │ │
│ │         society.execute_decisions(decisions)                                                         │ │
│ │         society.display_state()                                                                      │ │
│ │                                                                                                      │ │
│ │         if society.kitchen_state.all_completed():                                                    │ │
│ │             break                                                                                    │ │
│ │                                                                                                      │ │
│ │ Phase 5: 物理集成接口 (3-4天)                                                                        │ │
│ │                                                                                                      │ │
│ │ 5.1 toio接口桥接 (toio_bridge.py)                                                                    │ │
│ │                                                                                                      │ │
│ │ class ToioBridge:                                                                                    │ │
│ │     """连接CamelAI系统和toio物理控制"""                                                              │ │
│ │     def __init__(self):                                                                              │ │
│ │         self.toio_controllers = {}  # 由嵌入式工程师提供                                             │ │
│ │                                                                                                      │ │
│ │     def execute_physical_action(self, agent_id, action, target_position):                            │ │
│ │         """执行物理动作"""                                                                           │ │
│ │         controller = self.toio_controllers[agent_id]                                                 │ │
│ │         if action.startswith("go_to"):                                                               │ │
│ │             controller.move_to(target_position)                                                      │ │
│ │         elif action.startswith("cook"):                                                              │ │
│ │             controller.perform_cooking_action(action)                                                │ │
│ │                                                                                                      │ │
│ │ 5.2 位置同步 (position_sync.py)                                                                      │ │
│ │                                                                                                      │ │
│ │ class PositionSync:                                                                                  │ │
│ │     """通过MQTT同步toio位置"""                                                                       │ │
│ │     def __init__(self, mqtt_client):                                                                 │ │
│ │         self.mqtt_client = mqtt_client                                                               │ │
│ │         self.agent_positions = {}                                                                    │ │
│ │                                                                                                      │ │
│ │     def update_positions(self):                                                                      │ │
│ │         """每个step更新一次位置"""                                                                   │ │
│ │         for agent_id in self.agent_positions:                                                        │ │
│ │             real_pos = self.mqtt_client.get_position(agent_id)                                       │ │
│ │             self.agent_positions[agent_id] = real_pos                                                │ │
│ │                                                                                                      │ │
│ │ 技术栈和依赖                                                                                         │ │
│ │                                                                                                      │ │
│ │ 核心依赖                                                                                             │ │
│ │                                                                                                      │ │
│ │ # requirements.txt                                                                                   │ │
│ │ camel-ai>=0.1.0           # 核心多智能体框架                                                         │ │
│ │ openai>=1.0.0             # LLM支持                                                                  │ │
│ │ paho-mqtt>=1.6.0          # MQTT通信（与toio系统）                                                   │ │
│ │ asyncio                   # 异步执行                                                                 │ │
│ │ pydantic>=2.0.0           # 数据验证                                                                 │ │
│ │ python-dotenv>=1.0.0      # 环境变量管理                                                             │ │
│ │                                                                                                      │ │
│ │ 文件结构                                                                                             │ │
│ │                                                                                                      │ │
│ │ overcooked_camel/                                                                                    │ │
│ │ ├── main_demo.py              # 主演示程序                                                           │ │
│ │ ├── requirements.txt          # 依赖管理                                                             │ │
│ │ ├── .env                      # 环境配置                                                             │ │
│ │ ├── agents/                                                                                          │ │
│ │ │   ├── __init__.py                                                                                  │ │
│ │ │   ├── base_agent.py         # CamelAI Agent基类                                                    │ │
│ │ │   ├── order_manager.py      # 订单管理者                                                           │ │
│ │ │   └── cooking_agent.py      # 烹饪智能体                                                           │ │
│ │ ├── core/                                                                                            │ │
│ │ │   ├── __init__.py                                                                                  │ │
│ │ │   ├── kitchen_state.py      # 共享状态                                                             │ │
│ │ │   ├── kitchen_society.py    # CamelAI Society                                                      │ │
│ │ │   ├── decision_manager.py   # 顺序决策                                                             │ │
│ │ │   └── task_library.py       # 任务定义                                                             │ │
│ │ ├── physical/                                                                                        │ │
│ │ │   ├── __init__.py                                                                                  │ │
│ │ │   ├── toio_bridge.py        # toio接口桥接                                                         │ │
│ │ │   └── position_sync.py      # 位置同步                                                             │ │
│ │ └── tests/                                                                                           │ │
│ │     ├── test_agents.py        # 智能体测试                                                           │ │
│ │     ├── test_society.py       # Society测试                                                          │ │
│ │     └── test_integration.py   # 集成测试                                                             │ │
│ │                                                                                                      │ │
│ │ 关键改进点                                                                                           │ │
│ │                                                                                                      │ │
│ │ 1. 简化架构                                                                                          │ │
│ │                                                                                                      │ │
│ │ - 移除多层继承: 直接基于CamelAI ChatAgent                                                            │ │
│ │ - 统一状态管理: 单一SharedKitchenState                                                               │ │
│ │ - 消除重复代码: 复用CamelAI的现有功能                                                                │ │
│ │                                                                                                      │ │
│ │ 2. 解决并发冲突                                                                                      │ │
│ │                                                                                                      │ │
│ │ - 顺序决策: 按agent_id固定顺序决策                                                                   │ │
│ │ - 任务立即移除: 选择后立即从可用列表移除                                                             │ │
│ │ - 状态锁定: 决策期间锁定状态修改                                                                     │ │
│ │                                                                                                      │ │
│ │ 3. 优化LLM成本                                                                                       │ │
│ │                                                                                                      │ │
│ │ - 简化Prompt: 移除冗余信息                                                                           │ │
│ │ - 减少调用频率: 合并相似决策                                                                         │ │
│ │ - 缓存机制: 相似场景复用决策                                                                         │ │
│ │                                                                                                      │ │
│ │ 4. CamelAI原生集成                                                                                   │ │
│ │                                                                                                      │ │
│ │ - Society模式: 使用CamelAI的Society管理多Agent                                                       │ │
│ │ - Role Playing: 明确的角色定义和交互协议                                                             │ │
│ │ - Memory机制: 利用CamelAI的记忆功能                                                                  │ │
│ │                                                                                                      │ │
│ │ 成功指标                                                                                             │ │
│ │                                                                                                      │ │
│ │ 1. 功能完整性: 能够处理"制作2份西红柿炒蛋"等复杂订单                                                 │ │
│ │ 2. 冲突解决: 零并发任务选择冲突                                                                      │ │
│ │ 3. 位置智能: Agent优先选择距离近的任务                                                               │ │
│ │ 4. 物理集成: 成功控制toio机器人执行动作                                                              │ │
│ │ 5. 性能优化: LLM调用次数减少50%以上                                                                  │ │
│ │                                                                                                      │ │
│ │ 开发时间线                                                                                           │ │
│ │                                                                                                      │ │
│ │ - Week 1: Phase 1-2 (CamelAI基础框架 + 智能体实现)                                                   │ │
│ │ - Week 2: Phase 3-4 (冲突解决 + 集成测试)                                                            │ │
│ │ - Week 3: Phase 5 (物理集成) + 优化调试                                                              │ │
│ │                                                                                                      │ │
│ │ 这个计划将构建一个简化、稳定、基于CamelAI的多智能体系统，专注于核心功能的MVP实现，为后续扩展奠定坚实 │ │
│ │ 基础。  