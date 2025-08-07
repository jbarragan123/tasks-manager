from fastapi import APIRouter, HTTPException
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskInDB, TaskDelete, TaskStatus
from app.services.task_service import TaskService
from app.workers.celery_worker import notify_task_due, generate_task_report
from datetime import datetime, timedelta

# Convención ruta , costumbre
router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskInDB, status_code=201)
async def create_task(task: TaskCreate):
    """
    Crea una nueva tarea en la base de datos.
    """
    task_dict = task.dict()
    result = await TaskService.create_task(task_dict)
    return result

@router.get("/", response_model=list[TaskInDB])
async def get_all_tasks():
    """
    Obtiene todas las tareas existentes en la base de datos.
    """
    return await TaskService.get_all_tasks()

@router.get("/{task_id}", response_model=TaskInDB)
async def get_task_by_id(task_id: str):
    """
    Obtiene una tarea específica por su ID.
    Retorna 404 si no se encuentra.
    """
    task = await TaskService.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskInDB)
async def update_task(task_id: str, task_data: TaskCreate):
    """
    Reemplaza completamente una tarea por su ID.
    Todos los campos deben ser proporcionados.
    """
    result = await TaskService.replace_task(task_id, task_data.dict())
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@router.patch("/{task_id}", response_model=TaskInDB)
async def patch_task(task_id: str, task_update: TaskUpdate):
    """
    Actualiza parcialmente una tarea por su ID.
    Solo los campos enviados en el cuerpo serán modificados.
    """
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    result = await TaskService.update_task(task_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@router.delete("/{task_id}", response_model=TaskDelete, status_code=200)
async def delete_task(task_id: str):
    """
    Elimina una tarea específica por su ID.
    Retorna 404 si la tarea no existe.
    """
    deleted_count, deleted_id = await TaskService.delete_task(task_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted_id": deleted_id}

@router.get("/status/{status}", response_model=list[TaskInDB])
async def get_tasks_by_status(status: TaskStatus):
    """
    Obtiene todas las tareas con un estado específico.
    Retorna 404 si no hay tareas con ese estado.
    """
    tasks = await TaskService.get_tasks_by_status(status.value)
    if not tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found with status '{status}'")
    return tasks

@router.post("/{task_id}/schedule")
async def schedule_notification(task_id: str):
    """
    Programa una notificación para una tarea específica antes de su fecha de vencimiento (due_date).
    Utiliza Celery para ejecutar la tarea de forma asíncrona.
    """
    delay = await TaskService.schedule_task_notification(task_id)
    if delay is None:
        raise HTTPException(status_code=404, detail="Task or due date not found")
    return {"message": f"Notification scheduled {delay} seconds before due date"}

@router.post("/generate-report")
async def generate_report():
    """
    Programa la generación de un reporte de tareas completadas.
    La tarea se ejecuta en segundo plano con Celery.
    """
    TaskService.run_report_generation()
    return {"message": "Task report is being generated in background"}
