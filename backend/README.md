# FastAPI Sample Project

A minimal CRUD API using FastAPI + SQLAlchemy + SQLite.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

## API Docs

Open http://127.0.0.1:8000/docs in your browser.

## Endpoints


| Method | Endpoint         | Description       |
|--------|------------------|-------------------|
| POST   | /items           | Create an item    |
| GET    | /items           | List all items    |
| GET    | /items/{id}      | Get item by ID    |
| PUT    | /items/{id}      | Update item by ID |
| DELETE | /items/{id}      | Delete item by ID |