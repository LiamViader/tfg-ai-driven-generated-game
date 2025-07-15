current_status = {
    "status": "idle",     # idle | running | done | error
    "progress": 0.0,
    "message": "Esperando a iniciar generación..."
}

def update_global_progress(global_progress: float, message: str = ""):
    current_status["progress"] = global_progress
    current_status["message"] = message

def set_done():
    current_status["status"] = "done"
    current_status["progress"] = 1.0
    current_status["message"] = "Generación completada"

def set_error(message: str):
    current_status["status"] = "error"
    current_status["progress"] = 0.0
    current_status["message"] = message

def reset():
    current_status["status"] = "running"
    current_status["progress"] = 0.01
    current_status["message"] = "Inicializando generación..."

def get_status():
    return current_status