Workforce  劳动力
Concept  概念
Workforce is CAMEL-AI’s multi-agent teamwork engine.
Workforce 是 CAMEL-AI 的多智能体协作引擎。
Instead of relying on a single agent, Workforce lets you organize a team of specialized agents—each with its own strengths—under a single, coordinated system. You can quickly assemble, configure, and launch collaborative agent “workforces” for any task that needs parallelization, diverse expertise, or complex workflows.
与依赖单一代理不同，Workforce 允许您在统一的协调系统下组建一支由专业代理组成的团队——每个代理都具备独特的优势。您可以快速组建、配置并启动协作代理“工作团队”，以应对任何需要并行处理、多元专业技能或复杂工作流的任务。
With Workforce, agents plan, solve, and verify work together—like a project team in an organization, but fully automated.
借助 Workforce，客服代表可以像组织中的项目团队一样，共同规划、解决和验证工作——但整个过程完全自动化。
Key advantages of Workforce:
劳动力优势：
Instantly scale from single-agent to multi-agent workflows
即时扩展从单一代理到多代理工作流程
Built-in coordination, planning, and failure recovery
内置协调、规划和故障恢复功能
Ideal for hackathons, evaluations, code review, brainstorming, and more
适用于黑客马拉松、评估、代码审查、头脑风暴等场景。
Configure roles, toolsets, and communication patterns for any scenario
为任何场景配置角色、工具集和通信模式。
See More: Hackathon Judge Committee Example
查看更多：黑客马拉松评委委员会示例
Check out our in-depth Workforce example:
查看我们的详细劳动力示例：
Create a Hackathon Judge Committee with Workforce
组建黑客马拉松评委委员会，利用人力资源
​
System Design  系统设计
​
Architecture: How Workforce Works
架构： workforce 的运作方式
Workforce uses a hierarchical, modular design for real-world team problem-solving:
Workforce 采用分层模块化设计，适用于现实世界中的团队问题解决：
See how the coordinator and task planner agents orchestrate a multi-agent workflow:
了解协调器和任务规划器代理如何协同管理多智能体工作流：
Workforce Architecture Diagram
Workforce: The “team” as a whole.
劳动力：作为整体的“团队”。
Worker nodes: Individual contributors—each node can contain one or more agents, each with their own capabilities.
工作节点：独立贡献者——每个节点可以包含一个或多个代理，每个代理都具备独立的功能。
Coordinator agent: The “project manager”—routes tasks to worker nodes based on their role and skills.
协调代理：相当于“项目经理”——根据任务的类型和执行节点的角色及技能，将任务分配给相应的执行节点。
Task planner agent: The “strategy lead”—breaks down big jobs into smaller, doable subtasks and organizes the workflow.
任务规划代理：作为“战略负责人”，将大型任务分解为更小、更易管理的子任务，并组织工作流程。
​
Communication: A Shared Task Channel
沟通：一个共享任务通道
Every Workforce gets a shared task channel when it’s created.
每个工作组在创建时都会获得一个共享任务频道。
How it works:  工作原理：
All tasks are posted into this channel.
所有任务均发布在此频道中。
Worker nodes “listen” and accept their assigned tasks.
工作节点“监听”并接受分配的任务。
Results are posted back to the channel, where they’re available as dependencies for the next steps.
结果会被发回至通道，并在其中作为后续步骤的依赖项供使用。
This design lets agents build on each other’s work and ensures no knowledge is lost between steps.
该设计使代理能够在彼此的工作基础上进行构建，并确保在各个步骤之间不会丢失任何知识。
​
Failure Handling: Built-In Robustness
故障处理：内置健壮性
Workforce is designed to handle failures and recover gracefully:
Workforce 设计用于处理故障并实现优雅恢复：
If a worker fails a task, the coordinator agent will:
如果工人未能完成任务，协调员代理将：
Decompose and retry: Break the task into even smaller pieces and reassign.
分解并重试：将任务分解为更小的部分并重新分配。
Escalate: If the task keeps failing, create a new worker designed for that problem.
升级处理：如果任务持续失败，请创建一个专门针对该问题的全新工作者。
To prevent infinite loops, if a task has failed or been decomposed more than a set number of times (default: 3), Workforce will automatically halt that workflow.
为防止无限循环，如果一个任务失败或被分解的次数超过了设定的阈值（默认值：3），Workforce 将自动终止该工作流。
Tip: Workforce automatically stops stuck workflows—so you don’t waste compute or get caught in agent loops!
提示：Workforce 会自动暂停卡住的工作流，这样您就不会浪费计算资源或陷入代理循环！
Quickstart: Build Your First Workforce
快速入门：构建您的首个团队
1
Create a Workforce Instance
创建一个 workforce 实例

To begin, import and create a new Workforce:
首先，导入并创建一个新的劳动力：

Copy  复制
from camel.societies.workforce import Workforce

# Create a workforce instance
workforce = Workforce("A Simple Workforce")
For quick setups, just provide the description.
对于快速设置，只需提供描述。
For advanced workflows, you can pass in custom worker lists or configure the coordinator and planner agents.
对于高级工作流，您可以传入自定义的 worker 列表，或配置协调器和规划器代理。
2
Add Worker Nodes  添加工作节点

Now add your worker agents.
现在添加您的工作代理。
(Example: a ChatAgent for web search, named search_agent.)
（示例：用于网页搜索的 ChatAgent ，命名为 search_agent 。）

Copy  复制
# Add a worker agent to the workforce
workforce.add_single_agent_worker(
    "An agent that can do web searches",
    worker=search_agent,
)
Chain multiple agents for convenience:
为方便起见，将多个代理串联起来：

Copy  复制
workforce.add_single_agent_worker(
    "An agent that can do web searches",
    worker=search_agent,
).add_single_agent_worker(
    "Another agent",
    worker=another_agent,
).add_single_agent_worker(
    "Yet another agent",
    worker=yet_another_agent,
)
The description is important!
描述非常重要！
The coordinator uses it to assign tasks—so keep it clear and specific.
协调员使用它来分配任务——因此请保持内容清晰且具体。
3
Start the Workforce and Solve Tasks
启动团队并解决任务

Define a task and let the workforce handle it:
定义任务并让员工处理：

Copy  复制
from camel.tasks import Task

# The id can be any string
task = Task(
    content="Make a travel plan for a 3-day trip to Paris.",
    id="0",
)

# Process the task with the workforce
task = workforce.process_task(task)

# See the result
print(task.result)