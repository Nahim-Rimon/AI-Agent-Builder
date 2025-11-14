# Docker Setup for AI Agent Builder

This project is dockerized with Docker Compose for easy deployment and development.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v3.8 or higher

## Project Structure

- **Backend**: FastAPI application running on port 8000
- **Frontend**: React application served via Nginx on port 3000
- **Database**: SQLite database stored in persistent volume (`ai_agent_builder.db`)
- **Persistent Storage**: `./app` directory mounted for app data

## Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop all services:**
   ```bash
   docker-compose down
   ```

4. **Stop and remove volumes:**
   ```bash
   docker-compose down -v
   ```

## Services

### Backend Service
- **Container**: `ai-agent-builder-backend`
- **Port**: 8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: SQLite stored in `/app/data/ai_agent_builder.db`
- **Persistent Volume**: 
  - Database: `app_data` volume → `/app/data`
  - App Data: `./app` directory → `/app/app-data`

### Frontend Service
- **Container**: `ai-agent-builder-frontend`
- **Port**: 3000 (mapped to container port 80)
- **URL**: http://localhost:3000
- **Build**: Multi-stage build with Nginx for production

## Persistent Volumes

1. **Database Volume** (`app_data`):
   - Stores the SQLite database file
   - Named volume: `ai-agent-builder-data`
   - Mounted at: `/app/data` in backend container

2. **App Data Volume** (`./app`):
   - Persistent directory for application data
   - Bind mount from host `./app` to container `/app/app-data`
   - Created automatically if it doesn't exist

## Environment Variables

### Backend
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./data/ai_agent_builder.db`)
- `PYTHONUNBUFFERED`: Set to 1 for immediate log output

### Frontend
- `REACT_APP_API_BASE`: Backend API URL (default: `http://localhost:8000`)

## Development

### Rebuild after code changes:
```bash
docker-compose up -d --build
```

### View backend logs:
```bash
docker-compose logs -f backend
```

### View frontend logs:
```bash
docker-compose logs -f frontend
```

### Execute commands in backend container:
```bash
docker-compose exec backend bash
```

### Execute commands in frontend container:
```bash
docker-compose exec frontend sh
```

## Database

The database is stored in a persistent volume. To reset the database:

1. Stop the containers:
   ```bash
   docker-compose down
   ```

2. Remove the volume:
   ```bash
   docker volume rm ai-agent-builder-data
   ```

3. Start again:
   ```bash
   docker-compose up -d
   ```

## Troubleshooting

### Port already in use
If ports 8000 or 3000 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

### Database permissions
If you encounter database permission issues, ensure the `./app` directory has proper permissions:
```bash
mkdir -p ./app
chmod 755 ./app
```

### Rebuild from scratch
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

For production, consider:
1. Using PostgreSQL instead of SQLite
2. Setting up proper environment variables
3. Configuring HTTPS/SSL
4. Setting up reverse proxy (nginx/traefik)
5. Using Docker secrets for sensitive data
6. Setting up proper backup strategy for volumes

