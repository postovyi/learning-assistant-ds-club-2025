import os
from openai import AsyncOpenAI
from fastapi import UploadFile

class VectorStoreService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def create_vector_store(self, name: str):
        """Create a new vector store."""
        vector_store = await self.client.beta.vector_stores.create(name=name)
        return vector_store

    async def upload_file(self, file: UploadFile, vector_store_id: str):
        """Upload a file to the vector store."""
        # We need to save the file temporarily to upload it, or use a stream if supported
        # OpenAI API usually requires a file-like object with a name or a path
        
        # For now, let's assume we save it to a temp location
        temp_filename = file.filename
        with open(temp_filename, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            with open(temp_filename, "rb") as f:
                # Upload file to OpenAI
                openai_file = await self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            
            # Add file to vector store
            await self.client.beta.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=openai_file.id
            )
            return openai_file
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    async def list_files(self, vector_store_id: str):
        """List files in a vector store."""
        return await self.client.beta.vector_stores.files.list(vector_store_id=vector_store_id)
