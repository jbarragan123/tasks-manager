from app.db.mongo import db
from bson import ObjectId
from bson.errors import InvalidId

class TaskService:
    @staticmethod
    async def create_task(task_dict):
        result = await db.tasks.insert_one(task_dict)
        task_dict["_id"] = str(result.inserted_id)
        return task_dict

    @staticmethod
    async def get_all_tasks():
        cursor = db.tasks.find()
        tasks = []
        async for task in cursor:
            task["_id"] = str(task["_id"])
            tasks.append(task)
        return tasks

    @staticmethod
    async def get_task_by_id(task_id):
        try:
            task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        except InvalidId:
            return None
        if task:
            task["_id"] = str(task["_id"])
        return task

    @staticmethod
    async def replace_task(task_id, new_data):
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
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            return 0, None
        result = await db.tasks.delete_one({"_id": obj_id})
        return result.deleted_count, str(obj_id)

    @staticmethod
    async def get_tasks_by_status(status):
        cursor = db.tasks.find({"status": status})
        tasks = []
        async for task in cursor:
            task["_id"] = str(task["_id"])
            tasks.append(task)
        return tasks