from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, PrimaryKeyConstraint,func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Injection(Base):
    __tablename__ = "injection"

    id_record = Column(Integer, ForeignKey("records.id_record"), primary_key=True)
    value = Column(Float)

    record = relationship("Record", back_populates="injection")


class Record(Base):
    __tablename__ = "records"

    id_record = Column(Integer, primary_key=True, index=True)
    id_service = Column(Integer, ForeignKey("services.id_service"))
    record_timestamp = Column(DateTime, default=func.now())

    service = relationship("Service", back_populates="records")
    injection = relationship("Injection", back_populates="record", uselist=False)
    consumption = relationship("Consumption", back_populates="record", uselist=False)


class Service(Base):
    __tablename__ = "services"

    id_service = Column(Integer, primary_key=True, index=True)
    id_market = Column(Integer)
    cdi = Column(Integer)
    voltage_level = Column(Integer)

    records = relationship("Record", back_populates="service")


class Tariff(Base):
    __tablename__ = "tariffs"

    id_market = Column(Integer, primary_key=True)
    cdi = Column(Integer, primary_key=True)
    voltage_level = Column(Integer, primary_key=True)
    G = Column(Float)
    T = Column(Float)
    D = Column(Float)
    R = Column(Float)
    C = Column(Float)
    P = Column(Float)
    Cu = Column(Float,name="CU")

    __table_args__ = (
        PrimaryKeyConstraint('id_market', 'cdi', 'voltage_level'),
    )


class Consumption(Base):
    __tablename__ = "consumption"

    id_record = Column(Integer, ForeignKey("records.id_record"), primary_key=True)
    value = Column(Float)

    record = relationship("Record", back_populates="consumption")


class XmDataHourlyPerAgent(Base):
    __tablename__ = "xm_data_hourly_per_agent"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_timestamp = Column(DateTime)
    value = Column(Float)