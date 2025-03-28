from typing import Annotated, Sequence, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import MessageGraph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import WebSearchTool

# Define the state
class AgentState(TypedDict):
    messages: Sequence[HumanMessage | AIMessage]
    input: str
    research_info: str
    validation_info: str

# Define tools
@tool
def read_file(file_name: str) -> str:
    """Read the contents of a file.

    Args:
        file_name: The name to the file to read.

    Returns:
        The content of the file.
    """
    with open(file_name, "r") as file_content:
        return file_content.read()

@tool
def append_file(content : str):
    """Append the content to a file."

    Args:
        content: The content to append to the file.

    """
    with open("questions.txt", "a") as file_content:
        file_content.write(content + "\n")

# Define models
model = ChatOpenAI(model="gpt-4o")

# Define prompts
research_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful research assistant. "
            "You will research the web for sample questions and answers for a particular maths topic. "
            "Provide the questions first and then the answers in separate sections."
            "For answers Do not provide the solution, just the answer."
            "Print the questions first and then the answers.",
        ),
        ("human", "{input}"),
    ]
)

validation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful validation assistant. "
            "First read the pre existing questions from the file 'questions.txt'."
            "Then you will validate the questions provided in the input text if they are same as pre existing questions. "
            "If the questions are same, provide the response as 'The questions are same' else handoff to the persist agent to append the questions to the file."
            "If there are no pre existing questions, handoff to the persist agent to append the questions to the file.",
        ),
        ("human", "Validate if any of the questions in the text {research_info} are similar to the pre existing questions provided here : {preexisting_questions}."),
    ]
)

persist_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant who appends the input to a given file. "
            "You will append the questions provided in the input text to a file named questions.txt. "
            "Then print the questions and answers.",
        ),
        ("human", "{input}"),
    ]
)

# Define tools
tools = [read_file, append_file, WebSearchTool()]
tool_executor = ToolExecutor(tools)

# Define nodes
def research_agent(state: AgentState):
    research_info = (
        research_prompt
        | model
        | StrOutputParser()
    ).invoke({"input": state["input"]})
    return {"research_info": research_info}

def validation_agent(state: AgentState):
    preexisting_questions = read_file("questions.txt")
    validation_info = (
        validation_prompt
        | model
        | StrOutputParser()
    ).invoke({"research_info": state["research_info"], "preexisting_questions": preexisting_questions})
    return {"validation_info": validation_info}

def persist_agent(state: AgentState):
    append_file(state["research_info"])
    return {"messages": [AIMessage(content="Questions appended to file.")]}

def route(state: AgentState):
    if "The questions are same" in state["validation_info"]:
        return "end"
    else:
        return "persist"

# Define graph
workflow = StateGraph(AgentState)

workflow.add_node("research", research_agent)
workflow.add_node("validation", validation_agent)
workflow.add_node("persist", persist_agent)

workflow.set_entry_point("research")

workflow.add_conditional_edges(
    "validation",
    route,
    {
        "persist": "persist",
        "end": END,
    },
)

workflow.add_edge("research", "validation")
workflow.add_edge("persist", END)

app = workflow.compile()

# Run the graph
inputs = {"input": "Provide 5 questions with answers on two step equations word problems."}
result = app.invoke(inputs)

print(f"Research Agent Response: {result['research_info']}")
print(f"Validation Agent Response: {result.get('validation_info', 'No validation performed.')}")
