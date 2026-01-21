from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import pandas as pd
import os
import glob
from datetime import datetime

app = FastAPI(title="Доставка Якутск")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def web_app(request: Request, user_id: int = None):
    if not user_id:
        return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head><title>Ошибка</title></head>
            <body style="background: #0f0f0f; color: white; padding: 40px; text-align: center;">
                <h1>🔒 Откройте через Telegram бота</h1>
            </body>
            </html>
        """)
    return templates.TemplateResponse("app.html", {"request": request, "user_id": user_id})

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user: raise HTTPException(404, "User not found")
    return {
        "telegram_id": user[1], "phone": user[2], "name": user[3],
        "client_code": user[4], "role": user[5], "registered": user[6]
    }

@app.get("/api/search/{track}")
async def search_track(track: str, user_id: int):
    track = track.upper().strip()
    files = find_excel_files()
    for name, path in files.items():
        try:
            df = pd.read_excel(path, dtype=str)
            for i in range(min(2000, len(df))):
                for j in range(min(100, len(df.columns))):
                    if track in str(df.iat[i, j]):
                        save_package(track, user_id, get_location_name(name))
                        return {"found": True, "track": track, "location": get_location_name(name)}
        except: continue
    return {"found": False, "track": track}

@app.get("/api/packages/{user_id}")
async def get_packages(user_id: int):
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.* FROM packages p
        JOIN users u ON p.user_id = u.id
        WHERE u.telegram_id = ? ORDER BY p.added_date DESC
    ''', (user_id,))
    packages = cursor.fetchall()
    conn.close()
    return [{"track": p[1], "location": p[3], "status": p[4], 
             "weight": p[5], "price": p[6], "added_date": p[7]} for p in packages]

def find_excel_files():
    files = {}
    for path in glob.glob("excel_files/*.xlsx"):
        name = os.path.basename(path).lower()
        if "китай" in name or "china" in name:
            files["china"] = path
        elif "уссурийск" in name or "ussuriysk" in name:
            files["ussuriysk"] = path
        else:
            files["yakutsk"] = path
    return files

def get_location_name(key):
    return {"china": "Китай 🇨🇳", "ussuriysk": "Уссурийск 🇷🇺"}.get(key, "Якутск 🇷🇺")

def save_package(track, user_id, location):
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        cursor.execute("SELECT id FROM packages WHERE track = ? AND user_id = ?", (track, user[0]))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO packages (track, user_id, location, added_date)
                VALUES (?, ?, ?, ?)
            ''', (track, user[0], location, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)