from sqlmodel import SQLModel, Session, create_engine
from Model import Conversation as ConversationTable, Message as MessageTable
from pydanticModels import Message as MessageSchema


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

def create_conversation(repo_url:str):
    repo_name = repo_url.split('github.com/')[-1].removesuffix('.git')
    with Session(engine) as session:
        conversation = ConversationTable(repo_name=repo_name)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    return conversation

def upload_chat_to_DB(message: MessageSchema):
    with Session(engine) as session:
        db_message = MessageTable(
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content
        )
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
    return db_message