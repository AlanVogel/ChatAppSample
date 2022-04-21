from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    create_engine,
    ForeignKey,
    UniqueConstraint,
    and_,
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
        return "<User(nick_name='{}', password='{}', email='{}'," \
               "key_word='{}')>" \
            .format(self.nick_name, self.password, self.email, self.key_word)


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
        return "<Message(msg='{}', created_at='{}', sender_id='{}')>" \
            .format(self.msg, self.created_at, self.sender_id)


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    conversation_name = Column(String(32), nullable=False)
    UniqueConstraint(conversation_name)

    def __repr__(self):
        return "<Conversation(conversation_name='{}')>" \
            .format(self.conversation_name)


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
    session.add(
        User(nick_name=data.get('nick_name'), password=data.get('password'),
             email=data.get('email')))
    session.commit()


def get_user_by_id(session: Session, id_: int) -> User:
    return session.query(User).filter(User.id == id_).first()


def get_user_by_email(session: Session, email: str) -> User:
    return session.query(User).filter(User.email == email).first()


def get_user_by_name(session: Session, name: str) -> User:
    return session.query(User).filter(User.nick_name == name).first()


def update_user(session: Session, user_: User, **kwargs):
    return session.query(User).filter(User.id == user_.id).update(kwargs)


def update_conversation(session: Session, conv_: Conversation, **kwargs):
    return session.query(Conversation).filter(
        Conversation.id == conv_.id).update(kwargs)


def get_conversation_by_room_name(session: Session,
                                  room_name: str) -> Conversation:
    return session.query(Conversation).filter(
        Conversation.conversation_name == room_name).first()


def get_all_users(session: Session) -> User:
    return session.query(User).all()


def add_message(session: Session, data, created_at, sender_id):
    session.add(Message(msg=data.get('msg'), created_at=created_at,
                        sender_id=sender_id))


def get_message_by_msg(session: Session, msg: str) -> Message:
    return session.query(Message).filter(Message.msg == msg).first()


def get_message_by_user_id(session: Session, id_: int) -> Message:
    return session.query(Message).filter(Message.id == id_).first()


def add_conversation(session: Session, data):
    session.add(Conversation(conversation_name=data.get('room_name')))


def add_conv_user(session: Session, user_id: int, conv_id: int):
    session.add(ConversationUser(user_id=user_id, conv_id=conv_id))
    session.commit()


def add_conv_msg(session: Session, user_id: int, conv_id: int):
    session.add(ConversationUser(user_id=user_id, conv_id=conv_id))
    session.commit()


def get_conv_user_by_ids(session: Session, id_: int,
                         room_id: int) -> ConversationUser:
    return session.query(ConversationUser).filter(
        ConversationUser.user_id == id_,
        ConversationUser.conversation_id == room_id).first()


def get_conv_user_by_user_id(session: Session, id_: int) -> ConversationUser:
    return session.query(ConversationUser).filter(
        ConversationUser.user_id == id_).first()


def get_all_conv_user_by_user_id(session: Session,
                                 id_: int) -> ConversationUser:
    return session.query(ConversationUser).filter(
        ConversationUser.user_id == id_).all()


def get_conversation_by_id(session: Session, id_: int) -> Conversation:
    return session.query(Conversation).filter(Conversation.id == id_).first()


def delete_conversation_by_id(session: Session, id_: int):
    con = session.query(Conversation).filter(Conversation.id == id_).first()
    return session.delete(con)


def delete_message_by_id(session: Session, id_: int, sender: int):
    msg = session.query(Message).filter(
        and_(Message.id == id_, Message.sender_id == sender)).first()
    return session.delete(msg)
