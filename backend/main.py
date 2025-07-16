from fastapi import FastAPI
from api.routes import game
from api.routes import assets



app = FastAPI(
    title="Backend del Juego Generado por IA",
    version="0.1.0",
    description="API para generar y gestionar el estado del juego"
)

app.include_router(game.router, prefix="/game", tags=["Game"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])


# Aditional route to know if it's running
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Server running"}
