# Portfolio Website

A modern portfolio website built with React (frontend) and FastAPI (backend), featuring a chatbot assistant.

## Features

- Interactive UI with a cold color scheme
- Project showcase with filtering capabilities
- Skills visualization
- Resume section with downloadable PDF
- Interactive chatbot assistant
- Responsive design for all devices

## Tech Stack

### Frontend
- React
- Context API for state management
- CSS with variables for theming
- Axios for API requests

### Backend
- FastAPI
- JSON-based data storage
- Rule-based chatbot implementation

## Getting Started

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- Docker (optional)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/portfolio-website.git
cd portfolio-website
```

2. Start the backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. Start the frontend
```bash
cd frontend
npm install
npm start
```

### Using Docker
```bash
docker-compose up
```

## Project Structure

The project follows a clean architecture with separate frontend and backend components:

- `frontend/`: React application
- `backend/`: FastAPI application
- `docker-compose.yml`: Docker configuration for development and deployment 