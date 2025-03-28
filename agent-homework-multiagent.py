from agents import Agent, Runner, WebSearchTool, function_tool

@function_tool 
async def read_file(file_name: str) -> str:
    """Read the contents of a file.
    
    Args:
        file_name: The name to the file to read.

    Returns:
        The content of the file.
    """
    with open(file_name, "r") as file_content:
        return file_content.read()

@function_tool
def append_file(content : str):
    """Append the content to a file."

    Args:
        content: The content to append to the file.
        
    """
    with open("questions.txt", "a") as file_content:
        file_content.write(content + "\n")

persist_agent = Agent(
    name="Persist Agent",
    model="gpt-4o",
    instructions="You are a helpful assistant who appends the input to a given file. "
    "You will append the questions provided in the input text to a file named questions.txt. "
    "Then print the questions and answers.",
    tools=[append_file]
)

validation_agent = Agent(
    name="Validation Agent",
    model="gpt-4o",
    instructions="You are a helpful validation assistant. "
    "First read the text from the file 'questions.txt'."
    "Then you will validate the questions provided in the input text if they are present in the text. "
    "If yes, then respond exactly as 'The questions are same' else handoff to the persist agent to append the questions to the file."
    "If there are no pre existing questions, handoff to the persist agent to append the questions to the file.",
    tools=[read_file],
    handoffs=[persist_agent]
)

research_agent = Agent(
    name="Research Agent",
    model="gpt-4o",
    instructions="You are a helpful research assistant. "
    "You will research the web for sample questions and answers for a particular maths topic. "
    "Provide the questions first and then the answers in separate sections."
    "For answers Do not provide the solution, just the answer."
    "Print the questions first and then the answers."
    "After retrieving questions handoff to the Validation Agent to validate if the questions are same as pre existing questions.",
    handoffs=[validation_agent],
    tools=[WebSearchTool()]
)

while True:
    research_results = Runner.run_sync(research_agent, f"Provide 5 questions with answers on two step equations word problems.")
    research_info = research_results.final_output

    print(f"Research Agent Response: {research_info}")

    if "The questions are same" in research_info:
        print("inside if")
        research_results = Runner.run_sync(research_agent, f"Provide 5 questions with answers on two step equations word problems.")
        research_info = research_results.final_output
    else:
        break

# preexisting_questions = read_file("questions.txt")

# validation_results = Runner.run_sync(validation_agent, f"Validate if any of the questions in the text {research_info} are similar to the pre existing questions provided here : {preexisting_questions}.")
# validation_info = validation_results.final_output

# print(f"Validation Agent Response: {validation_info}")