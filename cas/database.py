from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    create_engine,
    ForeignKey,
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
    email = Column(String(32), nullable=False)
    key_word = Column(String(32), nullable=False)

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


class ConversationUser(Base):
    __tablename__ = "user_conversations"
    id = Column(Integer, primary_key=True)
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
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
