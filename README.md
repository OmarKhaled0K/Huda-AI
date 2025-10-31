# Huda-AI 🌙

An AI-powered assistant designed to help non-Muslims learn about Islam with wisdom, compassion, and clarity. Also it helps muslims to get a duaa, Hadith or mental support.

## 🌟 Features

- Multiple LLM Support (OpenAI, Anthropic, Open-Source LLMs)
- Robust Logging System
- RESTful API with FastAPI
- Configurable Settings
- Modular Architecture

## 📁 Project Structure

```
src/
├── ai/
│   ├── embeddings/      # Embedding models and utilities
│   ├── llms/           # LLM implementations
│   └── prompts/        # System prompts and templates
├── api/
│   └── routers/        # API endpoints and routes
├── config/
│   └── settings/       # Configuration management
├── core/
│   └── services/      # Core business logic
├── schemas/           # Data models and schemas
└── utils/
    └── logging/       # Logging configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- pip (Python package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/OmarKhaled0K/Huda-AI.git
cd Huda-AI
```

2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Configuration

1. Navigate to `src/config/settings`
2. Create necessary environment variables or update settings.py

### Running the Application

From the `src` directory, run:
```bash
uvicorn main:app --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## 🛠️ Development

### Adding a New LLM

1. Create a new file in `src/ai/llms/`
2. Extend the base LLM class
3. Implement required methods
4. Register in `llm_manager.py`

### Creating New Endpoints

1. Add new router in `src/api/routers/`
2. Define schemas in `src/schemas/`
3. Implement services in `src/core/services/`
4. Register router in `main.py`

## 📝 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 📝 TODO List:
- 📋 Containerize the App
- 📋 Create `I am Feeling` dataset:
    - 🔹 Scrape the feelings from [Islamestic](https://www.islamestic.com/i-am-feeling/)
    - 🔹 Store them in a database (didn't decide yet should I use tabular database or vector database)
    - 🔹 Give full credit to [Islamestic](https://www.islamestic.com/i-am-feeling/)
- 📋 Create `I am Feeling` Endpoint v1:
    - 🔹 Accept one or more of `feelings` from a specific list
    - 🔹 Return response (Ayah from Al Qura'n Al Kareem) and (explaination) from the database
- 📋 Add RAG (Steps to v2 of the app)
- 📋 Create `I am feeling` Endpoint v2:
    - 🔹 Give the user the freedom to enter a message
    - 🔹 Extract the intent/feeling from the message
    - 🔹 Return response (Ayah from Al Qura'n Al Kareem) and (explaination) from the database
    - 🔹 [OPTIONAL] Make the LLM respond to the user based on the query (feeling) and the retrieved data (Ayah)

- 📋 Add Agentic RAG (Steps to v3 of the app)
- 📋 Add Multi-Agent Agentic RAG (Steps to v4 of the app)

## 📫 Contact

- Email: omarkhaledcvexpert@gmail.com
- LinkedIn: [Omar Khaled](https://www.linkedin.com/in/dsomarkhaled/)
- GitHub: [OmarKhaled0K](https://github.com/OmarKhaled0K/Huda-AI)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ and ☪️ by Omar Khaled
