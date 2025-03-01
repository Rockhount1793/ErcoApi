from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Request models
class InvoiceCalculationRequest(BaseModel):
    client_id: int
    month: int
    year: int

class ConceptCalculation(BaseModel):
    quantity: float
    tariff: float
    total: float

class ConceptResponseEE2(BaseModel):
    quantity: float
    registers: list
    total: float    

class InvoiceCalculationResponse(BaseModel):
    client_id: int
    month: int
    year: int
    EA: ConceptCalculation
    EC: ConceptCalculation
    EE1: ConceptCalculation
    EE2: ConceptResponseEE2
    total: float

class HourlySystemLoad(BaseModel):
    hour: int
    load: float

class SystemLoadResponse(BaseModel):
    date: datetime
    hourly_loads: List[HourlySystemLoad]

class ClientStatistic(BaseModel):
    month: int
    year: int
    consumption: float
    injection: float
    net: float

class ClientStatisticsResponse(BaseModel):
    client_id: int
    monthly_statistics: List[ClientStatistic]
    average_consumption: float
    average_injection: float
    average_net: float

class ConceptResponse(BaseModel):
    concept: str
    quantity: float
    rate: float
    total: float
