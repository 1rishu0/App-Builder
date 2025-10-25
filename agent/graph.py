# Field is like a decorator for individual model attributes, giving you control over: defaults, validations, documentation metadata
# END is a Special marker indicating the end of a graph flow
# StateGraph is a Class for building and managing state-based graphs
# enables detailed debugging info for LangChain execution
# enables verbose logs showing step-by-step flow of LangChain
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agent.prompts import *
from agent.states import *
from agent.tools import *
from langgraph.constants import END
from langgraph.graph import StateGraph
from langchain.globals import set_debug, set_verbose

_ = load_dotenv()

set_debug(True)
set_verbose(True)

llm = ChatGroq(model="openai/gpt-oss-120b")

# define the function for the graph to use as node
# Think of state as a shared memory or a context object that keeps updating as your workflow moves from one node to another.
def planner_agent(state: dict)->dict:
    users_prompt = state["user_prompt"]

    # the output we get from llm is structured through schema class and proper planner prompt
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(users_prompt))

    # the return should always be dict
    # we are doing exception handling
    if resp is None:
        raise ValueError("Planner did not return a valid response")
    return {"plan":resp}

# here the state would be the return value of planner_agent and now it become state and architect agent again return dict
def architect_agent(state: dict)->dict:
    # by taking response from planner agent of type Plan we send it to architect_prompt for the proper suitable prompt for the agent
    plan: Plan = state["plan"]

    # now we initialize the llm.invoke with structured output of type taskplan for the agent
    resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))

    # now we are going to exception handling
    if resp is None:
        raise ValueError("Architect did not return a valid response")

    # return the dictionary and add plan to the resp through COnfigDict
    resp.plan = plan
    return {"task_plan": resp}

# this function is used to take the state from architect agent , process it and with schema and prompt for coder agent generate suitable response and return it in state format
def coder_agent(state: dict) -> dict:
    # we are going to get the coder_state key from the state which does not exist at first but later recursion it does
    # coder_state = state["coder_state"]
    coder_state = state.get("coder_state",None)

    # check if coder_state is None so we can add the coder state class in the first place
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"],current_step_idx=0)

    # first we are going take implementation_steps from task_plan which have both implementation_steps and plan which is in coder_state
    steps = coder_state.task_plan.implementation_steps

    # if the current_step_idx of coder_state is equal or greater than len(steps) then just return the dict with coder_state and status
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    # set the current task
    current_task = steps[coder_state.current_step_idx]

    # reads and stores the existing content from the given file path
    existing_content = read_file.run(current_task.filepath)

    # user prompt will be the task description and file path of the current_task
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )
    # we will take prompt function from prompts.py file
    # so there are supposed to be two prompts one is system_prompt and other is user_prompt
    system_prompt = coder_system_prompt()

    # we are getting all the functions from the tools.py file
    coder_tools = [read_file, write_file, list_files, get_current_directory]

    # create_react_agent creates an AI agent that reasons and acts using tools to answer user queries
    react_agent = create_react_agent(llm, coder_tools)

    # runs the ReAct agent with system and user prompts as input messages
    react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}]})

    # increase the step
    coder_state.current_step_idx += 1

    # return the empty dict
    return {"coder_state": coder_state}

# define a simple state graph and set parameter to dictionary
graph = StateGraph(dict)

# add node to the graph
graph.add_node("planner", planner_agent)
# add another node in the graph for architect plan
graph.add_node("architect", architect_agent)
# add another node in the graph for coder agent to create the code by taking result from architect agent
graph.add_node("coder", coder_agent)

# connect planner node to architect node in the workflow
graph.add_edge("planner", "architect")
# connect the architect node to coder node in the workflow
graph.add_edge("architect", "coder")

# add the conditional edge here with the condition that if the status is DONE then END the graph but if not then go back to coder itself
graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status",None) == "DONE" else "coder",
    {"END":END, "coder":"coder"}
)

# there may be multiple nodes in the graph so to set the entrypoint from which the workflow should start we write the name of that node
graph.set_entry_point("planner")

# compile and run the graph
agent = graph.compile()

if __name__ == "__main__":
    user_prompt = "create a simple calculator web application"

    # agent is ready to invoke with state dict
    result = agent.invoke({"user_prompt": user_prompt},
                          {"recursion_limit": 100})
    print(result)