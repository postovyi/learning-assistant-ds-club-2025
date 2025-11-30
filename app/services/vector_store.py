import os
from openai import AsyncOpenAI
from fastapi import UploadFile

class VectorStoreService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def create_vector_store(self, name: str):
        """Create a new vector store."""
        vector_store = await self.client.vector_stores.create(name=name)
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
            await self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=openai_file.id
            )
            return openai_file
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    async def upload_bytes(self, filename: str, data: bytes, vector_store_id: str):
        """Upload in-memory bytes as a file to the vector store."""
        temp_filename = filename
        with open(temp_filename, "wb") as f:
            f.write(data)

        try:
            with open(temp_filename, "rb") as f:
                openai_file = await self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            await self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=openai_file.id
            )
            return openai_file
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    async def list_files(self, vector_store_id: str):
        """List files in a vector store."""
        return await self.client.vector_stores.files.list(vector_store_id=vector_store_id)

    async def get_or_create_vector_store(self, name: str) -> str:
        """Get a vector store by name or create it if it doesn't exist."""
        # List vector stores (pagination might be needed in prod, but simple for now)
        vector_stores = await self.client.vector_stores.list(limit=100)
        for vs in vector_stores.data:
            if vs.name == name:
                return vs.id
        
        # Create if not found
        vs = await self.create_vector_store(name)
        return vs.id
