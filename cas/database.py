from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    create_engine,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
)

Base = declarative_base()
DATABASE_URI = 'postgresql+psycopg2://postgres:admin@localhost:5432' \
               '/SimpleChat'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()


# For testing
def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    nick_name = Column(String(32), nullable=False)
    password = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False)
    key_word = Column(String(64), nullable=True)
    UniqueConstraint(nick_name, email)

    def __repr__(self):
        return "<User(nick_name='{}', email='{}', key_word={})>" \
            .format(self.nick_name, self.email, self.key_word)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    msg = Column(String(32), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    # Foreign key
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # Relationship
    user = relationship("User", foreign_keys=[sender_id])

    def __repr__(self):
        return "<Message(msg='{}', created_at='{}', sender_id={})>" \
            .format(self.msg, self.created_at, self.sender_id)


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    conversation_name = Column(String(32), nullable=False)
    joined = Column(Boolean, default=False, nullable=False)
    UniqueConstraint(conversation_name, joined)


class ConversationUser(Base):
    __tablename__ = "user_conversations"
    id = Column(Integer, primary_key=True)
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    conversation_id = Column(Integer, ForeignKey("conversations.id",
                                                 ondelete="CASCADE"))
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    conversation = relationship("Conversation", foreign_keys=[conversation_id])


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    id = Column(Integer, primary_key=True)
    # Foreign keys
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"))
    conversation_id = Column(Integer, ForeignKey("conversations.id",
                                                 ondelete="CASCADE"))
    # Relationships
    message = relationship("Message", foreign_keys=[message_id])
    conversation = relationship("Conversation", foreign_keys=[conversation_id])


def add_user(session: Session, data):
    session.add(User(nick_name=data.get('nick_name'), email=data.get('email'),
                     key_word=data.get('key_word')))
    session.commit()


def get_user_by_id(session: Session, id_: int) -> User:
    return session.query(User).filter(User.id == id_).first()


def get_user_by_email(session: Session, email: str) -> User:
    return session.query(User).filter(User.email == email).first()


def update_user(session: Session, user_: User, **kwargs):
    return session.query(User).filter(User.id == user_.id).update(kwargs)


def update_conversation(session: Session, conv_: Conversation, **kwargs):
    return session.query(Conversation).filter(
        Conversation.id == conv_.id).update(kwargs)


def get_all_users(session: Session) -> User:
    return session.query(User).all()


def add_message(session: Session, data, created_at):
    session.add(Message(msg=data.get('msg'), created_at=created_at,
                        sender_id=data.get('sender_id')))
    session.commit()


def get_message_by_id(session: Session, id_: int) -> Message:
    return session.query(Message).filter(Message.id == id_).first()


def add_conversation(session: Session, data):
    session.add(Conversation(conversation_name=data.get('conversation_name')))
    session.commit()


def get_conversation_by_id(session: Session, id_: int) -> Conversation:
    return session.query(Conversation).filter(Conversation.id == id_).all()


def delete_conversation_by_id(session: Session, id_: int):
    return session.query(Conversation).filter(Conversation.id == id_).delete()


def delete_message_by_id(session: Session, id_: int):
    return session.query(Message).filter(Message.id == id_).delete()
