Models
CAMEL-AI: Flexible integration and deployment of top LLMs and multimodal models like OpenAI, Mistral, Gemini, Llama, and more.

In CAMEL, every model refers specifically to a Large Language Model (LLM) the intelligent core powering your agent’s understanding, reasoning, and conversational capabilities.
Play with different models in our interactive Colab Notebook.
Large Language Models (LLMs)
LLMs are sophisticated AI systems trained on vast datasets to understand and generate human-like text. They reason, summarize, create content, and drive conversations effortlessly.
Flexible Model Integration
CAMEL allows quick integration and swapping of leading LLMs from providers like OpenAI, Gemini, Llama, and Anthropic, helping you match the best model to your task.
Optimized for Customization
Customize performance parameters such as temperature, token limits, and response structures easily, balancing creativity, accuracy, and efficiency.
Rapid Experimentation
Experiment freely, CAMEL’s modular design lets you seamlessly compare and benchmark different LLMs, adapting swiftly as your project needs evolve.
​
Supported Model Platforms in CAMEL
CAMEL supports a wide range of models, including OpenAI’s GPT series, Meta’s Llama models, DeepSeek models (R1 and other variants), and more.
​
Direct Integrations
Model Platform	Model Type(s)
OpenAI	gpt-4.5-preview
gpt-4o, gpt-4o-mini
o1, o1-preview, o1-mini
o3-mini, o3-pro
gpt-4-turbo, gpt-4, gpt-3.5-turbo
Azure OpenAI	gpt-4o, gpt-4-turbo
gpt-4, gpt-3.5-turbo
Mistral AI	mistral-large-latest, pixtral-12b-2409
ministral-8b-latest, ministral-3b-latest
open-mistral-nemo, codestral-latest
open-mistral-7b, open-mixtral-8x7b
open-mixtral-8x22b, open-codestral-mamba
magistral-medium-2506, mistral-small-2506
Moonshot	moonshot-v1-8k
moonshot-v1-32k
moonshot-v1-128k
Anthropic	claude-2.1, claude-2.0, claude-instant-1.2
claude-3-opus-latest, claude-3-sonnet-20240229, claude-3-haiku-20240307
claude-3-5-sonnet-latest, claude-3-5-haiku-latest
Gemini	gemini-2.5-pro, gemini-2.5-flash
gemini-2.0-flash, gemini-2.0-flash-thinking
gemini-2.0-flash-lite
Lingyiwanwu	yi-lightning, yi-large, yi-medium
yi-large-turbo, yi-vision, yi-medium-200k
yi-spark, yi-large-rag, yi-large-fc
Qwen	qwen3-coder-plus,qwq-32b-preview, qwen-max, qwen-plus, qwen-turbo, qwen-long
qwen-vl-max, qwen-vl-plus, qwen-math-plus, qwen-math-turbo, qwen-coder-turbo
qwen2.5-coder-32b-instruct, qwen2.5-72b-instruct, qwen2.5-32b-instruct, qwen2.5-14b-instruct
DeepSeek	deepseek-chat
deepseek-reasoner
ZhipuAI	glm-4, glm-4v, glm-4v-flash
glm-4v-plus-0111, glm-4-plus, glm-4-air
glm-4-air-0111, glm-4-airx, glm-4-long
glm-4-flashx, glm-zero-preview, glm-4-flash, glm-3-turbo
InternLM	internlm3-latest, internlm3-8b-instruct
internlm2.5-latest, internlm2-pro-chat
Reka	reka-core, reka-flash, reka-edge
COHERE	command-r-plus, command-r, command-light, command, command-nightly
​
API & Connector Platforms
Model Platform	Supported via API/Connector
GROQ	supported models
TOGETHER AI	supported models
SambaNova	supported models
Ollama	supported models
OpenRouter	supported models
PPIO	supported models
LiteLLM	supported models
LMStudio	supported models
vLLM	supported models
SGLANG	supported models
NetMind	supported models
NOVITA	supported models
NVIDIA	supported models
AIML	supported models
ModelScope	supported models
AWS Bedrock	supported models
IBM WatsonX	supported models
Crynux	supported models
qianfan	supported models
​
How to Use Models via API Calls
Integrate your favorite models into CAMEL-AI with straightforward Python calls. Choose a provider below to see how it’s done:
OpenAI
Gemini
Mistral
Anthropic
Qwen
Groq
Here’s how you use OpenAI models such as GPT-4o-mini with CAMEL:

Copy
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig
from camel.agents import ChatAgent

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type=ModelType.GPT_4O_MINI,
    model_config_dict=ChatGPTConfig(temperature=0.2).as_dict(),
)

agent = ChatAgent(
    system_message="You are a helpful assistant.",
    model=model
)

response = agent.step("Say hi to CAMEL AI community.")
print(response.msg.content)
​
Using On-Device Open Source Models
Run Open-Source LLMs Locally
Unlock true flexibility: CAMEL-AI supports running popular LLMs right on your own machine. Use Ollama, vLLM, or SGLang to experiment, prototype, or deploy privately (no cloud required).
CAMEL-AI makes it easy to integrate local open-source models as part of your agent workflows. Here’s how you can get started with the most popular runtimes:
1
Using Ollama for Llama 3

1
Install Ollama

Download Ollama and follow the installation steps for your OS.
2
Pull the Llama 3 model


Copy
ollama pull llama3
3
(Optional) Create a Custom Model

Create a file named Llama3ModelFile:

Copy
FROM llama3

PARAMETER temperature 0.8
PARAMETER stop Result

SYSTEM """ """
You can also create a shell script setup_llama3.sh:

Copy
#!/bin/zsh
model_name="llama3"
custom_model_name="camel-llama3"
ollama pull $model_name
ollama create $custom_model_name -f ./Llama3ModelFile
chmod +x setup_llama3.sh
./setup_llama3.sh
4
Integrate with CAMEL-AI


Copy
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

ollama_model = ModelFactory.create(
    model_platform=ModelPlatformType.OLLAMA,
    model_type="llama3",
    url="http://localhost:11434/v1",
    model_config_dict={"temperature": 0.4},
)
agent = ChatAgent("You are a helpful assistant.", model=ollama_model)
response = agent.step("Say hi to CAMEL")
print(response.msg.content)
2
Using vLLM for Phi-3

1
Install vLLM

Follow the vLLM installation guide for your environment.
2
Start the vLLM server


Copy
python -m vllm.entrypoints.openai.api_server \
  --model microsoft/Phi-3-mini-4k-instruct \
  --api-key vllm --dtype bfloat16
3
Integrate with CAMEL-AI


Copy
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

vllm_model = ModelFactory.create(
    model_platform=ModelPlatformType.VLLM,
    model_type="microsoft/Phi-3-mini-4k-instruct",
    url="http://localhost:8000/v1",
    model_config_dict={"temperature": 0.0},
)
agent = ChatAgent("You are a helpful assistant.", model=vllm_model)
response = agent.step("Say hi to CAMEL AI")
print(response.msg.content)
3
Using SGLang for Meta-Llama

1
Install SGLang

Follow the SGLang install instructions for your platform.
2
Integrate with CAMEL-AI


Copy
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

sglang_model = ModelFactory.create(
    model_platform=ModelPlatformType.SGLANG,
    model_type="meta-llama/Llama-3.2-1B-Instruct",
    model_config_dict={"temperature": 0.0},
    api_key="sglang",
)
agent = ChatAgent("You are a helpful assistant.", model=sglang_model)
response = agent.step("Say hi to CAMEL AI")
print(response.msg.content)
Looking for more examples?
Explore the full CAMEL-AI Examples library for advanced workflows, tool integrations, and multi-agent demos.
​
Model Speed and Performance
Why Model Speed Matters
For interactive AI applications, response speed can make or break the user experience. CAMEL-AI benchmarks tokens processed per second (TPS) across a range of supported models—helping you choose the right balance of power and performance.
Benchmark Insights
We ran side-by-side tests in this notebook comparing top models from OpenAI (GPT-4o Mini, GPT-4o, O1 Preview) and SambaNova (Llama series), measuring output speed in tokens per second.
Key Findings:
Small models = blazing speed: SambaNova’s Llama 8B and OpenAI GPT-4o Mini deliver the fastest responses.
Bigger models = higher quality, slower output: Llama 405B (SambaNova) and similar large models trade off speed for more nuanced reasoning.
OpenAI models = consistent speed: Most OpenAI models maintain stable throughput across use cases.
Llama 8B (SambaNova) = top performer: Outpaces others in raw tokens/sec.
