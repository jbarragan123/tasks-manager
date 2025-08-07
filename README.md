# 📝 Tasks Manager

Microservicio para gestión de tareas con FastAPI, MongoDB, Celery y Redis. Permite crear tareas, actualizarlas y programar notificaciones automáticas antes del vencimiento.

---

## 🚀 Tecnologías

- 🐍 Python 3.11
- ⚡ FastAPI
- 🍃 MongoDB
- 🧵 Celery + Redis (para tareas asíncronas)
- 🐳 Docker + Docker Compose

---

## 📦 Clonar y correr el proyecto

```bash
git clone https://github.com/jbarragan123/tasks-manager.git
cd tasks-manager
```

---

## ⚙️ Requisitos

- Tener instalados:
  - Docker
  - Docker Compose

---

## 📁 Estructura del proyecto

```
app/
├── db/                  # Conexión a MongoDB
├── routes/              # Rutas de la API
├── schemas/             # Esquemas Pydantic
├── services/            # Lógica de negocio
├── workers/             # Tareas Celery
main.py                  # Punto de entrada FastAPI
celery_worker.py         # Worker para Celery
```

---

## 🛠️ Levantar el entorno

```bash
docker-compose up --build
```

Esto inicia:

- API FastAPI (http://localhost:8000)
- MongoDB (puerto 27017)
- Redis (puerto 6379)
- Celery Worker

---

## 🧪 Probar la API

Visita Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔁 Flujo de notificaciones

- Crea o actualiza una tarea con `due_date`, después puedes programar una notificación llamando al endpoint:
  
  ```http
  POST /tasks/{task_id}/schedule_notification
  ```

- El sistema agenda una notificación usando Celery para que se dispare 1 minuto antes del `due_date`.

NOTA1: Si se crea o actualiza la tarea pero no se consume el endpoint /tasks/{task_id}/schedule_notification no generará nada

NOTA2: Recomiendo abrir la consola, entrar al proyecto y abrir los logs de docker con ```bash docker logs -f celery_worker``` para validar la tarea pesada cuando se consuma y ver el aviso de la notificación 1 min antes del due_date

NOTA3: Recomiendo validar la hora de la consola de logs (```bash docker logs -f celery_worker```), porque si programas una tarea por EJ: "2025-08-07 13:55" pero en la consola está adelantad0 6 horas EJ: "2025-08-07 19:55"  no se mostrará nada

---

## 🧪 Variables de entorno (.env)

Ya está configurado en `docker-compose.yml`, pero si deseas correr sin Docker:

```env
MONGO_URL=mongodb://localhost:27017
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## ✅ Verificación de contenedores

Puedes verificar los contenedores corriendo:

```bash
docker ps
```

Deberías ver algo como:

- fastapi_app
- mongodb
- redis
- celery_worker

---

## 📬 Comentarios

Si tienes alguna duda o error al momento de correr el proyecto no dudes en notificarme, mi correo es orionmaster8@gmail.com, respondo instantaneamente o a mi whatsapp 3125291007

## 🧑‍💻 Author

**Juan Barragán**  
[GitHub Profile](https://github.com/jbarragan123)
