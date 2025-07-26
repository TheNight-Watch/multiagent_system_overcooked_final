((venv) ) liuhaifeng@MacBook-Air-6 multiagent7_26_last % python main.py '宫保鸡丁'  
✅ 真实toio控制器导入成功
🍳 CamelAI 动态多智能体 Overcooked 系统
📋 处理订单: 宫保鸡丁
============================================================
🤖 启动动态多智能体协作系统...
📋 处理订单: 宫保鸡丁
🔍 正在连接真实toio设备...
Scanning for 3 toio cubes...
2025-07-27 05:40:50,581 - ToioPyLogger.toio.device_interface.ble - DEBUG - scanner: timeout 15.0 sec
Connected to cube: cube_1
Connected to cube: cube_2
Connected to cube: cube_3
✅ 成功连接到真实toio设备
🍳 烹饪工具包初始化完成 - 基于真实ToioController API
2025-07-27 05:40:52,421 - camel.camel.societies.workforce.workforce - WARNING - No coordinator_agent provided. Using default ChatAgent settings (ModelPlatformType.DEFAULT, ModelType.DEFAULT) with default system message.
2025-07-27 05:40:52,553 - camel.camel.societies.workforce.workforce - WARNING - No task_agent provided. Using default ChatAgent settings (ModelPlatformType.DEFAULT, ModelType.DEFAULT) with default system message and TaskPlanningToolkit.
🔄 多智能体协作分析中...
   - Order Manager: 动态分析菜品需求
   - Chef_1 (通用厨师): 使用工具执行烹饪任务
   - Chef_2 (通用厨师): 使用工具执行烹饪任务
   - Chef_3 (通用厨师): 使用工具执行烹饪任务
🤖 开始多智能体协作制作: 宫保鸡丁
🧠 动态分析菜品需求: 宫保鸡丁
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task dish_analysis_宫保鸡丁_1753566052.0: Chef_1: pick ingredients for 宫保鸡丁
Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务) get task dish_analysis_宫保鸡丁_1753566052.1: Chef_2: pick seasonings for 宫保鸡丁
🥬 chef_2: 开始拾取原料 'seasonings'
🚶 chef_2: 移动到原料位置 (188, 70)
✋ chef_2: 拾取 seasonings
🤖 chef_2 移动到位置 (188, 70)，执行动作: picked_seasonings
🥬 chef_1: 开始拾取原料 'meat'
🚶 chef_1: 移动到原料位置 (270, 70)
✋ chef_1: 拾取 meat
🤖 chef_1 移动到位置 (270, 70)，执行动作: picked_meat
🥬 chef_1: 开始拾取原料 'vegetables'
🚶 chef_1: 移动到原料位置 (229, 70)
✋ chef_1: 拾取 vegetables
🤖 chef_1 移动到位置 (229, 70)，执行动作: picked_vegetables
🥬 chef_1: 开始拾取原料 'seasonings'
🚶 chef_1: 移动到原料位置 (188, 70)
✋ chef_1: 拾取 seasonings
🤖 chef_1 移动到位置 (188, 70)，执行动作: picked_seasonings
======
Reply from Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务):

成功拾取 seasonings 用于宫保鸡丁。
======
🎯 Task dish_analysis_宫保鸡丁_1753566052.1 completed successfully.
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

成功拾取宫保鸡丁所需食材：meat、vegetables和seasonings。
======
🎯 Task dish_analysis_宫保鸡丁_1753566052.0 completed successfully.
Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务) get task dish_analysis_宫保鸡丁_1753566052.2: Chef_3: cook 宫保鸡丁 using the picked ingredients and seasonings
🍳 chef_3: 开始烹饪菜品 '宫保鸡丁'
🚶 chef_3: 移动到灶台位置 (188, 274)
🔥 chef_3: 烹饪 宫保鸡丁
  烹饪进度: 25%
  🔥 点火加热...
  烹饪进度: 50%
  🥄 翻炒中...
  烹饪进度: 75%
  🧂 调味中...
  烹饪进度: 100%
  ✨ 即将完成...
✅ chef_3: 宫保鸡丁 烹饪完成!
🤖 chef_3 移动到位置 (188, 274)，执行动作: cooked_宫保鸡丁
======
Reply from Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务):

成功烹饪 宫保鸡丁。
======
🎯 Task dish_analysis_宫保鸡丁_1753566052.2 completed successfully.
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task dish_analysis_宫保鸡丁_1753566052.3: Chef_1: serve 宫保鸡丁
🍽️ chef_1: 开始交付菜品 '宫保鸡丁'
🚶 chef_1: 移动到交付窗口 (352, 70)
🎯 chef_1: 交付 宫保鸡丁
  📋 检查菜品质量...
  🍽️ 小心放置到交付窗口...
  ✅ 交付完成，等待顾客取餐...
🤖 chef_1 移动到位置 (352, 70)，执行动作: served_宫保鸡丁
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

成功交付 宫保鸡丁。
======
🎯 Task dish_analysis_宫保鸡丁_1753566052.3 completed successfully.
📋 菜品需求分析完成:
--- Subtask dish_analysis_宫保鸡丁_1753566052.0 Result ---
成功拾取宫保鸡丁所需食材：meat、vegetables和seasonings。

--- Subtask dish_analysis_宫保鸡丁_1753566052.1 Result ---
成功拾取 seasonings 用于宫保鸡丁。

--- Subtask dish_analysis_宫保鸡丁_1753566052.2 Result ---
成功烹饪 宫保鸡丁。

--- Subtask dish_analysis_宫保鸡丁_1753566052.3 Result ---
成功交付 宫保鸡丁。
🚀 开始多智能体协作执行...
Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务) get task collaborative_cooking_宫保鸡丁_1753566100.0: Chef_1: 拾取宫保鸡丁所需食材：meat、vegetables和seasonings。
Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务) get task collaborative_cooking_宫保鸡丁_1753566100.1: Chef_2: 拾取 seasonings 用于宫保鸡丁。
🥬 chef_2: 开始拾取原料 'seasonings'
🚶 chef_2: 移动到原料位置 (188, 70)
✋ chef_2: 拾取 seasonings
🤖 chef_2 移动到位置 (188, 70)，执行动作: picked_seasonings
🥬 chef_1: 开始拾取原料 'meat'
🚶 chef_1: 移动到原料位置 (270, 70)
✋ chef_1: 拾取 meat
🤖 chef_1 移动到位置 (270, 70)，执行动作: picked_meat
🥬 chef_1: 开始拾取原料 'vegetables'
🚶 chef_1: 移动到原料位置 (229, 70)
✋ chef_1: 拾取 vegetables
🤖 chef_1 移动到位置 (229, 70)，执行动作: picked_vegetables
🥬 chef_1: 开始拾取原料 'seasonings'
🚶 chef_1: 移动到原料位置 (188, 70)
✋ chef_1: 拾取 seasonings
🤖 chef_1 移动到位置 (188, 70)，执行动作: picked_seasonings
======
Reply from Worker node chef_2 (Chef_2 (通用厨师)：使用工具执行烹饪任务):

成功拾取 seasonings 用于宫保鸡丁。
======
🎯 Task collaborative_cooking_宫保鸡丁_1753566100.1 completed successfully.
======
Reply from Worker node chef_1 (Chef_1 (通用厨师)：使用工具执行烹饪任务):

成功拾取宫保鸡丁所需食材：meat、vegetables和seasonings。
======
🎯 Task collaborative_cooking_宫保鸡丁_1753566100.0 completed successfully.
Worker node chef_3 (Chef_3 (通用厨师)：使用工具执行烹饪任务) get task collaborative_cooking_宫保鸡丁_1753566100.2: Chef_3: 烹饪 宫保鸡丁。
🍳 chef_3: 开始烹饪菜品 '宫保鸡丁'
🚶 chef_3: 移动到灶台位置 (188, 274)
🔥 chef_3: 烹饪 宫保鸡丁
  烹饪进度: 25%
  🔥 点火加热...
  烹饪进度: 50%
  🥄 翻炒中...
  烹饪进度: 75%
  🧂 调味中...
  烹饪进度: 100%
  ✨ 即将完成...
✅ chef_3: 宫保鸡丁 烹饪完成!
🤖 chef_3 移动到位置 (188, 274)，执行动作: cooked_宫保鸡丁
🍽️ chef_3: 开始交付菜品 '宫保鸡丁'
🚶 chef_3: 移动到交付窗口 (352, 70)
🎯 chef_3: 交付 宫保鸡丁
  📋 检查菜品质量...
  🍽️ 小心放置到交付窗口...
  ✅ 交付完成，等待顾客取餐...
🤖 chef_3 移动到位置 (352, 70)，执行动作: served_宫保鸡丁
^CTraceback (most recent call last):
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/workforce.py", line 930, in process_task
    current_loop = asyncio.get_running_loop()
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: no running event loop

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/workforce.py", line 891, in process_task_async
    await self.start()
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/workforce.py", line 2081, in start
    await self._listen_to_channel()
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/workforce.py", line 1999, in _listen_to_channel
    returned_task = await self._get_returned_task()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/workforce.py", line 1633, in _get_returned_task
    return await asyncio.wait_for(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/tasks.py", line 520, in wait_for
    return await fut
           ^^^^^^^^^
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/task_channel.py", line 100, in get_returned_task_by_publisher
    await self._condition.wait()
  File "/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/locks.py", line 266, in wait
    await fut
asyncio.exceptions.CancelledError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/liuhaifeng/multiagent7_26_last/main.py", line 398, in <module>
    main()
  File "/Users/liuhaifeng/multiagent7_26_last/main.py", line 375, in main
    actions_json = process_dish_order(dish_name)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/liuhaifeng/multiagent7_26_last/main.py", line 329, in process_dish_order
    actions = cooking_system.execute_collaborative_cooking(dish_name)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/liuhaifeng/multiagent7_26_last/main.py", line 177, in execute_collaborative_cooking
    self.workforce.process_task(collaboration_task)
  File "/Users/liuhaifeng/multiagent7_26_last/venv/lib/python3.12/site-packages/camel/societies/workforce/workforce.py", line 960, in process_task
    return asyncio.run(self.process_task_async(task))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.11/Frameworks/Python.framework/Versions/3.12/lib/python3.12/asyncio/runners.py", line 123, in run
    raise KeyboardInterrupt()
KeyboardInterrupt
zsh: trace trap  python main.py '宫保鸡丁'