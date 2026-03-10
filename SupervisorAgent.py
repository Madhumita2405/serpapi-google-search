import os, getpass
from dotenv import load_dotenv
load_dotenv()
hf = getpass.getpass("Enter your HF token: ")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
endpoint = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation"
)

llm = ChatHuggingFace(llm=endpoint)
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()
search.invoke("what is AI")

def search_ddgo(query: str):
    """Search the web using DuckDuckGo."""
    search = DuckDuckGoSearchRun()
    return search.invoke(query)

def add(a: float, b: float):
    """Add two numbers together."""
    return a + b

def multiply(a: float, b: float):
    """Multiply two numbers together."""
    return a * b
math_agent = create_react_agent(
    model=llm,
    tools=[add, multiply],
    name="math_agent"
)
research_agent = create_react_agent(
    model=llm,
    tools=[search_ddgo],
    name="res_agent"
)
from langgraph_supervisor import create_supervisor
workflow = create_supervisor(
    [research_agent, math_agent],
    model=llm,
    prompt=(
        "You are a team supervisor managing a research expert and a math expert. "
        "For current events, use res_agent. "
        "For math, use math_agent."
    )
)
app = workflow.compile()
result = app.invoke({
    "messages": [{"role": "user", "content": "what is quantum computing ?"}]
})
print(result)
print(result['messages'][-1].content)
from typing import TypedDict, Annotated, List
from langchain_core.agents import AgentFinish
from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage, AIMessage
import operator
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_agent: str
def agent_node(state, agent, name):
    result = agent.invoke({"messages": state["messages"]})

    if isinstance(result, AgentFinish):
        return {
            "messages": [AIMessage(content=result.return_values["output"], name=name)],
            "current_agent": "supervisor",
        }
    else:
        return {
            "messages": result["messages"],
            "current_agent": "supervisor",
        }
def supervisor_node(state: AgentState):
    last_message = state["messages"][-1]
    if isinstance(last_message, dict):
        content = last_message["content"].lower()
    else:
        content = last_message.content.lower()

    if any(keyword in content for keyword in ["multiply", "add", "math"]):
        return {"current_agent": "math_agent"}

    elif any(keyword in content for keyword in ["temperature", "what is", "research"]):
        return {"current_agent": "res_agent"}

    else:
        return {"current_agent": "res_agent"}

workflow = StateGraph(AgentState)

workflow.add_node("res_agent", lambda state: agent_node(state, research_agent, "res_agent"))
workflow.add_node("math_agent", lambda state: agent_node(state, math_agent, "math_agent"))
workflow.add_node("supervisor", supervisor_node)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["current_agent"],
    {
        "res_agent": "res_agent",
        "math_agent": "math_agent",
    }
)

workflow.add_edge("res_agent", "supervisor")
workflow.add_edge("math_agent", "supervisor")
app = workflow.compile()
result = app.invoke({
    "messages": [{"role": "user", "content":
        "what is the temperature in Delhi ? Multiply the temperature by 2 and then add 3 to the result"}],
    "current_agent": "supervisor"
})
print(result)
