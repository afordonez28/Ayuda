from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Modelos ---
class Enemy(BaseModel):
    name: str
    speed: float
    jump: float
    hit_speed: int
    health: int
    type: str
    spawn: float
    probability_spawn: float
    image: str

class Player(BaseModel):
    name: str
    health: int
    regenerate_health: int
    speed: float
    jump: float
    is_dead: bool
    armor: int
    hit_speed: int
    image: str

# --- Base de datos simulada con IDs ---
players_db: List[Dict[str, Any]] = []
enemies_db: List[Dict[str, Any]] = []
deleted_players: List[Dict[str, Any]] = []
deleted_enemies: List[Dict[str, Any]] = []

# --- Datos adicionales (manual) ---
planeacion_db = [
    {"fase": "Ideación", "descripcion": "Definir mecánicas y objetivos."},
    {"fase": "Prototipo", "descripcion": "Bocetos y primeras pruebas."}
]
diseno_db = [
    {"elemento": "Mapa", "descripcion": "Creación de escenarios."},
    {"elemento": "Pixel Art", "descripcion": "Diseño de personajes y enemigos."}
]
objetivo_db = {
    "objetivo": "Crear la interfaz gráfica de un videojuego 2D utilizando PixelArt en Godot Engine, que fomente la creatividad y la capacidad de diseñar mientras el jugador enfrenta oleadas de enemigos."
}
desarrollador_db = {
    "nombre": "Andrés Felipe Ordóñez Carrasco",
    "rol": "Desarrollador de Videojuegos y Software",
    "contacto": "afordonez28@ejemplo.com"
}

# --- Templates frontend ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/players", response_class=HTMLResponse)
def players_page(request: Request):
    return templates.TemplateResponse("players.html", {"request": request})

@app.get("/enemies", response_class=HTMLResponse)
def enemies_page(request: Request):
    return templates.TemplateResponse("enemies.html", {"request": request})

@app.get("/stats", response_class=HTMLResponse)
def stats_page(request: Request):
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "total_players": len(players_db),
            "total_enemies": len(enemies_db),
        }
    )

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# ------------------- API ENDPOINTS -------------------
# Consulta total
@app.get("/api/players/")
def get_players():
    return players_db

@app.get("/api/enemies/")
def get_enemies():
    return enemies_db

# Consulta por ID
@app.get("/api/players/{player_id}")
def get_player_by_id(player_id: int):
    for player in players_db:
        if player["id"] == player_id:
            return player
    raise HTTPException(status_code=404, detail="Jugador no encontrado")

@app.get("/api/enemies/{enemy_id}")
def get_enemy_by_id(enemy_id: int):
    for enemy in enemies_db:
        if enemy["id"] == enemy_id:
            return enemy
    raise HTTPException(status_code=404, detail="Enemigo no encontrado")

# Consulta por nombre o característica (search)
@app.get("/api/players/search/")
def search_players(
    name: Optional[str] = None,
    health: Optional[int] = None,
    armor: Optional[int] = None,
    speed: Optional[float] = None
):
    results = players_db
    if name:
        results = [p for p in results if name.lower() in p["name"].lower()]
    if health is not None:
        results = [p for p in results if p["health"] == health]
    if armor is not None:
        results = [p for p in results if p["armor"] == armor]
    if speed is not None:
        results = [p for p in results if p["speed"] == speed]
    return results

@app.get("/api/enemies/search/")
def search_enemies(
    name: Optional[str] = None,
    type: Optional[str] = None,
    health: Optional[int] = None
):
    results = enemies_db
    if name:
        results = [e for e in results if name.lower() in e["name"].lower()]
    if type:
        results = [e for e in results if type.lower() in e["type"].lower()]
    if health is not None:
        results = [e for e in results if e["health"] == health]
    return results

# Crear
@app.post("/api/players/")
def create_player(player: Player):
    new_id = 1 if not players_db else max(p["id"] for p in players_db) + 1
    player_dict = player.dict()
    player_dict["id"] = new_id
    players_db.append(player_dict)
    return {"message": "Jugador creado", "id": new_id}

@app.post("/api/enemies/")
def create_enemy(enemy: Enemy):
    new_id = 1 if not enemies_db else max(e["id"] for e in enemies_db) + 1
    enemy_dict = enemy.dict()
    enemy_dict["id"] = new_id
    enemies_db.append(enemy_dict)
    return {"message": "Enemigo creado", "id": new_id}

# Modificación total (PUT)
@app.put("/api/players/{player_id}")
def update_player(player_id: int, player: Player):
    for i, p in enumerate(players_db):
        if p["id"] == player_id:
            player_dict = player.dict()
            player_dict["id"] = player_id
            players_db[i] = player_dict
            return {"message": "Jugador actualizado"}
    raise HTTPException(status_code=404, detail="Jugador no encontrado")

@app.put("/api/enemies/{enemy_id}")
def update_enemy(enemy_id: int, enemy: Enemy):
    for i, e in enumerate(enemies_db):
        if e["id"] == enemy_id:
            enemy_dict = enemy.dict()
            enemy_dict["id"] = enemy_id
            enemies_db[i] = enemy_dict
            return {"message": "Enemigo actualizado"}
    raise HTTPException(status_code=404, detail="Enemigo no encontrado")

# Modificación parcial (PATCH)
@app.patch("/api/players/{player_id}")
def patch_player(player_id: int, player_patch: dict):
    for i, p in enumerate(players_db):
        if p["id"] == player_id:
            players_db[i].update(player_patch)
            return {"message": "Jugador modificado parcialmente"}
    raise HTTPException(status_code=404, detail="Jugador no encontrado")

@app.patch("/api/enemies/{enemy_id}")
def patch_enemy(enemy_id: int, enemy_patch: dict):
    for i, e in enumerate(enemies_db):
        if e["id"] == enemy_id:
            enemies_db[i].update(enemy_patch)
            return {"message": "Enemigo modificado parcialmente"}
    raise HTTPException(status_code=404, detail="Enemigo no encontrado")

# Eliminar uno (con historial, por ID)
@app.delete("/api/players/{player_id}")
def delete_player(player_id: int):
    for i, p in enumerate(players_db):
        if p["id"] == player_id:
            deleted_players.append(players_db[i])
            players_db.pop(i)
            return {"message": "Jugador eliminado y guardado en historial"}
    raise HTTPException(status_code=404, detail="Jugador no encontrado")

@app.delete("/api/enemies/{enemy_id}")
def delete_enemy(enemy_id: int):
    for i, e in enumerate(enemies_db):
        if e["id"] == enemy_id:
            deleted_enemies.append(enemies_db[i])
            enemies_db.pop(i)
            return {"message": "Enemigo eliminado y guardado en historial"}
    raise HTTPException(status_code=404, detail="Enemigo no encontrado")

# Eliminar todos (con historial)
@app.delete("/api/players/")
def delete_all_players():
    global deleted_players
    deleted_players.extend(players_db.copy())
    players_db.clear()
    return {"message": "Todos los jugadores eliminados"}

@app.delete("/api/enemies/")
def delete_all_enemies():
    global deleted_enemies
    deleted_enemies.extend(enemies_db.copy())
    enemies_db.clear()
    return {"message": "Todos los enemigos eliminados"}

# Historial
@app.get("/api/players/history/")
def get_deleted_players():
    return deleted_players

@app.get("/api/enemies/history/")
def get_deleted_enemies():
    return deleted_enemies

# Estadísticas
@app.get("/api/stats/")
def get_stats():
    return {
        "total_players": len(players_db),
        "total_enemies": len(enemies_db),
    }

# Endpoint info desarrollador
@app.get("/api/desarrollador")
def get_desarrollador():
    return desarrollador_db

# Endpoint planeación
@app.get("/api/planeacion")
def get_planeacion():
    return planeacion_db

# Endpoint diseño
@app.get("/api/diseno")
def get_diseno():
    return diseno_db

# Endpoint objetivo
@app.get("/api/objetivo")
def get_objetivo():
    return objetivo_db

# Manejo de errores
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)