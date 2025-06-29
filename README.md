# 🏥 Curelia Health Platform

**HIPAA-Compliant Healthcare Management Platform**

A comprehensive healthcare management solution designed for modern care coordination, inspired by industry best practices and built with security-first architecture.

## 🏗️ Architecture Overview

```
┌─────────────────┬─────────────────┬─────────────────┐
│   Frontend      │     Mobile      │   Backend API   │
│   (React)       │ (React Native)  │   (FastAPI)     │
├─────────────────┼─────────────────┼─────────────────┤
│ • Patient Portal│ • Caregiver App │ • JWT Auth      │
│ • Admin Dashboard│ • Schedule Mgmt │ • CRUD APIs     │
│ • Billing UI    │ • Secure Chat   │ • File Upload   │
│ • Analytics     │ • GPS Check-in  │ • Audit Logs    │
└─────────────────┴─────────────────┴─────────────────┘
                           │
                    ┌─────────────────┐
                    │   Database      │
                    │  (PostgreSQL)   │
                    ├─────────────────┤
                    │ • Patient Data  │
                    │ • Appointments  │
                    │ • Billing       │
                    │ • Audit Trail   │
                    └─────────────────┘
                           │
                    ┌─────────────────┐
                    │ Cloud Infra     │
                    │ (GCP + Terraform)│
                    ├─────────────────┤
                    │ • VPC Security  │
                    │ • Cloud Run     │
                    │ • Cloud SQL     │
                    │ • Secret Mgmt   │
                    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend Web Application
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **Routing**: React Router v6
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios with auth interceptors
- **Testing**: Vitest + React Testing Library

**Rationale**: React ecosystem provides mature tooling, excellent TypeScript support, and large community. Vite offers superior developer experience with fast HMR. TanStack Query handles server state elegantly with caching and background updates.

### Mobile Application
- **Framework**: React Native with Expo SDK
- **Build System**: EAS (Expo Application Services)
- **Storage**: MMKV for offline caching
- **Authentication**: Biometric login support
- **Push Notifications**: Firebase FCM/APNs
- **Maps**: React Native Maps for GPS features

**Rationale**: Expo provides streamlined development and deployment while maintaining native performance. EAS enables professional-grade CI/CD for app stores.

### Backend API
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 15 with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT with refresh tokens
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Testing**: Pytest with asyncio support

**Rationale**: FastAPI offers excellent performance, automatic API documentation, and native async support. Python's ecosystem provides robust libraries for healthcare data processing and ML capabilities.

### Infrastructure
- **Cloud Provider**: Google Cloud Platform
- **Infrastructure as Code**: Terraform
- **Container Platform**: Cloud Run (serverless containers)
- **Database**: Cloud SQL (PostgreSQL)
- **Storage**: Cloud Storage with lifecycle policies
- **Security**: VPC Service Controls, Binary Authorization
- **Monitoring**: Cloud Monitoring + Alerting

**Rationale**: GCP provides comprehensive HIPAA-compliant services with strong security controls. Cloud Run offers automatic scaling and cost efficiency.

## 📁 Project Structure

```
curelia-health/
├── frontend/           # React web application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/            # FastAPI application
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── mobile/             # React Native Expo app
│   ├── src/
│   ├── app.json
│   └── package.json
├── infra/              # Terraform infrastructure
│   ├── modules/
│   ├── environments/
│   └── main.tf
├── design/             # UI/UX assets
│   ├── wireframes/
│   ├── mockups/
│   └── design-tokens/
├── analytics/          # Event tracking schemas
│   ├── events/
│   └── amplitude-config/
├── .github/            # CI/CD workflows
│   └── workflows/
└── docs/               # Documentation
    ├── api/
    ├── deployment/
    └── security/
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.12+ with pip
- **PostgreSQL** 15+
- **Docker** (optional, for containerized development)
- **Git** for version control

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/curelia-health.git
   cd curelia-health
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your database credentials
   
   # Run database migrations
   alembic upgrade head
   
   # Start the API server
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Set up environment variables
   cp .env.example .env.local
   
   # Start the development server
   npm run dev
   ```

4. **Mobile Setup**
   ```bash
   cd mobile
   npm install
   
   # Start Expo development server
   npx expo start
   ```

### Environment Variables

Create the following environment files:

**Backend (.env)**:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/curelia_health
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:19006
```

**Frontend (.env.local)**:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

## 🔒 Security & Compliance

### HIPAA Compliance Features

- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Access Controls**: Role-based permissions (Patient, Staff, Admin)
- **Audit Logging**: Comprehensive activity tracking
- **Data Minimization**: Collect only necessary PHI
- **Breach Detection**: Automated monitoring and alerting

### Security Measures

- JWT authentication with secure refresh tokens
- Rate limiting and DDoS protection
- OWASP security headers implementation
- Regular security scanning with OWASP ZAP
- Dependency vulnerability monitoring

## 🧪 Testing Strategy

- **Unit Tests**: Jest/Vitest for components and functions
- **Integration Tests**: API endpoint testing with Pytest
- **E2E Tests**: Playwright for critical user journeys
- **Load Testing**: k6 for performance validation
- **Security Testing**: Automated OWASP ZAP scans

## 📊 Monitoring & Analytics

- **Application Monitoring**: Cloud Monitoring dashboards
- **Error Tracking**: Structured logging and alerting
- **Performance Metrics**: Core Web Vitals tracking
- **User Analytics**: Amplitude for product insights
- **Uptime Monitoring**: SLA tracking and alerting

## 🚀 Deployment

### Development
```bash
# Deploy to development environment
./scripts/deploy-dev.sh
```

### Production
```bash
# Deploy to production with blue-green strategy
./scripts/deploy-prod.sh
```

### Mobile App Deployment
```bash
# Build and submit to app stores
eas build --platform all
eas submit --platform all
```

## 📈 Roadmap

- [x] Project initialization and architecture setup
- [ ] Core authentication and user management
- [ ] Patient registration and profile management
- [ ] Caregiver scheduling system
- [ ] Secure messaging platform
- [ ] Billing and payment processing
- [ ] Mobile app development
- [ ] Analytics and reporting dashboard
- [ ] HIPAA compliance audit
- [ ] Beta testing program
- [ ] Production launch

## 🤝 Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or questions:
- **Email**: support@curelia.health
- **Documentation**: [docs.curelia.health](https://docs.curelia.health)
- **Issues**: [GitHub Issues](https://github.com/your-org/curelia-health/issues)

---

**Built with ❤️ for better healthcare outcomes** 