from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

router = APIRouter()

from app.database import get_db

from app.interfaces.responses import (
    InvoiceCalculationRequest,
    InvoiceCalculationResponse,
    ClientStatisticsResponse,
    SystemLoadResponse,
    ConceptResponse,
    ConceptResponseEE2
)

from app.utils.calculations import (
    calculate_all_concepts,
    calculate_EA,
    calculate_EC,
    calculate_EE1,
    calculate_EE2,
    get_client_statistics,
    get_system_load
)

#calculando factura OK
@router.post("/calculate-invoice", response_model=InvoiceCalculationResponse)
def calculate_invoice(request: InvoiceCalculationRequest,db: Session = Depends(get_db)):
    try:
        return calculate_all_concepts(db, request.client_id, request.year, request.month)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate invoice: {str(e)}")

#calculando estadistica OK
@router.get("/client-statistics/{client_id}", response_model=ClientStatisticsResponse)
def client_statistics(client_id: int,db: Session = Depends(get_db)):
    try:
        result = get_client_statistics(db, client_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get client statistics: {str(e)}")

@router.get("/system-load", response_model=SystemLoadResponse)
def system_load(date_str: Optional[str] = None,db: Session = Depends(get_db)):
    try:
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            target_date = datetime.now()

        result = get_system_load(db, target_date)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system load: {str(e)}")

#calculando EA por mes OK
@router.get("/calculate-ea/{client_id}", response_model=ConceptResponse)
def calculate_ea_endpoint(client_id: int,year: int,month: int,db: Session = Depends(get_db)):
    try:
        quantity, rate, total = calculate_EA(db, client_id, year, month)
        return {
            "concept": "EA",
            "quantity": quantity,
            "rate": rate,
            "total": total
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate EA: {str(e)}")

#calculando EC por mes OK
@router.get("/calculate-ec/{client_id}", response_model=ConceptResponse)
def calculate_ec_endpoint(client_id: int,year: int,month: int,db: Session = Depends(get_db)):
    try:
        quantity, rate, total = calculate_EC(db, client_id, year, month)
        return {
            "concept": "EC",
            "quantity": quantity,
            "rate": rate,
            "total": total
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate EC: {str(e)}")

#calculando EE1 por mes OK
@router.get("/calculate-ee1/{client_id}", response_model=ConceptResponse)
def calculate_ee1_endpoint(client_id: int,year: int,month: int,db: Session = Depends(get_db)):
    try:
        quantity, rate, total = calculate_EE1(db, client_id, year, month)
        return {
            "concept": "EE1",
            "quantity": quantity,
            "rate": rate,
            "total": total
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate EE1: {str(e)}")

#calculando EE2 por mes OK
@router.get("/calculate-ee2/{client_id}", response_model=ConceptResponseEE2)
def calculate_ee2_endpoint(client_id: int,year: int,month: int,db: Session = Depends(get_db)):
    
    try:
        quantity,registers,total = calculate_EE2(db, client_id, year, month)
        return {
            "concept": "EE2",
            "quantity": quantity,
            "registers": registers,
            "total": total
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate EE2: {str(e)}")