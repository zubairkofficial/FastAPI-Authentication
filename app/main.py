from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import engine, Base, init_db
from app.models.User import User
from app.models.Token import  Token
from app.models.PasswordReset import PasswordReset
from app.models.Item import Item
from app.routes.user_route import router as user_router
from app.routes.api_routes import router as api_router
import logging
from fastapi.middleware.cors import CORSMiddleware


def create_table():
    Base.metadata.create_all(engine)
    print("Database Table Created Successfully...")


@asynccontextmanager
async def lifespan(app=FastAPI):
    try:
        create_table()
    except Exception as e:
        logging.error(f"Database not created due to {e}")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router, prefix='/api/auth', tags=['User'])
app.include_router(api_router, prefix='/api/user', tags=['User'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def index():
    return {"message": "Hello, World!"}
