# ACEest Fitness & Gym Management System

A comprehensive gym management application built with Flask, SQLAlchemy, and Docker. Features a REST API, web UI, and CI/CD pipeline with Jenkins.

## Features

- **Member Management**: Add, view, delete members; search and filter by name/plan
- **Trainer Management**: Add and view trainers; assign trainers to members
- **Membership Plans**: Assign Basic, Premium, Monthly, or Yearly plans to members
- **Attendance Tracking**: Mark attendance and view history per member
- **BMI Calculator**: Calculate BMI and category from height/weight
- **Payment Tracking**: Record payments and view history with totals
- **Authentication**: Admin login with token-based auth for protected routes
- **Web UI**: Simple interface at `/ui` for interacting with all features
- **Database**: SQLite with SQLAlchemy ORM
- **Docker**: Containerized with Gunicorn for production
- **CI/CD**: Jenkins pipeline for automated testing and deployment

## API Endpoints

### Authentication
- `POST /login` - Admin login (username: admin, password: admin123)

### Members
- `GET /members` - List members (query: ?search=name&plan=plan)
- `POST /members` - Create member
- `DELETE /members/<id>` - Delete member
- `PUT /members/<id>/assign_trainer` - Assign trainer
- `PUT /members/<id>/assign_plan` - Assign plan

### Trainers
- `GET /trainers` - List trainers
- `POST /trainers` - Create trainer

### Attendance
- `POST /attendance` - Mark attendance
- `GET /attendance/<member_id>` - View attendance history

### BMI
- `POST /bmi` - Calculate BMI

### Payments
- `POST /payments` - Create payment
- `GET /payments/<member_id>` - View payment history

### UI
- `GET /ui` - Web interface

## Installation & Setup

### Prerequisites
- Python 3.10+
- Docker
- Jenkins (for CI/CD)

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/2024tm93591-hash/MM_Devops_Assignment1.git
   cd MM_Devops_Assignment1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python gym.py
   ```
   - API available at `http://localhost:5000`
   - UI at `http://localhost:5000/ui`

### Docker Setup
1. Build the image:
   ```bash
   docker build -t gym-app .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 gym-app
   ```

### Jenkins Pipeline
- The `Jenkinsfile` defines a pipeline with stages for dependency installation, testing, Docker build, and container run.
- Configure Jenkins to use the repository and run the pipeline.

## Testing
Run tests with:
```bash
pytest -q
```

## Database
- Uses SQLite (`gym.db`) with SQLAlchemy.
- Tables: Member, Trainer, Attendance, Payment.
- Auto-created on app startup.

## Authentication
- Admin credentials: `admin` / `admin123`
- Protected routes require `Authorization: Bearer <token>` header.
- Token obtained via `/login`.

## Project Structure
```
.
├── gym.py              # Main Flask app
├── wsgi.py             # WSGI entry point
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── Jenkinsfile         # Jenkins pipeline
├── templates/
│   └── index.html      # Web UI
├── tests/
│   └── test_app.py     # Unit tests
└── README.md           # This file
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License
This project is for educational purposes.
