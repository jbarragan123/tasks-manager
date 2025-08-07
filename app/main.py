from fastapi import FastAPI
from app.routes import task_routes

app = FastAPI()

# Routes
app.include_router(task_routes.router)

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}
