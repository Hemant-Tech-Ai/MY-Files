Detailed Portfolio Website Architecture
Backend Architecture (FastAPI)
Core Components

Main Application Entry Point (main.py)

Initializes the FastAPI application
Configures CORS middleware to allow requests from the React frontend
Includes all route modules
Sets up exception handlers and middleware


Configuration Management (config.py)

Loads environment variables
Contains configuration classes for different environments (development, production)
Manages secrets and API keys for any external services


Data Storage and Access

JSON files in the data/ directory store structured information:

resume.json: Education, work experience, certifications
skills.json: Technical skills with proficiency levels and categorization
projects.json: Project descriptions, technologies, links, images
chatbot_training_data.json: Intent-response mappings for chatbot





API Routes Structure

Portfolio Routes (routes/portfolio.py)

GET /api/portfolio/overview: Returns basic portfolio information
GET /api/portfolio/stats: Returns aggregated statistics about skills and projects


Projects Routes (routes/projects.py)

GET /api/projects: Lists all projects with filtering capabilities
GET /api/projects/{project_id}: Returns detailed information about a specific project


Skills Routes (routes/skills.py)

GET /api/skills: Returns skills grouped by categories
GET /api/skills/top: Returns top skills based on proficiency


Resume Routes (routes/resume.py)

GET /api/resume: Returns formatted resume data
GET /api/resume/experience: Returns only work experience
GET /api/resume/education: Returns educational background


Chatbot Routes (routes/chatbot.py)

POST /api/chatbot/query: Accepts user messages and returns appropriate responses
GET /api/chatbot/context: Retrieves contextual information for the chatbot



Chatbot Service Implementation

Rule-Based Response System (services/chatbot_service.py)

Intent recognition function to categorize user queries (skills, projects, experience, etc.)
Pattern matching with predefined templates and keywords
Entity extraction to identify specific skills or projects mentioned


Response Generation

Context-aware response formatting
Data retrieval functions to pull relevant information from JSON files
Fallback responses for unrecognized queries


Optional NLP Integration

Interface for connecting to external NLP services if needed
Simple vector embedding for better query matching



Frontend Architecture (React)
UI Component Hierarchy

Layout Components

Layout.jsx: Main wrapper component with consistent styling
Navbar.jsx: Responsive navigation with smooth scrolling to sections
Footer.jsx: Contact information and social links


Section Components

Hero.jsx: Full-screen landing section with animation
About.jsx: Personal introduction and background
Skills.jsx: Interactive skill visualization (possibly with charts)
Projects.jsx: Grid/carousel of project cards with filtering
Experience.jsx: Timeline of work and internship experiences
Resume.jsx: Downloadable resume and key highlights
Contact.jsx: Contact form and professional links


Chatbot UI Components

Chatbot.jsx: Main chatbot container that floats on the page
ChatMessage.jsx: Individual message bubbles with styling for user/bot
ChatInput.jsx: Input field with send button and suggestions



State Management

Context API Implementation

ChatbotContext.jsx: Manages chatbot conversation history and state
Provides functions for sending messages and managing chat visibility


Custom Hooks

useFetch.js: Handles API requests with loading/error states
useChatbot.js: Encapsulates chatbot interaction logic



API Integration

Services Layer

api.js: Axios configuration with interceptors for error handling
Organized API functions for each endpoint category
Response transformation and data normalization


Chatbot Communication Flow

User input captured in ChatInput.jsx
Messages stored in context state
Requests sent to backend through chatbotService.js
Responses displayed as new chat messages



Cold Color Scheme Implementation

Design System

Primary colors: Deep blues (#0A192F, #172A45)
Secondary colors: Teals (#64FFDA), light blues (#8892B0)
Accent colors: Light purples (#C792EA), subtle grays (#CCD6F6)


CSS Architecture

CSS variables for consistent color application
Dark mode support with color transformations
Component-specific styling with consistent theming



Data Flow Architecture

Portfolio Data Loading

Initial app load fetches core data from backend
Data cached in memory for fast access
Lazy loading for detailed project information


Chatbot Interaction Sequence

User types question in chat interface
Frontend sends query to /api/chatbot/query endpoint
Backend analyzes query using chatbot service
Relevant data extracted from JSON files
Formatted response generated and returned
Frontend displays response in chat interface


Content Update Process

Backend JSON files serve as the single source of truth
Updates to skills, projects, or resume only require JSON modifications



Deployment Architecture

Docker Implementation

Dockerfile for frontend: Node.js base image, build process, Nginx for serving
Dockerfile for backend: Python base image, dependency installation, Uvicorn server
docker-compose.yml: Orchestrates both services with appropriate networking


Environment Configuration

Development variables for local testing
Production variables for deployment
Secrets management for any API keys or sensitive information


Hosting Considerations

Static frontend can be deployed to CDN or static hosting
FastAPI backend requires Python runtime environment
Both can be deployed to cloud platforms (AWS, Azure, GCP, etc.)