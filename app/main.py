from fastapi import FastAPI 
from contextlib import asynccontextmanager
from app.db.database import engine, Base, init_db
from app.models.User import User
from app.models.PasswordReset import PasswordReset
from app.routes.user_route import router as user_router
import logging



def create_table():
    Base.metadata.create_all(engine)
    print("Database Table Created Successfully...")


@asynccontextmanager
async def lifespan(app= FastAPI):
    try:
        create_table()
    except Exception as e:
        logging.error(f"Database not created due to {e}")
    yield
        
app = FastAPI(lifespan=lifespan)
app.include_router(user_router, prefix='/auth', tags=['User'])

@app.get('/')
def index():
    return {"message": "Hello, World!"}

