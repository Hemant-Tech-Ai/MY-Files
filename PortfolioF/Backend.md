backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py (optional if using DB)
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── portfolio.py
│   │   ├── projects.py
│   │   ├── skills.py
│   │   ├── resume.py
│   │   └── chatbot.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── chatbot_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── data/
│       ├── resume.json
│       ├── skills.json
│       ├── projects.json
│       └── chatbot_training_data.json
├── requirements.txt
├── Dockerfile
└── .env.example