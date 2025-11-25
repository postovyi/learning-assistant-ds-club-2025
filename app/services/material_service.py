from uuid import UUID
from fastapi import HTTPException, UploadFile
from app.repos.chat_repo import SessionRepo
from app.repos.content_repo import MaterialRepo
from app.models.content import Material
from app.services.vector_store import VectorStoreService
from app.enums.db_enums import FileType

class MaterialService:
    def __init__(
        self,
        session_repo: SessionRepo,
        material_repo: MaterialRepo,
        vector_store_service: VectorStoreService
    ):
        self.session_repo = session_repo
        self.material_repo = material_repo
        self.vector_store_service = vector_store_service

    async def upload_material(
        self,
        session_id: UUID,
        user_id: UUID,
        file: UploadFile
    ) -> Material:
        """Upload a learning material to a session."""
        # Verify session belongs to user
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Determine file type
        file_extension = file.filename.split(".")[-1].lower()
        file_type_map = {
            "pdf": FileType.PDF,
            "docx": FileType.DOCX,
            "txt": FileType.TXT,
            "png": FileType.IMAGE,
            "jpg": FileType.IMAGE,
            "jpeg": FileType.IMAGE,
        }
        file_type = file_type_map.get(file_extension, FileType.OTHER)

        # Create vector store for this session
        vector_store_name = f"session_{session_id}"
        vector_store = await self.vector_store_service.create_vector_store(vector_store_name)

        # Upload file to OpenAI
        openai_file = await self.vector_store_service.upload_file(file, vector_store.id)

        # Save material to DB
        material = await self.material_repo.create(
            session_id=session_id,
            name=file.filename,
            file_url=openai_file.id,
            file_type=file_type,
            size=file.size or 0
        )

        return material

    async def get_session_materials(self, session_id: UUID, user_id: UUID) -> list[Material]:
        """Get all materials for a session."""
        # Verify session belongs to user
        session = await self.session_repo.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")

        return await self.material_repo.get_by_session(session_id)
