from app.db.mongo import db
from bson import ObjectId
from bson.errors import InvalidId
from app.workers.celery_worker import notify_task_due, generate_task_report
from datetime import datetime

class TaskService:
    @staticmethod
    async def create_task(task_dict):
        """
        Crea una nueva tarea en la base de datos.
        """
        result = await db.tasks.insert_one(task_dict)
        task_dict["_id"] = str(result.inserted_id)
        return task_dict

    @staticmethod
    async def get_all_tasks():
        """
        Obtiene todas las tareas almacenadas en la base de datos.
        """
        cursor = db.tasks.find()
        tasks = []
        async for task in cursor:
            task["_id"] = str(task["_id"])
            tasks.append(task)
        return tasks

    @staticmethod
    async def get_task_by_id(task_id):
        """
        Busca una tarea por su ID. Retorna None si el ID es inválido o no se encuentra.
        """
        try:
            task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        except InvalidId:
            return None
        if task:
            task["_id"] = str(task["_id"])
        return task

    @staticmethod
    async def replace_task(task_id, new_data):
        """
        Reemplaza completamente los datos de una tarea con el ID proporcionado.
        """
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            return None
        result = await db.tasks.replace_one({"_id": obj_id}, new_data)
        if result.modified_count:
            new_data["_id"] = str(obj_id)
            return new_data
        return None

    @staticmethod
    async def update_task(task_id, update_data):
        """
        Actualiza parcialmente los datos de una tarea.
        Solo modifica los campos proporcionados.
        """
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            return None
        result = await db.tasks.find_one_and_update(
            {"_id": obj_id},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    @staticmethod
    async def delete_task(task_id):
        """
        Elimina una tarea por su ID.
        Retorna una tupla con la cantidad eliminada (0 o 1) y el ID.
        """
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            return 0, None
        result = await db.tasks.delete_one({"_id": obj_id})
        return result.deleted_count, str(obj_id)

    @staticmethod
    async def get_tasks_by_status(status):
        """
        Filtra y retorna todas las tareas que tengan un estado específico.
        """
        cursor = db.tasks.find({"status": status})
        tasks = []
        async for task in cursor:
            task["_id"] = str(task["_id"])
            tasks.append(task)
        return tasks

    @staticmethod
    async def schedule_task_notification(task_id: str):
        """
        Programa una notificación para una tarea próxima a vencer (1 minuto antes del due_date).
        Usa Celery para ejecutar la tarea asíncronamente.
        """
        task = await TaskService.get_task_by_id(task_id)
        if not task or not task.get("due_date"):
            return None

        due_date_raw = task["due_date"]
        if isinstance(due_date_raw, str):
            due_date = datetime.fromisoformat(due_date_raw)
        else:
            due_date = due_date_raw 

        delay = (due_date - datetime.utcnow()).total_seconds() - 60
        delay = max(0, delay)

        notify_task_due.apply_async(
            args=[str(task["_id"]), task["title"], due_date.isoformat()],
            countdown=delay
        )

        return round(delay)

    @staticmethod
    def run_report_generation():
        """
        Lanza la generación de un reporte en segundo plano con Celery.
        """
        generate_task_report.delay()
