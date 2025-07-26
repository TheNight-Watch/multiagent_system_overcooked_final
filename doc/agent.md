Agents
Learn about CAMEL’s agent types, with a focus on ChatAgent and advanced agent architectures for AI-powered automation.

​
Concept
Agents in CAMEL are autonomous entities capable of performing specific tasks through interaction with language models and other components. Each agent is designed with a particular role and capability, allowing them to work independently or collaboratively to achieve complex goals.
Think of an agent as an AI-powered teammate one that brings a defined role, memory, and tool-using abilities to every workflow. CAMEL’s agents are composable, robust, and can be extended with custom logic.
​
Base Agent Architecture
All CAMEL agents inherit from the BaseAgent abstract class, which defines two essential methods:
Method	Purpose	Description
reset()	State Management	Resets the agent to its initial state
step()	Task Execution	Performs a single step of the agent’s operation
​
Types
​
ChatAgent
The ChatAgent is the primary implementation that handles conversations with language models. It supports:
System message configuration for role definition
Memory management for conversation history
Tool/function calling capabilities
Response formatting and structured outputs
Multiple model backend support with scheduling strategies
Async operation support
Other Agent Types (When to Use)

​
Usage
​
Basic ChatAgent Usage

Copy
from camel.agents import ChatAgent

# Create a chat agent with a system message
agent = ChatAgent(system_message="You are a helpful assistant.")

# Step through a conversation
response = agent.step("Hello, can you help me?")
​
Simplified Agent Creation
The ChatAgent supports multiple ways to specify the model:

Copy
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Method 1: Using just a string for the model name (default model platform is used)
agent_1 = ChatAgent("You are a helpful assistant.", model="gpt-4o-mini")

# Method 2: Using a ModelType enum (default model platform is used)
agent_2 = ChatAgent("You are a helpful assistant.", model=ModelType.GPT_4O_MINI)

# Method 3: Using a tuple of strings (platform, model)
agent_3 = ChatAgent("You are a helpful assistant.", model=("openai", "gpt-4o-mini"))

# Method 4: Using a tuple of enums
agent_4 = ChatAgent(
    "You are a helpful assistant.",
    model=(ModelPlatformType.ANTHROPIC, ModelType.CLAUDE_3_5_SONNET),
)

# Method 5: Using default model platform and default model type when none is specified
agent_5 = ChatAgent("You are a helpful assistant.")

# Method 6: Using a pre-created model with ModelFactory (original approach)
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,  # Using enum
    model_type=ModelType.GPT_4O_MINI,         # Using enum
)
agent_6 = ChatAgent("You are a helpful assistant.", model=model)

# Method 7: Using ModelFactory with string parameters
model = ModelFactory.create(
    model_platform="openai",     # Using string
    model_type="gpt-4o-mini",    # Using string
)
agent_7 = ChatAgent("You are a helpful assistant.", model=model)
​
Using Tools with Chat Agent

Copy
from camel.agents import ChatAgent
from camel.toolkits import FunctionTool

# Define a tool
def calculator(a: int, b: int) -> int:
    return a + b

# Create agent with tool
agent = ChatAgent(tools=[calculator])

# The agent can now use the calculator tool in conversations
response = agent.step("What is 5 + 3?")
​
Structured Output

Copy
from pydantic import BaseModel
from typing import List

class ResponseFormat(BaseModel):
    points: List[str]
    summary: str

# Create agent with structured output
agent = ChatAgent()
response = agent.step("List benefits of exercise", response_format=ResponseFormat)
​
Best Practices
Memory Management

Tool Integration

Response Handling

Model Specification

​
Advanced Features
Model Scheduling
Output Language Control
You can dynamically select which model an agent uses for each step by adding your own scheduling strategy.

Custom Model Scheduling

Copy
def custom_strategy(models):
    # Custom model selection logic
    return models[0]

agent.add_model_scheduling_strategy("custom", custom_strategy)