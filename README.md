# Patient Dashboard Application

A web application for viewing patient summary data with role-based access control. The application consists of a React frontend and a FastAPI backend with MongoDB database.

## Features

- **Authentication**: JWT-based login system with username/password
- **Role-based Access**: Different user types with different data access levels
- **Patient Data**: Protected patient endpoints that return different data based on user type
- **Patient Forms**: View patient visit forms with question descriptions and answers
- **Visit Interface**: Blue "Visit" button on patient pages to view detailed form data
- **XML Data Storage**: Full XML patient summaries stored and accessible based on user permissions
- **Modern UI**: Clean, responsive React frontend with expandable sections
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

## Sample Patients

The migration script creates two sample patients from XML files:

- **Christopher C Dowd** (ID: 1) - Male, DOB: 12/28/1970
- **Constance E. Bratcher** (ID: 2) - Female, goes by "Connie"

## Question Schema

The migration script creates question schema data from `question_schema.json`:

- **Visit Types**: SOC, RN, DC, PTEVAL, PTVIS
- **Categories**: Patient_Tracking, Administrative, Vitals, Patient_History_and_Prognosis, etc.
- **Questions**: 913 total questions with qid (primary key), description, casting, and optional subitems
- **Sample Questions**:
  - `r_provided_cfc12d` - "Location of care provided" (SOC/Patient_Tracking)
  - `t_limit_dcf1c7` - "Patient's last name" (SOC/Patient_Tracking)
  - `t_limit_c33e28` - "Patient's first name" (SOC/Patient_Tracking)

## Patient Forms

The migration script creates patient forms from `form_response_*.json` files:

- **Form Types**: SOC, RN, DC, PTEVAL, PTVIS (matching question schema)
- **Structure**: Each form includes patient_id, form_date, form_type, and survey_data
- **Survey Data**: Enhanced with question descriptions from the question schema
- **Sample Forms**:
  - Christopher's SOC form (Patient ID: 1)
  - Connie's PTEVAL form (Patient ID: 2)

## API Endpoints

### Public Endpoints
- `GET /status` - Health check
- `POST /auth/login` - User authentication

### Protected Endpoints
- `GET /patients` - Get patient data (requires authentication)
- `GET /patients/{patient_id}` - Get specific patient by ID (requires authentication)
- `GET /auth/me` - Get current user information (requires authentication)
- `GET /questions/{qid}` - Get specific question by qid (requires authentication)
- `GET /questions/` - Get questions with optional filtering by visit_type and category (requires authentication)
- `GET /forms/` - Get forms with optional filtering by patient_id and form_type (requires authentication)
- `GET /forms/{form_id}` - Get specific form by form_id (requires authentication)
- `GET /forms/patient/{patient_id}` - Get all forms for a specific patient (requires authentication)

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
