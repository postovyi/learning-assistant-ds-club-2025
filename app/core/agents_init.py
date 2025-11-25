from agents import Agent

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
        tools=[]  # Tools will be added as needed
    )

