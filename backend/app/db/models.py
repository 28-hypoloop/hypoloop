from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    hypothesis_id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    u_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    max_experiments = Column(Integer, nullable=False)
    parallel_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiments = relationship(
        "Experiment", back_populates="hypothesis", cascade="all, delete-orphan"
    )


class Experiment(Base):
    __tablename__ = "experiments"

    exp_id = Column(String, primary_key=True)
    hypothesis_id = Column(
        String, ForeignKey("hypotheses.hypothesis_id"), nullable=False, index=True
    )
    score = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="ready")  # ready/running/done/failed
    analysis_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    hypothesis = relationship("Hypothesis", back_populates="experiments")
