# Smart ERP — Django Backend

Village Production System backend built with Django (no DRF).

## Setup

```bash
cd backend

# Install dependencies
pip3 install -r requirements.txt

# Run migrations
python3 manage.py migrate

# Create demo users + seed sample data
python3 manage.py seed

# Start server
python3 manage.py runserver 8000
```

## Demo Users

| Email            | Password       | Role    |
|------------------|----------------|---------|
| admin@erp.in     | SmartErp@2026! | Admin   |
| manager@erp.in   | SmartErp@2026! | Manager |
| staff@erp.in     | SmartErp@2026! | Staff   |

## Project Structure

```
backend/
├── manage.py
├── db.sqlite3
├── backend/          # Project config + URL routing
│   ├── settings.py
│   ├── urls.py
│   └── api_urls.py   # All API endpoints
├── accounts/         # Auth app (login, logout, token)
├── operations/       # Villages + Units
└── main/             # Production, Inventory, Training, Dashboard
```

## API Endpoints

All endpoints are under `/api/`. Token-based auth via `Authorization: Bearer <token>`.

### Auth
| Method | Endpoint         | Body                      |
|--------|------------------|---------------------------|
| POST   | /auth/login      | `{ email, password }`     |
| POST   | /auth/logout     | (token in header)         |
| GET    | /auth/me         | (token in header)         |

### Villages
| Method | Endpoint             |
|--------|----------------------|
| GET    | /villages            |
| POST   | /villages            |
| GET    | /villages/<id>       |
| PUT    | /villages/<id>       |
| DELETE | /villages/<id>       |
| GET    | /villages/<id>/units |

### Units
| Method | Endpoint       |
|--------|----------------|
| GET    | /units         |
| POST   | /units         |
| PUT    | /units/<id>    |
| DELETE | /units/<id>    |

### Production
| Method | Endpoint          |
|--------|-------------------|
| GET    | /production       |
| POST   | /production       |
| PUT    | /production/<id>  |
| DELETE | /production/<id>  |

### Inventory
| Method | Endpoint               | Body                              |
|--------|------------------------|-----------------------------------|
| GET    | /inventory             |                                   |
| POST   | /inventory             | `{ product, category, min_stock, unit }` |
| PUT    | /inventory/<id>        |                                   |
| DELETE | /inventory/<id>        |                                   |
| POST   | /inventory/stock-in    | `{ inventory_id, quantity, note }` |
| POST   | /inventory/stock-out   | `{ inventory_id, quantity, note }` |
| GET    | /inventory/<id>/history|                                   |

### Training
| Method | Endpoint            | Body                                     |
|--------|---------------------|------------------------------------------|
| GET    | /trainings          |                                          |
| POST   | /trainings          | `{ title, trainer, startDate, endDate, seats, status, location }` |
| PUT    | /trainings/<id>     |                                          |
| DELETE | /trainings/<id>     |                                          |
| POST   | /trainings/enroll   | `{ training_id, name, village, note }`   |

### Trainees
| Method | Endpoint         |
|--------|------------------|
| GET    | /trainees        |
| POST   | /trainees        |
| PUT    | /trainees/<id>   |
| DELETE | /trainees/<id>   |

### Dashboard
| Method | Endpoint            |
|--------|---------------------|
| GET    | /dashboard/summary  |
| GET    | /dashboard/charts   |

## Tech Stack

- Django 4.2
- SQLite
- django-cors-headers
- Function-based views (no DRF)
- Token-based authentication

## Django Admin

Visit `http://localhost:8000/admin/` with your superuser credentials to manage all models.
