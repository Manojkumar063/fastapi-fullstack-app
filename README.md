# fastapi-fullstack-app

Full-stack application with FastAPI backend, React frontend, Docker, Kubernetes, and CI/CD pipeline.

## Tech Stack

- **Backend** — FastAPI, SQLAlchemy, SQLite, Redis
- **Frontend** — React, Vite, Nginx
- **Auth** — JWT-based authentication
- **AI/Chat** — RAG-based document Q&A (Gemini API)
- **Infrastructure** — Docker Compose, Kubernetes, Terraform
- **Monitoring** — Prometheus, Grafana
- **CI/CD** — GitHub Actions → Docker Hub → EC2

## Project Structure

```
├── backend/        # FastAPI app (auth, items, chat/RAG)
├── frontend/       # React app
├── gateway/        # Nginx reverse proxy
├── k8s/            # Kubernetes manifests
├── infrastructure/ # Terraform (AWS)
├── monitoring/     # Prometheus config
└── .github/        # CI/CD workflows
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### Run with Docker Compose

```bash
cp backend/.env.example backend/.env  # fill in your values
docker-compose up --build
```

| Service    | URL                    |
|------------|------------------------|
| Frontend   | http://localhost:80    |
| API        | http://localhost:8080  |
| Prometheus | http://localhost:9090  |
| Grafana    | http://localhost:3000  |

### Run Locally (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint         | Description         | Auth |
|--------|-----------------|---------------------|------|
| POST   | /auth/signup    | Register user       | No   |
| POST   | /auth/login     | Login & get token   | No   |
| GET    | /auth/me        | Current user info   | Yes  |
| GET    | /items          | List all items      | Yes  |
| POST   | /items          | Create item         | Yes  |
| PUT    | /items/{id}     | Update item         | Yes  |
| DELETE | /items/{id}     | Delete item         | Yes  |
| POST   | /chat/upload    | Upload document     | Yes  |
| POST   | /chat/message   | Ask a question      | Yes  |
| DELETE | /chat/reset     | Reset chat history  | Yes  |

## Environment Variables

Create `backend/.env`:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./items.db
GEMINI_API_KEY=your_gemini_api_key
```

## CI/CD

On every push to `main`:
1. Runs backend tests (pytest)
2. Builds frontend (npm)
3. Builds & pushes Docker images to Docker Hub
4. Deploys to EC2 via SSH

### Required GitHub Secrets

| Secret           | Description              |
|-----------------|--------------------------|
| DOCKER_USERNAME  | Docker Hub username      |
| DOCKER_PASSWORD  | Docker Hub password      |
| SECRET_KEY       | JWT secret key           |
| GEMINI_API_KEY   | Google Gemini API key    |
| EC2_HOST         | EC2 public IP            |
| EC2_USER         | EC2 SSH username         |
| EC2_SSH_KEY      | EC2 private SSH key      |

## License

MIT
