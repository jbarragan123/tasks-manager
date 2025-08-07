from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

celery = Celery("tasks", broker=CELERY_BROKER_URL)

@celery.task
def notify_task_due(task_id: str, title: str, due_date: str):
    """
    Tarea asíncrona que simula una notificación cuando una tarea está próxima a vencer.
    """
    print(f"🔔 [NOTIFY] La tarea '{title}' (ID: {task_id}) vence el {due_date}.")
    return f"Notificación enviada para la tarea {task_id}"

@celery.task
def generate_task_report():
    """
    Tarea asíncrona simulada para generar un reporte de tareas.
    (Por ahora solo espera 10 segundos y muestra un mensaje).
    """
    import time
    time.sleep(10)
    print("📄 Reporte generado.")
    return "Reporte de tareas generado"
