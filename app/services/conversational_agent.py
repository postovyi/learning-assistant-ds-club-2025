from agents import Runner
from agents.extensions.memory import SQLAlchemySession
from app.core.agents_init import create_learning_assistant
from app.core.db import engine

class ConversationalAgent:
    def __init__(self):
        self.agent = create_learning_assistant()
        self.sessions = {}  # Cache SQLAlchemySession objects by session_id

    def _get_or_create_session(self, session_id: str) -> SQLAlchemySession:
        """Get existing cached session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = SQLAlchemySession(
                session_id,
                engine=engine,
                create_tables=True
            )
        return self.sessions[session_id]

    async def send_message(self, session_id: str, message: str, vector_store_id: str = None) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            session_id: Unique identifier for the conversation session
            message: User's message
            vector_store_id: Optional vector store ID for file search
            
        Returns:
            Agent's response text
        """
        # Get or create SQLAlchemy session for persistent conversation history
        session = self._get_or_create_session(session_id)
        
        # Configure tool resources if vector store is provided
        tool_resources = None
        if vector_store_id:
            tool_resources = {
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        
        # Run the agent with the message
        result = await Runner.run(
            starting_agent=self.agent,
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
        session = self._get_or_create_session(session_id)
        
        async for chunk in Runner.run_stream(
            starting_agent=self.agent,
            input=message,
            session=session
        ):
            if chunk.type == "text":
                yield chunk.data
