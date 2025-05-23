# TFG – AI-Generated and Directed Video Game

This repository contains both the AI backend (LangGraph + Python agents) and the Unity-based frontend for the TFG project.

📂 `backend/` – Narrative generation, map structure, and agent system  
🎮 `unity-client/` – Unity project for interaction and game interface  
🛠️ `scripts/` – Tools and utilities (e.g., exporters, benchmarks)


## 🛠️ Setup Instructions

### 🔁 Backend (Python 3.10+ recommended)

1. Make sure you have **Python 3.10 or higher** installed:
```bash
   python --version
```
If not, download it from https://www.python.org/downloads/

2. Create and activate a virtual environment:
```bash
    cd backend
    python -m venv .venv
    .venv\Scripts\activate      # On Windows
```

3. Install backend dependencies:
```bash
    pip install -r requirements.txt
```

4. Run the backend entrypoint:
```bash
    python main.py
```
### 🎮 Unity Frontend

1. Open the folder unity-client/ in Unity Hub or Unity Editor.

2. Build and run the scene as usual.

## ✅ Quick Start
```bash
    cd backend
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py
```
