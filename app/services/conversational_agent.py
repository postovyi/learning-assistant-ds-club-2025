from agents import Runner, Session
from app.core.agents_init import create_learning_assistant

class ConversationalAgent:
    def __init__(self):
        self.agent = create_learning_assistant()

    async def send_message(self, session_id: str, message: str) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            session_id: Unique identifier for the conversation session
            message: User's message
            
        Returns:
            Agent's response text
        """
        # Create or retrieve session
        session = Session(id=session_id)
        
        # Run the agent with the message
        result = await Runner.run(
            agent=self.agent,
            input=message,
            session=session
        )
        
        return result.final_output
    
    async def send_message_streaming(self, session_id: str, message: str):
        """
        Send a message to the agent and stream the response.
        
        Args:
            session_id: Unique identifier for the conversation session
            message: User's message
            
        Yields:
            Chunks of the agent's response
        """
        session = Session(id=session_id)
        
        async for chunk in Runner.run_stream(
            agent=self.agent,
            input=message,
            session=session
        ):
            if chunk.type == "text":
                yield chunk.data

