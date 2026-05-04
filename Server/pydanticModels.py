from pydantic import BaseModel
from typing import List, Literal, Optional

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    related_file: Optional[str] = None

class RepoChunks(BaseModel):
    repo_id: str
    repo_name: str
    file_path: str
    content: str
    chunk_index: int
    language: Optional[str] = None

class repoUrl(BaseModel):
    url: str


class Conversation(BaseModel):
    id: Optional[int] = None
    repo_url: str
    messages: List[ChatMessage]

class Message(BaseModel):
    id: Optional[int] = None
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str


class sendChatRequest(BaseModel):
    repo_url: str
    query: str
    role: Literal["user", "assistant"]
    conversation_id: int