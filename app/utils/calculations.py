from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import calendar
from typing import Tuple, Dict, List
from app.models.models import Service, Consumption, Injection, Record, Tariff, XmDataHourlyPerAgent

# devolver primer y último día del mes OK
def get_month_date_range(year: int, month: int) -> Tuple[datetime, datetime]:
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
    return first_day, last_day

# calcular solo suma de Consumption value OK
def calculateSumConsumption(db: Session, client_id: int, year: int, month: int) ->float:
    first_day, last_day = get_month_date_range(year, month)
    return db.query(func.sum(Consumption.value)).join(
        Record
    ).filter(
        Record.id_service == client_id,
        Record.record_timestamp >= first_day,
        Record.record_timestamp <= last_day
    ).scalar() or 0.0

# calcular solo suma de Injectiontion value OK
def calculateSumInjection(db: Session, client_id: int, year: int, month: int) ->float:
    first_day, last_day = get_month_date_range(year, month)
    return db.query(func.sum(Injection.value)).join(
        Record
    ).filter(
        Record.id_service == client_id,
        Record.record_timestamp >= first_day,
        Record.record_timestamp <= last_day
    ).scalar() or 0.0

# calcular EA OK
def calculate_EA(db: Session, client_id: int, year: int, month: int) -> Tuple[float, float, float]:
    # Se obtiene servicio relacionado al cliente
    service = db.query(Service).filter(Service.id_service == client_id).first()
    if not service:
        raise ValueError(f"Client with ID {client_id} not found")

    # Consumo en un rango de mes por usuario
    
    total_consumption = calculateSumConsumption(db,client_id,year,month)
    tariff = db.query(Tariff).filter(
        Tariff.id_market == service.id_market,
        Tariff.voltage_level == service.voltage_level
    )

    # filtramos por cdi solo si voltage_level no es 2 o 3
    if service.voltage_level not in [2,3]:
        tariff = tariff.filter(Tariff.cdi == service.cdi)

    tariff = tariff.first()

    if not tariff:
        raise ValueError("Tariff not found for the given service parameters")
    cu_rate = tariff.Cu
    return total_consumption, cu_rate, total_consumption * cu_rate

# calcular EC OK
def calculate_EC(db: Session, client_id: int, year: int, month: int) -> Tuple[float, float, float]:
    
    # Se obtiene servicio relacionado al cliente
    service = db.query(Service).filter(Service.id_service == client_id).first()
    if not service:
        raise ValueError(f"Client with ID {client_id} not found")

    # Consumo en un rango de mes por usuario
    total_injection = calculateSumInjection(db,client_id,year,month)

    tariff = db.query(Tariff).filter(
        Tariff.id_market == service.id_market,
        Tariff.voltage_level == service.voltage_level
    )

    # filtramos por cdi solo si voltage_level no es 2 o 3
    if service.voltage_level not in [2, 3]:
        tariff = tariff.filter(Tariff.cdi == service.cdi)

    tariff = tariff.first()

    if not tariff:
        raise ValueError("Tariff not found for the given service parameters")
    cu_rate = tariff.Cu
    return total_injection, cu_rate, total_injection * cu_rate

# calcular EE1 OK
def calculate_EE1(db: Session, client_id: int, year: int, month: int) -> Tuple[float, float, float]:
    
    # Se obtiene servicio relacionado al cliente
    service = db.query(Service).filter(Service.id_service == client_id).first()
    if not service:
        raise ValueError(f"Client with ID {client_id} not found")

    total_consumption = calculateSumConsumption(db,client_id,year,month)
    total_injection = calculateSumInjection(db,client_id,year,month)

    ee1_quantity = min(total_injection, total_consumption)

    tariff = db.query(Tariff).filter(
        Tariff.id_market == service.id_market,
        Tariff.voltage_level == service.voltage_level
    )

    if service.voltage_level not in [2, 3]:
        tariff = tariff.filter(Tariff.cdi == service.cdi)

    tariff = tariff.first()

    if not tariff:
        raise ValueError("Tariff not found for the given service parameters")
    cu_rate = tariff.Cu
    return ee1_quantity, -cu_rate, ee1_quantity*-cu_rate

# calcular EE2 OK
def calculate_EE2(db: Session, client_id: int, year: int, month: int) -> Tuple[float, float, float]:
    first_day, last_day = get_month_date_range(year, month)

    service = db.query(Service).filter(Service.id_service == client_id).first()
    if not service:
        raise ValueError(f"Client with ID {client_id} not found")

    query = db.query(
        Record.id_record,
        Record.id_service,
        Record.record_timestamp,
        Injection.value.label('injectionvalue'),
        Consumption.value.label('consumptionvalue'),
        XmDataHourlyPerAgent.value.label('agentvalue'),
        func.sum(Consumption.value).label('sum_comcumption'),
        func.sum(Injection.value).label('sum_injection')
    ).join(
        Injection, Record.id_record == Injection.id_record, isouter=True
    ).join(
        Consumption, Record.id_record == Consumption.id_record, isouter=True
    ).join(
        XmDataHourlyPerAgent, Record.record_timestamp == XmDataHourlyPerAgent.record_timestamp, isouter=True
    ).filter(
        Record.id_service == client_id,
        Record.record_timestamp >= first_day,
        Record.record_timestamp <= last_day
    ).order_by(
        Record.record_timestamp
    )
    
    results = query.all()

    combined_list = [{
        'id_record': record.id_record,
        'id_service': record.id_service,
        'record_timestamp': record.record_timestamp,
        'injection_value': record.injectionvalue,
        'consumption_value': record.consumptionvalue,
        'agent_value': record.agentvalue
    } for record in results]
    
    total_injection = sum(record["injection_value"] for record in combined_list if record['injection_value'] is not None)

    total_consumption = sum(record["consumption_value"] for record in combined_list if record['consumption_value'] is not None)

    EEv = min(total_injection, total_consumption)
    
    quantity = 0
    total = 0
    registers = []

    if total_injection > total_consumption:
    
        #accumulate_consumption = 0
        accumulate_injection = 0
    
        for record in combined_list:
            #accumulate_consumption += record['consumption_value'] if record['consumption_value'] is not None else 0
            accumulate_injection += record['injection_value'] if record['injection_value'] is not None else 0

            if accumulate_injection > EEv:
                datetime = record['record_timestamp']
                tariff = record['agent_value']
                if not registers:
                    ee2 = accumulate_injection - EEv
                else:
                    ee2 = record['injection_value'] if record['injection_value'] is not None else 0

                registers.append({
                    'datetime': datetime,
                    'ee2': ee2,
                    'tariff': tariff
                })

                quantity += ee2
                total += ee2 * tariff

    return quantity,registers,total

# calcular Invoice OK
def calculate_all_concepts(db: Session, client_id: int, year: int, month: int) -> Dict:
    ea_quantity, ea_rate, ea_total = calculate_EA(db, client_id, year, month)
    ec_quantity, ec_rate, ec_total = calculate_EC(db, client_id, year, month)
    ee1_quantity, ee1_rate, ee1_total = calculate_EE1(db, client_id, year, month)
    ee2_quantity, ee2_rate, ee2_total = calculate_EE2(db, client_id, year, month)
    print(ee2_quantity, ee2_rate, ee2_total)
    total_invoice = ea_total + ec_total + ee1_total + ee2_total
    
    return {
        "client_id": client_id,
        "month": month,
        "year": year,
        "EA": {
            "quantity": ea_quantity,
            "tariff": ea_rate,
            "total": ea_total
        },
        "EC": {
            "quantity": ec_quantity,
            "tariff": ec_rate,
            "total": ec_total
        },
        "EE1": {
            "quantity": ee1_quantity,
            "tariff": ee1_rate,
            "total": ee1_total
        },
        "EE2": {
            "quantity": ee2_quantity,
            "registers": ee2_rate,
            "total": ee2_total
        },
        "total": total_invoice
    }

# calcular estadisticas OK 
def get_client_statistics(db: Session, client_id: int) -> Dict:
    #obtenemos un reporte detallado por cient_id respecto de los consumos agrupados por año y mes
    #se obtiene de todos los registros disponibles
    record = db.query(
        func.extract('year', Record.record_timestamp).label('year'),
        func.extract('month', Record.record_timestamp).label('month'),
        func.sum(Consumption.value).label('consumption'),
        func.sum(Injection.value).label('injection')
    ).outerjoin(
        Consumption, Record.id_record == Consumption.id_record
    ).outerjoin(
        Injection, Record.id_record == Injection.id_record
    ).filter(
        Record.id_service == client_id
    ).group_by(
        func.extract('year', Record.record_timestamp),
        func.extract('month', Record.record_timestamp)
    ).all()

    monthly_stats = []
    total_consumption = 0
    total_injection = 0
    months_count = 0

    for year, month, consumption, injection in record:
        _consumption = consumption or 0
        _injection = injection or 0
        net = consumption - injection

        monthly_stats.append({
            "month": int(month),
            "year": int(year),
            "consumption": _consumption,
            "injection": _injection,
            "net": net
        })

        total_consumption += _consumption
        total_injection += _injection
        months_count += 1

    
    avg_consumption = total_consumption / months_count if months_count > 0 else 0
    avg_injection = total_injection / months_count if months_count > 0 else 0
    avg_net = (total_consumption - total_injection) / months_count if months_count > 0 else 0

    return {
        "client_id": client_id,
        "monthly_statistics": monthly_stats,
        "average_consumption": avg_consumption,
        "average_injection": avg_injection,
        "average_net": avg_net
    }

# calcular carga de sistema a partir de hora
def get_system_load(db: Session, date: datetime) -> Dict:

    start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
    end_date = datetime(date.year, date.month, date.day, 23, 59, 59)

    hourly_loads = db.query(
        func.extract('hour', Record.record_timestamp).label('hour'),
        func.sum(Consumption.value).label('load')
    ).join(
        Consumption
    ).filter(
        Record.record_timestamp >= start_date,
        Record.record_timestamp <= end_date
    ).group_by(
        func.extract('hour', Record.record_timestamp)
    ).all()

    return {
        "date": date,
        "hourly_loads": [
            {"hour": int(hour), "load": load} for hour, load in hourly_loads
        ]
    }