from pydantic import BaseModel

class Response_bot(BaseModel):
    history: list

class Response_chat_database(BaseModel):
    chat_name: str
    chat_history: list
