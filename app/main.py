import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.db import Base, engine
from app.routers import associates, auth, invoices, items, remissions, users

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cobrizi API", version="0.1.0")

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(associates.router)
app.include_router(items.router)
app.include_router(invoices.router)
app.include_router(remissions.router)


@app.get("/")
def root():
    return {"message": "Cobrizi API running ✅"}
