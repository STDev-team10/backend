from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import ask, compounds, hall_of_fame
from app.services.compound_seed_service import seed_compounds_if_needed

app = FastAPI(
    title="compounds-service",
    docs_url="/api/compounds/docs",
    redoc_url="/api/compounds/redoc",
    openapi_url="/api/compounds/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
seed_compounds_if_needed()

app.include_router(compounds.router)
app.include_router(hall_of_fame.router)
app.include_router(ask.router)
