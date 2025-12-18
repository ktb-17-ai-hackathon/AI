from fastapi import FastAPI
from app.routes.life_cycle import router as life_cycle_router

app = FastAPI(title="Life Cycle API")

app.include_router(life_cycle_router)