from agents import Agent, Runner, WebSearchTool, function_tool

@function_tool 
async def read_file(file_name: str) -> list[str]:
    """Read the contents of a file.
    
    Args:
        file_name: The name to the file to read.

    Returns:
        The content of the file.
    """
    with open(file_name, "r") as file_content:
        return file_content.readlines()

@function_tool
def append_file(content : str):
    """Append the content to a file."

    Args:
        content: The content to append to the file.
        
    """
    with open("questions.txt", "a") as file_content:
        file_content.write(content + "\n")

@function_tool
def convert_to_array(content: str) -> list[str]:
    """Convert the input string to an array of strings delimited by newline.

    Args:
        content: The content to convert to an array.

    Returns:
        The content converted to an array of strings with asterisks removed.
    """
    content = content.replace("*", "")
    return content.splitlines()

@function_tool
def compare_text(array1: list[str], array2: list[str]) -> bool:
    """Check if any element in the first array is present in the second array.

    Args:
        array1: The first string array.
        array2: The second string array.

    Returns:
        True if any element in array1 is present in array2, False otherwise.
    """
    return any(item in array2 for item in array1)

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
    "First read all the lines from the file 'questions.txt'. as the first array of strings. "
    "Then convert the input questions as the second array of strings. "
    "Then you will compare the seconds array of strings if any one is present in the first array of strings. "
    "If yes, then respond exactly as 'The questions are same' else handoff to the persist agent to append the questions to the file."
    "If there are no pre existing questions, handoff to the persist agent to append the questions to the file.",
    tools=[read_file, compare_text, convert_to_array],
    handoffs=[persist_agent]
)

research_agent = Agent(
    name="Research Agent",
    model="gpt-4o",
    instructions="You are a helpful research assistant. "
    "You will research the web for sample questions and answers for a particular maths topic. "
    # "Provide the questions first and then the answers in separate sections, exactly in this manner."
    "For answers Do not provide the solution, just the answer."
    "Print all the questions first and then print all the answers, exactly in this manner."
    "Then handoff to the Validation Agent with only the questions as input. "
    ,
    handoffs=[validation_agent],
    tools=[WebSearchTool()]
)

# while True:
research_results = Runner.run_sync(research_agent, f"Provide 5 questions with answers on two step equations word problems.")
research_info = research_results.final_output

print(f"Validation Agent Response: {research_info}")