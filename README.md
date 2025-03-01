# Sistema de Facturación de Energía

Un sistema para calcular y analizar la facturación de energía utilizando Python y PostgreSQL.

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/rockhount793/energy.git
   cd energy
   ```
2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Crear una base de datos PostgreSQL con nombre energy

4. Actualizar el archivo `.env` con la URL de conexión a la base de datos:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@localhost/energy
   ```
   
5. Cargar la data inicial desde los CSV:
   ```
   python load_initial_data.py
   ```

## Ejecutar la Aplicación

Iniciar el servidor FastAPI:
```
uvicorn app.main:app --reload
```

La API estará disponible en http://localhost:8000.

La documentación de la API estará disponible en http://localhost:8000/docs.

### Pruebas con comandos CURL

```sh
# 1. Probar la página de inicio
curl -X GET "http://localhost:8000/"

# 2. Calcular una factura completa para un cliente (Febrero 2023)
curl -X POST "http://localhost:8000/api/calculate-invoice" \
  -H "Content-Type: application/json" \
  -d '{"client_id": 3222, "month": 9, "year": 2023}'

# 3. Obtener estadísticas de un cliente
curl -X GET "http://localhost:8000/api/client-statistics/3222"

# 4. Obtener la carga del sistema 
curl -X GET "http://localhost:8000/api/system-load?date_str=2023-09-02"

# 5. Calcular EA (Energía Activa)
curl -X GET "http://localhost:8000/api/calculate-ea/3222?year=2023&month=9"

# 6. Calcular EC (Excedente de Comercialización de Energía)
curl -X GET "http://localhost:8000/api/calculate-ec/3222?year=2023&month=9"

# 7. Calcular EE1 (Excedente de Energía tipo 1)
curl -X GET "http://localhost:8000/api/calculate-ee1/3222?year=2023&month=9"

# 8. Calcular EE2 (Excedente de Energía tipo 2)
curl -X GET "http://localhost:8000/api/calculate-ee2/3222?year=2023&month=9"

## Endpoints de la API

- `POST /api/calculate-invoice`: Calcula la factura de un cliente para un mes específico.
- `GET /api/client-statistics/{client_id}`: Obtiene estadísticas de consumo e inyección de un cliente.
- `GET /api/system-load`: Obtiene la carga del sistema por hora según los datos de consumo.
- `GET /api/calculate-ea/{client_id}`: Calcula EA (Energía Activa) para un cliente y mes.
- `GET /api/calculate-ec/{client_id}`: Calcula EC (Excedente de Comercialización de Energía) para un cliente y mes.
- `GET /api/calculate-ee1/{client_id}`: Calcula EE1 (Excedente de Energía tipo 1) para un cliente y mes.
- `GET /api/calculate-ee2/{client_id}`: Calcula EE2 (Excedente de Energía tipo 2) para un cliente y mes.

## Esquema de Base de Datos

El esquema de la base de datos incluye las siguientes tablas:
- `services`: Información sobre los servicios de los clientes.
- `records`: Registros de consumo e inyección de energía.
- `consumption`: Datos de consumo de energía.
- `injection`: Datos de inyección de energía.
- `tariffs`: Tarifas de energía.
- `xm_data_hourly_per_agent`: Precios de la energía por hora.
