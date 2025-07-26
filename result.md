((venv) ) liuhaifeng@MacBook-Air-6 multiagent7_26_last % python main.py '炝炒西兰花'
✅ 真实toio控制器导入成功
🍳 CamelAI 动态多智能体 Overcooked 系统
📋 处理订单: 炝炒西兰花
============================================================
🤖 启动动态多智能体协作系统...
📋 处理订单: 炝炒西兰花
🔍 正在连接真实toio设备...
Scanning for 3 toio cubes...
2025-07-27 06:01:40,610 - ToioPyLogger.toio.device_interface.ble - DEBUG - scanner: timeout 15.0 sec
Connected to cube: cube_1
Connected to cube: cube_2
Connected to cube: cube_3
✅ 成功连接到真实toio设备
🍳 烹饪工具包初始化完成 - 基于真实ToioController API
2025-07-27 06:01:42,087 - camel.camel.societies.workforce.workforce - WARNING - No coordinator_agent provided. Using default ChatAgent settings (ModelPlatformType.DEFAULT, ModelType.DEFAULT) with default system message.
2025-07-27 06:01:42,276 - camel.camel.societies.workforce.workforce - WARNING - No task_agent provided. Using default ChatAgent settings (ModelPlatformType.DEFAULT, ModelType.DEFAULT) with default system message and TaskPlanningToolkit.
🔄 多智能体协作分析中...
   - Order Manager: 动态分析菜品需求
   - Chef_1 (通用厨师): 使用工具执行烹饪任务
   - Chef_2 (通用厨师): 使用工具执行烹饪任务
   - Chef_3 (通用厨师): 使用工具执行烹饪任务
🤖 开始任务队列协作制作: 炝炒西兰花
📋 生成带依赖关系的任务队列...
📋 添加 炝炒西兰花 的任务到队列 (4 个任务)
  + task_1_pick_x: pick_x(chef_1, vegetables)
  + task_2_pick_x: pick_x(chef_2, seasonings)
  + task_3_cook_x: cook_x(chef_3, 炝炒西兰花) (依赖: ['task_1_pick_x', 'task_2_pick_x'])
  + task_4_serve_x: serve_x(chef_1, 炝炒西兰花) (依赖: ['task_3_cook_x'])
✅ 任务队列初始化完成，共 4 个任务
📋 任务队列状态摘要:

📊 统计信息:
  总任务数: 4
  待执行: 4
  执行中: 0
  已完成: 0

⏳ 待执行任务:
  ✅ task_1_pick_x: pick_x(chef_1, vegetables)
  ✅ task_2_pick_x: pick_x(chef_2, seasonings)
  ❌ task_3_cook_x: cook_x(chef_3, 炝炒西兰花) (依赖: ['task_1_pick_x', 'task_2_pick_x'])
  ❌ task_4_serve_x: serve_x(chef_1, 炝炒西兰花) (依赖: ['task_3_cook_x'])

🚀 开始执行任务队列...

=== 执行步骤 1 ===
🎯 chef_1 获得任务: pick_x(chef_1, vegetables)
🚀 chef_1 开始执行任务 task_1_pick_x: pick_x
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0: chef_1: Execute the pick_x operation to pick the specified vegetables.
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

I need to know the specific vegetables to pick in order to execute the pick_x operation.
======
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.0: chef_1: Execute the pick_x operation to pick the specified vegetables assigned to chef_1.
Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.1: chef_2: Execute the pick_x operation to pick the specified vegetables assigned to chef_2.
Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.2: chef_3: Execute the pick_x operation to pick the specified vegetables assigned to chef_3.
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

I could not perform the pick_x operation due to missing information about the specific vegetables to pick.
======
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.0.0: Identify the specific vegetables assigned to chef_1 to pick.
======
Reply from Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务):

I could not execute the pick_x operation because the specific vegetables to pick were not provided.
======
======
Reply from Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务):

I could not perform the pick_x operation because the specific vegetables to pick were not provided.
======
Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.1.0: Identify the specific vegetables assigned to chef_2 for picking.
Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.2.0: Identify the specific vegetables to pick assigned to chef_3.
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

There is no information provided about the specific vegetables assigned to chef_1 to pick.
======
/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/toolkits/function_tool.py:533: UserWarning: Parameter description is missing for the function 'search_linkup'. The parameter definition is {'enum': ['searchResults', 'sourcedAnswer', 'structured'], 'type': ['string', 'null']}. This may affect the quality of tool calling.
  warnings.warn(
/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/toolkits/function_tool.py:533: UserWarning: Parameter description is missing for the function 'search_alibaba_tongxiao'. The parameter definition is {'enum': ['OneDay', 'OneWeek', 'OneMonth', 'OneYear', 'NoLimit'], 'type': ['string', 'null']}. This may affect the quality of tool calling.
  warnings.warn(
/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/toolkits/function_tool.py:533: UserWarning: Parameter description is missing for the function 'search_alibaba_tongxiao'. The parameter definition is {'anyOf': [{'enum': ['finance', 'law', 'medical', 'internet', 'tax', 'news_province', 'news_center'], 'type': 'string'}, {'type': 'null'}], 'type': ['null']}. This may affect the quality of tool calling.
  warnings.warn(
Worker node 4e431470-0a8e-4e54-b667-0ee5d766dbc7 (Specialist worker node dedicated to identifying and specifying the precise vegetables required for picking tasks, ensuring clear instructions for pick operations without overlapping general chef roles.) created.
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.0.1: Execute the pick_x operation to pick the identified vegetables assigned to chef_1.
======
Reply from Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务):

I could not identify the specific vegetables to pick assigned to chef_3 due to missing information.
======
======
Reply from Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务):

The specific vegetables assigned to chef_2 for picking were not provided in the available information.
======
Worker node 45f66885-8d51-4bae-b82d-eba2da516248 (Worker node specialized in analyzing and assigning specific vegetable picking tasks to chefs, ensuring clear vegetable-to-chef assignments distinct from general cooking or picking operations.) created.
Worker node 1a5a0dc2-8e97-428e-b8b2-cb7fac7a30b2 (Consultant worker node focused on the identification and clarification of specific vegetables for picking tasks, providing detailed information to enable precise picking without overlapping existing chef or assignment analyst roles.) created.
Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.1.1: Execute the pick_x operation to pick the identified vegetables assigned to chef_2.
Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务) get task execute_task_1_pick_x_1753567302.0.2.1: Perform the pick_x operation to pick the identified vegetables assigned to chef_3.
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

I could not perform the pick_x operation due to missing information about the specific vegetables assigned to chef_1 to pick.
======
Worker node 1bc2baf8-c4a4-4d2a-a790-a911ca72188b (Worker node specialized in executing pick_x operations to pick specific vegetables as assigned, distinct from roles involved in identifying or assigning vegetables for picking.) created.
======
Reply from Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务):

I could not perform the pick_x operation because the specific vegetables to pick assigned to chef_3 were not provided.
======
======
Reply from Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务):

I could not execute the pick_x operation because the specific vegetables to pick assigned to chef_2 were not provided.
======
Worker node 97fcb66b-860b-4471-8c95-1963c88b3767 (Specialized worker node dedicated to performing vegetable picking operations as instructed, focusing solely on the execution of picking tasks without involvement in vegetable identification or assignment.) created.
^CWorker node 1bf6ddff-8a2a-4ccc-8a5b-b913c15b9092 (Worker node dedicated to performing precise vegetable picking operations as assigned, ensuring accurate execution of pick_x tasks without overlapping identification or assignment responsibilities.) created.