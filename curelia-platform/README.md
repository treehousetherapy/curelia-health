# Curelia Health Platform

A HIPAA-compliant home-care management platform focused on EVV (Electronic Visit Verification), scheduling, caregiver/client records, documents, billing/payroll, and secure messaging.

## Project Overview

Curelia Health Platform is designed to streamline home healthcare operations while maintaining strict HIPAA compliance. The platform provides tools for managing caregivers, clients, scheduling, time tracking, document management, and more.

### Key Features

- **EVV & Scheduling**: Compliant time tracking with GPS verification, shift scheduling with recurrence patterns
- **Caregiver Management**: Credentials, certifications, availability, and assignments
- **Client Management**: Care plans, service needs, and authorized services
- **Document Vault**: Secure document storage with e-signature capabilities
- **HIPAA Compliance**: Comprehensive audit logging, data encryption, and security controls
- **User Management**: Role-based access control with secure authentication

## Architecture

The platform follows a modern, scalable architecture:

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│  React Frontend│     │ FastAPI Backend│     │ PostgreSQL DB  │
│                │◄────►                ◄─────►                │
│                │     │                │     │                │
└────────────────┘     └────────────────┘     └────────────────┘
                              │
                              │
                      ┌───────▼────────┐
                      │                │
                      │  S3 Document   │
                      │    Storage     │
                      │                │
                      └────────────────┘
```

- **Frontend**: React with TypeScript, responsive design for web and mobile
- **Backend**: Python FastAPI, SQLAlchemy ORM, JWT authentication
- **Database**: PostgreSQL with UUID primary keys and soft delete
- **Storage**: S3-compatible object storage for documents
- **Deployment**: Docker containers, Kubernetes orchestration

## Project Structure

```
curelia-platform/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── db/             # Database models and migrations
│   │   ├── middleware/     # Custom middleware
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── main.py             # Application entry point
│
├── frontend/               # React frontend
│   ├── public/             # Static files
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # State management
│   │   └── utils/          # Utility functions
│   └── package.json        # Frontend dependencies
│
├── mobile/                 # React Native mobile app
│   ├── android/            # Android-specific code
│   ├── ios/                # iOS-specific code
│   └── src/                # Shared React Native code
│
└── infrastructure/         # Deployment configuration
    ├── docker/             # Docker configuration
    ├── kubernetes/         # Kubernetes manifests
    └── terraform/          # Infrastructure as code
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Node.js 16+
- Docker (optional)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000, with documentation at http://localhost:8000/api/docs.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5173.

## Development Guidelines

### Code Style

- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint and Prettier configurations

### Database Migrations

Generate migrations after model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Testing

Run backend tests:

```bash
cd backend
pytest
```

Run frontend tests:

```bash
cd frontend
npm test
```

## License

This project is proprietary software. All rights reserved.

## Contact

For questions or support, please contact support@curelia.health. 