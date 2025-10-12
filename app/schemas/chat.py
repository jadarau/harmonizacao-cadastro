from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, validator

Role = Literal["system", "user", "assistant", "tool"]

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    stream: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

    @validator("messages")
    def validate_messages(cls, v: List[Message]):
        if not v:
            raise ValueError("messages must not be empty")
        return v

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class Usage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None
