Tools  工具
For more detailed usage information, please refer to our cookbook: Tools Cookbook
如需更详细的使用说明，请参阅我们的手册：工具手册
What is a Tool?  什么是工具？
A Tool in CAMEL is a callable function with a name, description, input parameters, and an output type.
CAMEL 中的工具是一个可调用的函数，具有名称、描述、输入参数和输出类型。
Tools act as the interface between agents and the outside world—think of them like OpenAI Functions you can easily convert, extend, or use directly.
工具充当代理与外部世界之间的接口——可以将它们视为类似于 OpenAI Functions 的组件，你可以轻松地转换、扩展或直接使用它们。
What is a Toolkit?  什么是工具包？
A Toolkit is a curated collection of related tools designed to work together for a specific purpose.
工具包是一组经过精心挑选的、相互关联的工具，这些工具被设计成能够协同工作以实现特定目标。
CAMEL provides a range of built-in toolkits—covering everything from web search and data extraction to code execution, GitHub integration, and much more.
CAMEL 提供了一系列内置工具包，涵盖从网页搜索和数据提取到代码执行、GitHub 集成等多种功能，以及更多其他功能。
​
Get Started  立即开始
Install Toolkits  安装工具包
To unlock advanced capabilities for your agents, install CAMEL’s extra tools package:
要为您的代理解锁高级功能，请安装 CAMEL 的额外工具包：

Copy  复制
pip install ‘camel-ai[tools]’
A tool in CAMEL is just a FunctionTool—an interface any agent can call to run custom logic or access APIs.
CAMEL 中的工具只是一个 FunctionTool——任何代理都可以调用该接口来执行自定义逻辑或访问 API。
Define a Custom Tool  定义自定义工具
You can easily create your own tools for any use case. Just write a Python function and wrap it using FunctionTool:
您可以轻松创建适用于任何场景的自定义工具。只需编写一个 Python 函数，并使用 FunctionTool 进行封装：
add_tool.py
  添加工具.py

Copy  复制
from camel.toolkits import FunctionTool

def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

add_tool = FunctionTool(add)
Inspect your tool’s properties—such as its name, description, and OpenAI-compatible schema—using built-in methods:
检查工具的属性（如名称、描述和与 OpenAI 兼容的 schema）使用内置方法：

tool_properties.py
  工具属性.py

output.txt
  输出.txt

Copy  复制
print(add_tool.get_function_name())          # add
print(add_tool.get_function_description())   # Adds two numbers.
print(add_tool.get_openai_function_schema()) # OpenAI Functions schema
print(add_tool.get_openai_tool_schema())     # OpenAI Tool format
Using Toolkits  使用工具包
Toolkits group related tools for specialized tasks—search, math, or automation. Use built‑in toolkits or build your own:
工具包将相关工具分组，用于特定任务——搜索、数学或自动化。使用内置工具包或创建自己的工具包：
toolkit_usage.py
  工具包使用说明.py

Copy  复制
from camel.toolkits import SearchToolkit
toolkit = SearchToolkit()
tools   = toolkit.get_tools()
You can also wrap toolkit methods as individual FunctionTools:
您还可以将工具包方法封装为独立的 FunctionTools：
custom_tools.py
  自定义工具.py

Copy  复制
from camel.toolkits import FunctionTool, SearchToolkit
google_tool = FunctionTool(SearchToolkit().search_google)
wiki_tool   = FunctionTool(SearchToolkit().search_wiki)
Passing Tools to ChatAgent
将工具传递给聊天机器人
You can enhance any ChatAgent with custom or toolkit-powered tools. Just pass the tools during initialization:
您可以通过自定义工具或工具包提供的工具来增强任何 ChatAgent。只需在初始化时传入这些工具：
chatagent_tools.py
  聊天机器人工具.py

Copy  复制
from camel.agents import ChatAgent
tool_agent = ChatAgent(
    tools=tools,  # List of FunctionTools
)
response = tool_agent.step("A query related to the tool you added")
​
