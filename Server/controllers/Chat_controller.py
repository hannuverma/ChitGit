from sqlmodel import SQLModel, Session, create_engine
from SQLModel import Conversation, Message
from pydanticModels import Message, Conversation


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


def upload_chat_to_DB(Message: Message):
    with Session(engine) as session:
        db_message = Message(
            conversation_id=Message.conversation_id,
            role=Message.role,
            content=Message.content
        )
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
    return db_message