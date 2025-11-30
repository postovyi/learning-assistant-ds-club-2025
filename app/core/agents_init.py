from agents import Agent
from agents.tool import FileSearchTool

def create_learning_assistant() -> Agent:
    """
    Create the main learning assistant agent using the openai-agents SDK.
    """
    return Agent(
        name="Learning Assistant",
        instructions="""You are a helpful learning assistant for the DS Club. 
You help students with their homework, lessons, and understanding course materials.
You can search through uploaded materials to provide accurate answers.""",
        model="gpt-4o",
        tools=[FileSearchTool(vector_store_ids=["vs_692a19c6c540819188d01143f07e604e"])])

