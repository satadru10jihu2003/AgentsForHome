from agents import Agent, Runner, WebSearchTool, handoffs

def read_file(file_path):
    with open(file_path, "r") as file_content:
        return file_content.read()

validation_agent = Agent(
    name="Validation Agent",
    model="gpt-4o",
    instructions="You are a helpful validation assistant. "
    f"You will validate the questions provided in the input text if they are similar to pre existing questions defined in {read_file("questions.txt")}",
    tools=[WebSearchTool()]
)

# Research Agent (unchanged)
research_agent = Agent(
    name="Research Agent",
    model="gpt-4o",
    instructions="You are a helpful research assistant. "
    "You will research the web for sample questions and answers for a particular maths topic. "
    "Provide the questions first and then the answers in separate sections."
    "For answers Do not provide the solution, just the answer."
    "After retrieving questions handoff to the Validation Agent to validate if the questions are similar to pre existing questions.",
    handoffs=[validation_agent],
    tools=[WebSearchTool()]
)

# Create a vector store
#vector_store = create_vector_store()

# Add the file to the vector store
#file_id = open_file("questions.txt")
#add_file_to_vector_store(vector_store, file_id)

# Check the status of the vector store
#check_status(vector_store)

research_results = Runner.run_sync(research_agent, f"Provide 5 questions with answers on two step equations word problems.")
research_info = research_results.final_output

# preexisting_questions = read_file("questions.txt")

# validation_results = Runner.run_sync(validation_agent, f"Validate if any of the questions in the text {research_info} are similar to the pre existing questions provided here : {preexisting_questions}.")
# validation_info = validation_results.final_output

print(f"Research Agent Response: {research_info}")
# print(f"Validation Agent Response: {validation_info}")
