import os
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agent.src.graph.state import AgentState
from agent.src.tool import tools

load_dotenv()

SYSTEM_PROMPT = """You are an elite, autonomous Machine Learning Agent.
Your goal is to conduct an end-to-end ML experiment and write a report.

[ENVIRONMENT & CONTEXT]
- Project ID: {project_id}
- Hypothesis ID: {hypothesis_id}
- Hypothesis Directory: {hypothesis_dir}
- Experiment Directory: {exp_dir}

[CRITICAL INSTRUCTIONS]
1. Read the path_rules template: Use `read_file` to read `shared/templates/path_rules.md` and strictly follow its directory rules and read-only DB constraints.
2. Read the code templates: Use `read_file` to read `shared/templates/eda_template.py` and `shared/templates/train_template.py` to understand the mandatory code format.
3. Read the hypothesis configuration from `data/projects/{project_id}/hypotheses/{hypothesis_id}/u_id_{hypothesis_id}.yml` to understand the goal.
4. Data is in the SQLite DB `data/projects/{project_id}/data.db`. You can read it using a python script or sqlite query.
5. Write your EDA code to `{exp_dir}/eda.py` and execute it. Make sure images are saved to `{exp_dir}/img/`.
6. Write your Train code to `{exp_dir}/train.py` and execute it. Make sure MLflow logs correctly.
   **CRITICAL**: You MUST set the MLflow tracking URI to `sqlite:///{hypothesis_dir}/mlflow.db` so that all experiments for this hypothesis share the same database.
7. Finally, write a comprehensive experiment report to `{exp_dir}/report.md` summarizing the EDA findings, the model training results (Accuracy/Score), and whether the hypothesis was supported.
   **CRITICAL**: When embedding images in `report.md`, you MUST use relative paths (e.g., `![caption](img/target_distribution.png)`). Do NOT use absolute paths.

Remember to execute the python scripts using `execute_command` to verify they work and generate the expected artifacts.
"""

# Initialize Solar LLM
llm = ChatUpstage(model="solar-pro")
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm_with_tools
    
    # Fill system prompt with state variables
    res = chain.invoke({
        "project_id": state["project_id"],
        "hypothesis_id": state["hypothesis_id"],
        "hypothesis_dir": state["hypothesis_dir"],
        "exp_dir": state["exp_dir"],
        "messages": state["messages"]
    })
    
    return {"messages": [res]}

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    tool_node = ToolNode(tools)
    workflow.add_node("tools", tool_node)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
