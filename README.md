# Patient Dashboard Application

A web application for viewing patient summary data with role-based access control. The application consists of a React frontend and a FastAPI backend with MongoDB database.

## Features

- **Authentication**: JWT-based login system with username/password
- **Role-based Access**: Different user types with different data access levels
- **Patient Data**: Protected patient endpoints that return different data based on user type
- **Modern UI**: Clean, responsive React frontend
- **RESTful API**: FastAPI backend with automatic documentation

## User Types

- **Field Clinician**: Need quick, mobile-friendly summaries before patient visits
- **Quality Administrator**: Conduct detailed, thorough documentation review for error-prone insurance claims

## Project Structure

```
rogerday2/
├── frontend/                 # React frontend application
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── core/            # Configuration and database setup
│   │   ├── models/          # Data models
│   │   └── routers/         # API endpoints
│   └── tests/               # Backend tests
├── scripts/                 # Database migration scripts
├── infrastructure/          # Docker configuration files
├── docker-compose.yml       # Docker Compose configuration
└── Makefile                 # Build and deployment commands
```

## Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile commands)

## Quick Start

1. **Build the application:**
   ```bash
   make build
   ```

2. **Run the entire stack:**
   ```bash
   make run
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Default Users

The migration script creates two default users:

- **Username**: `Bob`, **Password**: `test`, **Type**: Field Clinician
- **Username**: `Alice`, **Password**: `test`, **Type**: Quality Administrator

## API Endpoints

### Public Endpoints
- `GET /status` - Health check
- `POST /auth/login` - User authentication

### Protected Endpoints
- `GET /patients` - Get patient data (requires authentication)

## Development

### Backend Development

1. **Install Poetry dependencies:**
   ```bash
   cd backend
   poetry install
   ```

2. **Run the development server:**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

3. **Run tests:**
   ```bash
   poetry run pytest
   ```

### Frontend Development

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm start
   ```

3. **Run tests:**
   ```bash
   npm test
   ```

## Docker Commands

### Build and Run
```bash
# Build all services
make build

# Run the stack
make run

# View logs
make logs

# Check status
make status
```

### Cleanup
```bash
# Stop and remove everything
make clean
```

### Database Migration
```bash
# Run migration manually
make migrate
```

## Testing

Run all tests:
```bash
make test
```

## Environment Variables

### Backend
- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `DATABASE_NAME`: Database name (default: `patient_dashboard`)
- `SECRET_KEY`: JWT secret key (change in production)

### Frontend
- `REACT_APP_API_URL`: Backend API URL (default: `http://localhost:8000`)

## Production Deployment

For production deployment:

1. Update the `SECRET_KEY` in the backend configuration
2. Configure proper CORS origins
3. Use environment-specific Docker Compose files
4. Set up proper MongoDB authentication
5. Configure reverse proxy (nginx) for the frontend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
