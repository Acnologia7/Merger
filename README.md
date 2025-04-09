# 🍽️ Merger

**Merger** is an asynchronous FastAPI application that periodically fetches and merges data using a background scheduler, then exposes the results via RESTful endpoints.

Built with:

- FastAPI ⚡️
- APScheduler for background tasks ⏰
- SQLAlchemy + SQLite for persistence 🗂️
- Uvicorn for ASGI serving 🚀

---

## 📦 Features

- ✅ REST API built on FastAPI
- 🔁 Background merging via APScheduler
- 🗃️ SQLite for lightweight DB storage
- 🐳 Dockerized for easy deployment
- 🛡️ Custom exception handling and logging

---

## 🏗️ Project Structure

```
app/
├── core/
│   ├── config.py                   # App settings via pydantic
│   ├── db.py                       # DB engine + session logic
│   ├── logging_config.py           # Logging setup
│   ├── scheduler.py                # APScheduler job setup
│   └── exception_handlers.py       # Custom exception handlers
├── docs/
│   └──openapidocs.py               # Basic openapi docs for enpoints
├── models/
│   ├──models.py                    # SQLAlchemy models
│   └──schemas.py                   # Pydantic validation models
├── routers/
│   └── routes.py                   # API routes
├── services/
│   └── data.py                     # Data fetching/merging logic
└── server.py                       # FastAPI app instance
tests/
├── integration/
│   └── test_routes.py              # Integration tests for routes
└── unit/
    ├── test_data_service.py        # Unit tests for Data service
    ├── test_exception_handlers.py  # Unit tests for exception handlers
    └── test_scheduler.py           # Unit tests for apscheduler
main.py                             # AppManager with scheduler + app boot
```

---

## ⚙️ Installation (local)

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/Merger.git
cd Merger
```

### 2. Create `.env` File

```env
# .env
DATABASE_URL="sqlite+aiosqlite:///./data.db"

WORKERS_COUNT=1
APP_HOST="0.0.0.0"
APP_PORT=8000

DATA_B_URL="url/where/data_b/are/located"
FETCH_INTERVAL_SECONDS=90
MAX_RETRIES=3
RETRY_DELAY=2
```

> ✅ SQLite is used for development. For production, switch to Postgres or another RDBMS.

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App Locally

```bash
python main.py
```

The API will be live at:  
http://localhost:8000

Swagger UI is available at:  
http://localhost:8000/docs

---

## 🐳 Running with Docker

### 1. Build and run via docker-compose

```bash
docker-compose up
```

### 2. (optionaly) build and run only tests

```bash
docker-compose up test --abort-on-container-exit
```

> 🔐 Ensure `.env` file is in the root and includes `WORKERS_COUNT=1` for SQLite compatibility.

---

## 🛠️ API Endpoints

Auto-generated OpenAPI docs available at `/docs` for more details.

Examples:

```
POST /data-a
```

```
{
  "menus": [
    {
      "id": 1,
      "sysName": "string",
      "name": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
      },
      "price": 1,
      "vatRate": "normal"
    }
  ],
  "vatRates": {
    "additionalProp1": {
      "ratePct": 1,
      "isDefault": false
    },
    "additionalProp2": {
      "ratePct": 1,
      "isDefault": false
    },
    "additionalProp3": {
      "ratePct": 1,
      "isDefault": false
    }
  }
}
```

```
GET /data-c
```

```
{
  "data": {
    "additionalProp1": [
      {
        "id": 1,
        "sysName": "string",
        "name": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "price": 1,
        "vatRate": "normal"
      }
    ],
    "additionalProp2": [
      {
        "id": 1,
        "sysName": "string",
        "name": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "price": 1,
        "vatRate": "normal"
      }
    ],
    "additionalProp3": [
      {
        "id": 1,
        "sysName": "string",
        "name": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "price": 1,
        "vatRate": "normal"
      }
    ]
  },
  "vatRates": {
    "additionalProp1": {
      "ratePct": 1,
      "isDefault": false
    },
    "additionalProp2": {
      "ratePct": 1,
      "isDefault": false
    },
    "additionalProp3": {
      "ratePct": 1,
      "isDefault": false
    }
  },
  "lastUpdate": "2025-04-09T08:03:14.689Z",
  "products": [
    {
      "additionalProp1": "string",
      "additionalProp2": "string",
      "additionalProp3": "string"
    }
  ]
}
```

---

## 🔄 Background Job

The scheduler runs `DataService.fetch_and_merge()` every `FETCH_INTERVAL_SECONDS`, which:

- Fetches data from external/internal sources
- Merges or transforms the data
- Saves the result to the database

---

## 📝 Logging

Logs are written to console. Log level can be adjusted via `logging_config.py`.

---

## ❗ Exception Handling

Handled globally:

- Generic exceptions
- SQLAlchemy database errors
