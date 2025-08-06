from fastapi import APIRouter, HTTPException
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse, TaskDelete, TaskStatus, TaskInDB
from app.db.mongo import db
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from bson.errors import InvalidId


router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/tasks", status_code=201)
async def create_task(task: TaskCreate):
    task_dict = task.dict()
    result = await db.tasks.insert_one(task_dict)
    task_dict["_id"] = str(result.inserted_id)
    return task_dict

@router.get("/tasks", response_model=list[TaskInDB])
async def get_all_tasks():
    tasks_cursor = db.tasks.find()
    tasks = []
    async for task in tasks_cursor:
        task["_id"] = str(task["_id"])
        tasks.append(task)
    return tasks

@router.get("/tasks/{task_id}")
async def get_task_by_id(task_id: str):
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task["id"] = str(task["_id"])
    del task["_id"]
    return task


@router.put("/tasks/{task_id}", response_model=TaskInDB)
async def update_task(task_id: str, task_update: TaskUpdate):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    update_data = {k: v for k, v in task_update.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = await db.tasks.find_one_and_update(
        {"_id": obj_id},
        {"$set": update_data},
        return_document=True 
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    result["_id"] = str(result["_id"])
    return result

@router.delete("/tasks/{task_id}", response_model=TaskDelete, status_code=200)
async def delete_task(task_id: str):
    try:
        obj_id = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task ID")

    result = await db.tasks.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"deleted_id": str(obj_id)}


@router.get("/status/{status}", response_model=list[TaskResponse])
async def get_tasks_by_status(status: TaskStatus):
    tasks_cursor = db.tasks.find({"status": status.value})
    tasks = []
    async for task in tasks_cursor:
        task["id"] = str(task["_id"])
        del task["_id"]
        tasks.append(task)

    if not tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found with status '{status}'")

    return tasks