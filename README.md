# AI Agent Builder

AI Agent Builder is a full-stack web application that allows users to create, manage, and interact with AI agents. The application provides a user-friendly interface for building custom AI agents with configurable roles, goals, and parameters, enabling seamless chat interactions with your AI agents.

## Features

- **User Authentication**: Secure user registration and login system with JWT tokens
- **Agent Management**: Create, list, and delete AI agents with customizable configurations
- **Agent Configuration**: Configure agents with:
  - Name and role
  - Goal/purpose
  - Model selection (e.g., GPT-4 Turbo)
  - Temperature settings
  - Maximum token limits
- **Chat Interface**: Interactive chat interface to communicate with your AI agents
- **Persistent Storage**: SQLite database for data persistence
- **Docker Support**: Containerized deployment with Docker Compose for easy setup

## Project Structure

The project is organized into two main components:

### Backend (`backend/`)
- **FastAPI** application providing RESTful API endpoints
- **SQLAlchemy** for database management
- **SQLite** database for data storage
- Authentication and authorization middleware
- Agent management and chat functionality
- API documentation available at `/docs` endpoint

### Frontend (`frontend/`)
- **React** application with modern UI
- **React Router** for navigation
- **Axios** for API communication
- Protected routes for authenticated users
- Responsive design with Nginx serving the production build

## Prerequisites

Before running this project, ensure you have the following installed on your system:

- **Docker** (version 20.10 or higher)
  - Docker Desktop for Windows or Mac
  - Docker Engine for Linux
- **Docker Compose** (version 2.0 or higher)
  - Usually included with Docker Desktop
  - For Linux, install separately if needed

## Getting Started

This guide will walk you through the complete setup process from cloning the repository to running the application. The application uses Docker Compose to manage all services, making setup straightforward.

### Quick Start

If you're familiar with Docker and just need the commands:

```bash
# Clone the repository
git clone <repository-url>
cd AI-Agent-Builder

# Pull latest changes (if repository already exists)
git pull origin developement

# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Detailed Steps:**
1. Install Git, Docker, and Docker Compose
2. Clone or pull the repository
3. Navigate to the project directory
4. Start Docker
5. Build and start the application with Docker Compose
6. Wait for services to initialize
7. Verify the installation
8. Access the application in your browser

### Step 1: Install Prerequisites

Before you begin, make sure you have the following installed:
- **Git** - For cloning the repository
- **Docker** - Version 20.10 or higher (Docker Desktop for Windows/Mac, or Docker Engine for Linux)
- **Docker Compose** - Version 2.0 or higher (usually included with Docker Desktop)

### Step 2: Clone or Pull the Repository

If you don't have the repository yet:
```bash
git clone <repository-url>
cd AI-Agent-Builder
```

Replace `<repository-url>` with the actual repository URL (e.g., `https://github.com/username/ai-agent-builder.git` or `git@github.com:username/ai-agent-builder.git`).

If you already have the repository:
```bash
cd AI-Agent-Builder
git pull origin developement
```

Note: Replace `developement` with your branch name (e.g., `main`, `master`, or your feature branch).

To check your current branch:
```bash
git branch
```

### Step 3: Navigate to Project Directory

After cloning or pulling the repository, navigate to the project root directory:
```bash
cd AI-Agent-Builder
```

Verify you're in the correct directory by checking for the presence of `docker-compose.yml`, `backend`, and `frontend` folders:
```bash
ls -la
```

On Windows PowerShell:
```powershell
dir
```

### Step 4: Ensure Docker is Running

Before starting the application, verify Docker is running:

```bash
docker --version
docker-compose --version
```

Start Docker Desktop if you're on Windows or Mac, then verify Docker is running:
```bash
docker ps
```

If Docker is running, this command should execute without errors. If you see an error, make sure Docker Desktop is started.

### Step 5: Build and Start the Application

From the project root directory, build and start all services:

```bash
docker-compose up -d --build
```

This command will:
- Build the backend Docker image and install all Python dependencies from `requirements.txt`
- Build the frontend Docker image, install Node.js dependencies, and create the production build
- Create a Docker network named `ai-agent-network` for service communication
- Create a persistent Docker volume named `app_data` for database storage
- Start the backend container on port 8000
- Start the frontend container on port 3000 (mapped to container port 80)

The `-d` flag runs containers in detached mode (in the background), and `--build` ensures images are rebuilt.

### Step 6: Wait for Services to Initialize

After starting the containers, monitor the startup process. The first build may take several minutes as Docker downloads base images and installs dependencies.

To view the logs in real-time:
```bash
docker-compose logs -f
```

To check the status of all containers:
```bash
docker-compose ps
```

You should see both `ai-agent-builder-backend` and `ai-agent-builder-frontend` containers with status "Up". Wait until both containers are in a running state before accessing the application.

### Step 7: Verify Installation

Once the containers are running, verify the installation:

Check container status:
```bash
docker-compose ps
```

View logs for a specific service:
```bash
docker-compose logs backend
docker-compose logs frontend
```

Test backend API:
```bash
curl http://localhost:8000/docs
```

Or open `http://localhost:8000/docs` in your browser to access the API documentation.

If any container fails to start, check the logs for error messages:
```bash
docker-compose logs [service-name]
```

### Accessing the Application

Once the services are running, you can access:

- **Frontend Application**: Open your web browser and navigate to `http://localhost:3000`
- **Backend API**: The API is available at `http://localhost:8000`
- **API Documentation**: Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`
- **Alternative API Docs**: ReDoc documentation is available at `http://localhost:8000/redoc`

### Step 8: Stopping the Application

To stop the running services (containers will be removed, but data volume preserved):
```bash
docker-compose down
```

To stop and remove all data including the database:
```bash
docker-compose down -v
```

This will completely reset the application state by removing volumes.

To restart the application after stopping:
```bash
docker-compose up -d
```

This will restart using existing images (faster than initial build). If you made code changes, rebuild:
```bash
docker-compose up -d --build
```

## Configuration

### Environment Variables

#### Backend
- **DATABASE_URL**: Database connection string (default: SQLite database at `./data/ai_agent_builder.db`)
- **PYTHONUNBUFFERED**: Set to 1 for immediate log output (helps with debugging)

#### Frontend
- **REACT_APP_API_BASE**: Backend API base URL (default: `http://localhost:8000`)

These environment variables are configured in the `docker-compose.yml` file and can be modified there if needed.

### Database

The application uses SQLite database stored in a Docker volume for persistence. The database is automatically initialized when the backend service starts. The database file is stored in the `app_data` volume and persists even after containers are stopped.

## Usage

### First Time Setup

1. **Access the application** at `http://localhost:3000`
2. **Create an account** by registering with a username, email, and password
3. **Log in** with your credentials
4. **Create your first agent** by providing:
   - Agent name
   - Role description
   - Goal or purpose
   - Model selection
   - Temperature and token settings (optional)
5. **Start chatting** with your agent by selecting it from your dashboard

### Managing Agents

- **Create Agents**: Add new AI agents with custom configurations
- **View Agents**: See all your agents listed on the dashboard
- **Delete Agents**: Remove agents you no longer need
- **Chat with Agents**: Click on an agent to open the chat interface

## Troubleshooting

### Port Conflicts

If ports 8000 or 3000 are already in use on your system:
- Modify the port mappings in the `docker-compose.yml` file
- Change the host port (left side of the mapping) to an available port
- Update the frontend API configuration if you change the backend port

### Service Not Starting

- Check Docker logs for error messages
- Verify Docker is running properly
- Ensure you have sufficient disk space for Docker images
- Check that no other containers are using the same ports

### Database Issues

The database is stored in a Docker volume. To reset the database:

```bash
docker-compose down -v
docker-compose up -d
```

This removes the volume and recreates it on startup. To view volume information:
```bash
docker volume ls
docker volume inspect ai-agent-builder-data
```

### Rebuilding After Changes

If you make changes to the code, rebuild the images:
```bash
docker-compose up -d --build
```

To force a complete rebuild without cache:
```bash
docker-compose build --no-cache
docker-compose up -d
```

To rebuild a specific service:
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Viewing Logs

View logs from all services:
```bash
docker-compose logs -f
```

View logs from a specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

View last 100 lines of logs:
```bash
docker-compose logs --tail=100
```

## Development

### Project Architecture

- **Backend**: FastAPI with SQLAlchemy ORM, JWT authentication
- **Frontend**: React with React Router, Context API for state management
- **Database**: SQLite with persistent Docker volumes
- **Deployment**: Docker containers with Nginx for frontend serving

### API Endpoints

The backend provides the following main endpoint groups:
- **Authentication** (`/auth`): User registration, login, token management
- **Agents** (`/agents`): Agent CRUD operations
- **Chat** (`/chat`): Chat message handling and agent interactions

Detailed API documentation is available at the `/docs` endpoint when the backend is running.

## Production Deployment

For production deployment, consider:

- Using PostgreSQL or another production database instead of SQLite
- Setting up proper environment variables and secrets management
- Configuring HTTPS/SSL certificates
- Setting up a reverse proxy (Nginx/Traefik)
- Implementing proper backup strategies for the database
- Setting up monitoring and logging
- Configuring resource limits for containers
- Using Docker secrets for sensitive data

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.

## License

This project is part of the AI Agent Builder application suite.