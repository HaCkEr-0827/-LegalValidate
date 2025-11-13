# ⚖️ LegalValidate API — Django REST Framework + Celery + Redis + PostgreSQL

A production-ready backend API for **Legal Document Analysis** built with  
**Django**, **Django REST Framework (DRF)**, **Celery**, **Redis**, and **PostgreSQL**.  
This API analyzes uploaded **contracts** or **documents**, runs asynchronous tasks with **Celery**,  
and provides secure authentication using **JWT** tokens.

---

## 🌟 Key Features

### 🔐 Authentication
- Secure **JWT-based** login and registration  
- Custom **User model** with email as username  
- Token blacklist for logout  
- Role-based user system (Admin, Staff, User)

### 📄 Contract Analysis
- Upload `.pdf`, `.txt` or `.docx` contracts
- Automatically extract text and run AI-based analysis
- Store analyzed results in PostgreSQL
- Asynchronous task processing via **Celery + Redis**

### 🧾 Subscriptions
- Manage user subscription plans
- Track active or expired plans

### ⚙️ Background Tasks
- Long-running AI analyses handled via **Celery**
- Redis as Celery **broker**
- Django admin for monitoring

### 📊 API Documentation
- **Docs UI:** `/docs/`
- **ReDoc UI:** `/redoc/`

---

## 🧠 Technologies Used

| Component | Technology |
|------------|-------------|
| Framework | Django 5.x |
| API | Django REST Framework |
| Task Queue | Celery 5.5 |
| Broker | Redis 7 |
| Database | PostgreSQL 15 |
| Auth | SimpleJWT |
| Docs | drf-yasg |
| Server | Gunicorn |
| Deployment | Docker / Podman |
| Python | 3.11+ |

---

## 🚀 Run Project

### Using Docker / Podman
```
podman-compose up --build -d
podman network inspect legalvalidate_backend_default
podman-compose up -d web
podman-compose exec web python manage.py makemigrations
podman-compose exec web python manage.py migrate
```

Your app will be available at:  
👉 http://localhost:8001/

---

### 🧩 Without Docker (Local Setup)

```
pip install -r requirements.txt
python manage.py migrate
podman exec -it web_app bash
python manage.py createsuperuser
celery -A config worker -l info
```

---

## 📡 API Endpoints (Simplified)

### 🔐 Authentication
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /api/auth/signup/ | POST | Register new user |
| /api/auth/login/ | POST | Login user |
| /api/auth/refresh/ | POST | Refresh JWT |

### 📄 Contracts
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /api/contracts/ | GET/POST | Upload or list analyzed contracts |
| /api/contracts/<id>/ | GET | Retrieve contract analysis |

### 💳 Subscriptions
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /api/subscriptions/ | GET | List subscriptions |
| /api/subscriptions/<id>/ | PUT | Update subscription status |

### ⚙️ Admin Tools
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /admin/ | Web | Django Admin panel |
| /docs/ | Web | Swagger UI Docs |
| /redoc/ | Web | ReDoc Documentation |

---

## 🧠 Celery + Redis Connection Check

```
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)
redis://redis_db:6379/0
```

✅ If correct, you’ll see:  
`redis://redis_db:6379/0`


## 📊 Admin Access

**URL:** http://localhost:8001/admin/  
**Login:** Superuser created via `createsuperuser`

Manage **users**, **contracts**, and **subscriptions**

---

## 🧾 License

**MIT License**  
Use freely for personal and commercial projects.

---

## 👨‍💻 Author

**Samandar Shukriddinov**  
📧 Email: samandarparkent@gmail.com
🐙 GitHub: [github.com/HaCkEr-0827](https://github.com/HaCkEr-0827)

⭐ Star this repo if you find it helpful!