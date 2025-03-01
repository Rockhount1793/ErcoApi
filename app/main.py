from fastapi import FastAPI

from app.routes.items import router as items_router
from app.models.models import Base
# Fix the import to use the app.database module
from app.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(items_router, prefix="/api", tags=["Energy Billing"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastApi"}