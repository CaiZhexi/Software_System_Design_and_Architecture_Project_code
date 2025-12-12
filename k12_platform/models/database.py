"""数据库模型定义"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(128))
    email = Column(String(100))
    grade = Column(String(20))  # 年级
    subjects = Column(String(200))  # 偏好学科，逗号分隔
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    
    # 关系
    questions = relationship("Question", back_populates="user")
    essays = relationship("Essay", back_populates="user")
    wrong_questions = relationship("WrongQuestion", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


class Question(Base):
    """问题表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)  # 问题内容
    image_url = Column(String(500))  # 图片URL
    subject = Column(String(50))  # 学科
    knowledge_point = Column(String(100))  # 知识点
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False)


class Answer(Base):
    """答案表"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    content = Column(Text)  # 答案内容
    steps = Column(Text)  # 分步骤解析 (JSON格式)
    is_correct = Column(Boolean, default=None)  # 用户标记是否理解
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    question = relationship("Question", back_populates="answer")


class Essay(Base):
    """作文表"""
    __tablename__ = "essays"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    content = Column(Text)
    essay_type = Column(String(50))  # 作文类型
    
    # 评价结果
    overall_score = Column(Float)
    structure_feedback = Column(Text)
    grammar_feedback = Column(Text)
    vocabulary_feedback = Column(Text)
    suggestions = Column(Text)
    topic_analysis = Column(Text)  # 审题立意解读 (JSON格式)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="essays")


class WrongQuestion(Base):
    """错题本"""
    __tablename__ = "wrong_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    error_reason = Column(Text)  # 错误原因
    practice_count = Column(Integer, default=0)  # 练习次数
    is_mastered = Column(Boolean, default=False)  # 是否已掌握
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="wrong_questions")
    question = relationship("Question")


class ChatSession(Base):
    """聊天会话"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """聊天消息"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String(20))  # user/assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")


class Exercise(Base):
    """推荐练习题库"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50))
    knowledge_point = Column(String(100))
    difficulty = Column(Integer)  # 1-5
    content = Column(Text)
    answer = Column(Text)
    explanation = Column(Text)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
