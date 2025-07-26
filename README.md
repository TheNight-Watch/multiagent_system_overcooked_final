# 🍳 CamelAI-Based Multi-Agent Overcooked System

基于CamelAI框架的真正多智能体Overcooked烹饪协作系统 - 动态协作主程序

## 📋 项目简介

这是一个基于CamelAI框架的多智能体协作烹饪系统，实现了真正的多智能体动态协作。系统可以：

- 🧠 **动态分析菜品需求** - 无需预定义模板，智能分析任意菜品
- 🤖 **多智能体协作** - 3个通用厨师智能体协作完成任务
- 🎯 **实时任务分配** - 智能协商和动态任务分配
- 🔧 **真实硬件控制** - 集成toio机器人硬件控制
- 📊 **完整动作记录** - 生成详细的JSON格式动作记录

## 🚀 核心特性

### 🧠 智能分析系统
- 动态分析任意菜品制作需求
- 智能分解任务步骤
- 识别可并行执行的操作
- 估算各步骤时间需求

### 🤖 多智能体协作
- **Order Manager**: 订单分析专家
- **Chef_1**: 通用厨师，可执行任何烹饪任务
- **Chef_2**: 通用厨师，可执行任何烹饪任务  
- **Chef_3**: 通用厨师，可执行任何烹饪任务

### 🔧 硬件集成
- 真实toio机器人控制
- 仿真模式支持
- 厨房布局管理
- 工具定位系统

### 📊 动作系统
- `pick_x()` - 拾取原料
- `slice_x()` - 切割原料
- `cook_x()` - 烹饪菜品
- `serve_x()` - 交付菜品
- `check_robot_status()` - 检查机器人状态

## 🏗️ 系统架构

```
main.py (主程序)
├── DynamicCookingSystem (动态烹饪系统)
│   ├── analyze_dish_requirements() - 菜品需求分析
│   ├── execute_collaborative_cooking() - 协作烹饪执行
│   └── _parse_agent_actions_from_collaboration() - 动作解析
├── agents/ (智能体模块)
│   ├── cooking_agent.py - 烹饪智能体
│   └── order_manager.py - 订单管理智能体
├── core/ (核心组件)
│   └── kitchen_state.py - 厨房状态管理
├── toio/ (硬件控制)
│   ├── controller.py - toio控制器
│   └── ai_agent.py - AI代理
└── toio_integration/ (集成模块)
    ├── toio_controller.py - 底层控制器
    └── cooking_toolkit.py - 烹饪工具包
```

## 🛠️ 安装与配置

### 环境要求
- Python 3.8+
- toio-py 库
- CamelAI 框架

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd multiagent7_26_last
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件配置必要的环境变量
```

## 🎮 使用方法

### 基本使用

```bash
python main.py "宫保鸡丁"
```

### 支持的菜品

系统支持动态分析任意菜品，包括但不限于：

- 🍅 西红柿炒蛋 (Tomato and Egg)
- 🐔 宫保鸡丁 (Kung Pao Chicken)  
- 🧈 麻婆豆腐 (Mapo Tofu)
- 🍚 炒饭 (Fried Rice)
- 🥩 红烧肉 (Braised Pork)
- 🍜 任意其他菜品

### 输出格式

系统会生成JSON格式的动作记录，包含：

```json
{
  "chef_1": [
    {
      "step": 0,
      "agent_id": "chef_1", 
      "action_type": "pick",
      "target": "vegetables",
      "position": [147, 274],
      "success": true,
      "timestamp": "step_0",
      "details": {
        "message": "Chef_1正在拾取蔬菜",
        "specialization": "通用厨师",
        "dynamic_decision": true
      }
    }
  ],
  "chef_2": [...],
  "chef_3": [...]
}
```

## 🏗️ 厨房布局

### 坐标系统
使用toio真实坐标系统 (45-455空间)

### 功能区域
- **储藏区** (229,70), (270,70) - 存放所有原料
- **切菜区** (106,70), (147,70), (188,70) - 处理原料
- **烹饪区** (147,274), (188,274), (229,274) - 烹饪菜品
- **交付区** (352,70) - 交付菜品
- **操作台区** (270,377) - 通用操作区域

### 原料映射
- 所有蔬菜 → "vegetables"
- 所有肉类 → "meat"
- 鸡蛋 → "eggs" 
- 米饭 → "rice"
- 所有调料 → "seasonings"

## 🔧 开发指南

### 项目结构
```
multiagent7_26_last/
├── main.py                 # 主程序入口
├── agents/                 # 智能体模块
│   ├── __init__.py
│   ├── cooking_agent.py
│   └── order_manager.py
├── core/                   # 核心组件
│   ├── __init__.py
│   └── kitchen_state.py
├── toio/                   # toio硬件控制
│   ├── __init__.py
│   ├── controller.py
│   └── ai_agent.py
├── toio_integration/       # 集成模块
│   ├── __init__.py
│   ├── toio_controller.py
│   └── cooking_toolkit.py
├── doc/                    # 文档
│   ├── agent.md
│   ├── model_factory.md
│   └── tool.md
├── requirements.txt        # 依赖列表
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明
```

### 添加新功能

1. **添加新的智能体**
   - 在 `agents/` 目录下创建新的智能体文件
   - 在 `main.py` 中注册新智能体

2. **添加新的烹饪动作**
   - 在 `toio_integration/cooking_toolkit.py` 中添加新方法
   - 更新智能体的动作调用

3. **修改厨房布局**
   - 编辑 `toio_integration/toio_controller.py` 中的 `KitchenLayout` 类

## 🧪 测试

### 运行测试
```bash
python -m pytest tests/
```

### 仿真模式测试
```bash
python main.py "测试菜品" --simulation
```

## 📈 性能优化

- 使用异步操作提高并发性能
- 智能任务分配减少冲突
- 缓存机制优化重复计算
- 并行执行提高效率

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [CamelAI](https://github.com/camel-ai/camel) - 多智能体框架
- [toio-py](https://github.com/sony/toio-py) - toio机器人控制库
- 所有贡献者和用户

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/multiagent7_26_last/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/multiagent7_26_last/discussions)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！ 