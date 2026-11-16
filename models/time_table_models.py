import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy import Boolean, DateTime, false, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from database import Base


class Teacher(Base):
    __tablename__ = "teachers" # name of the table in the real database

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    available_times = Column(JSON, nullable=True)

    # relationship is a pythonic solution for moving between objects of connected tables
    user = relationship("User", back_populates="teachers")
    user_teacher_course_relation = relationship("UserTeacherCourseRelation", back_populates="teacher")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    cohort = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)

    user = relationship("User", back_populates="courses")
    user_teacher_course_relation = relationship("UserTeacherCourseRelation", back_populates="course")


class UserTeacherCourseRelation(Base):
    __tablename__ = "user_teacher_course_relations"
    __table_args__ = (
        UniqueConstraint("user_id", "teacher_id", "course_id", name="uq_user_teacher_course"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="user_teacher_course_relation")
    teacher = relationship("Teacher", back_populates="user_teacher_course_relation")
    course = relationship("Course", back_populates="user_teacher_course_relation")


class TaskCharge(Base):
    """One row per started task. Records the charge and prevents double refunds."""
    __tablename__ = "task_charges"

    task_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    # default=False for defining default value at python level, server_default=false() for 
    # defining default value at database level like running sql cmd directly
    refunded = Column(Boolean, nullable=False, default=False, server_default=false())
    # func is used to call SQL functions(like COUNT(), MIN(), NOW(), ...) from Python using SQLAlchemy.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
