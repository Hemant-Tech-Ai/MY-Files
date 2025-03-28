frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   ├── robots.txt
│   └── assets/
│       ├── images/
│       ├── icons/
│       └── documents/ (resume PDF, etc.)
├── src/
│   ├── index.js
│   ├── App.js
│   ├── index.css
│   ├── components/
│   │   ├── common/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── Layout.jsx
│   │   │   └── Card.jsx
│   │   ├── Hero.jsx
│   │   ├── About.jsx
│   │   ├── Skills.jsx
│   │   ├── Projects.jsx
│   │   ├── Experience.jsx
│   │   ├── Resume.jsx
│   │   ├── Contact.jsx
│   │   └── chatbot/
│   │       ├── Chatbot.jsx
│   │       ├── ChatMessage.jsx
│   │       └── ChatInput.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── ProjectDetails.jsx
│   │   └── NotFound.jsx
│   ├── services/
│   │   ├── api.js
│   │   └── chatbotService.js
│   ├── hooks/
│   │   ├── useFetch.js
│   │   └── useChatbot.js
│   ├── context/
│   │   └── ChatbotContext.jsx
│   ├── utils/
│   │   └── helpers.js
│   ├── constants/
│   │   ├── routes.js
│   │   └── theme.js
│   └── styles/
│       ├── global.css
│       ├── variables.css
│       └── components/
│           ├── chatbot.css
│           └── project.css
├── package.json
├── postcss.config.js
├── tailwind.config.js (if using Tailwind CSS)
├── .env.example
└── Dockerfile