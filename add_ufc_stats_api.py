#!/usr/bin/env python3
"""
Добавляем API endpoints для ufc.stats в backend/app.py
"""

def add_ufc_stats_endpoints():
    """Добавляем endpoints для ufc.stats"""
    
    api_code = '''
# UFC Stats API endpoints
@app.get("/api/ufc-stats/fighters", response_model=List[dict])
async def get_ufc_stats_fighters(db: Session = Depends(get_db)):
    """Получить всех бойцов ufc.stats"""
    try:
        fighters = db.execute("SELECT * FROM ufc_stats_fighters ORDER BY name").fetchall()
        return [{"id": f[0], "name": f[1], "total_fights": f[2], "total_wins": f[3], 
                "total_losses": f[4], "total_draws": f[5], "total_knockdowns": f[6],
                "total_significant_strikes": f[7], "total_takedowns": f[8]} for f in fighters]
    except Exception as e:
        return []

@app.get("/api/ufc-stats/fighters/{fighter_id}")
async def get_ufc_stats_fighter(fighter_id: int, db: Session = Depends(get_db)):
    """Получить конкретного бойца ufc.stats"""
    try:
        fighter = db.execute("SELECT * FROM ufc_stats_fighters WHERE id = ?", (fighter_id,)).fetchone()
        if fighter:
            return {"id": fighter[0], "name": fighter[1], "total_fights": fighter[2], 
                   "total_wins": fighter[3], "total_losses": fighter[4], "total_draws": fighter[5],
                   "total_knockdowns": fighter[6], "total_significant_strikes": fighter[7], 
                   "total_takedowns": fighter[8]}
        return {"error": "Боец не найден"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/ufc-stats/search")
async def search_ufc_stats_fighters(q: str, db: Session = Depends(get_db)):
    """Поиск бойцов ufc.stats"""
    try:
        fighters = db.execute("SELECT * FROM ufc_stats_fighters WHERE name LIKE ? ORDER BY name", 
                            (f"%{q}%",)).fetchall()
        return [{"id": f[0], "name": f[1], "total_fights": f[2], "total_wins": f[3], 
                "total_losses": f[4], "total_draws": f[5], "total_knockdowns": f[6],
                "total_significant_strikes": f[7], "total_takedowns": f[8]} for f in fighters]
    except Exception as e:
        return []

@app.get("/api/ufc-stats/stats")
async def get_ufc_stats_summary(db: Session = Depends(get_db)):
    """Получить статистику ufc.stats"""
    try:
        total_fighters = db.execute("SELECT COUNT(*) FROM ufc_stats_fighters").fetchone()[0]
        top_fighters = db.execute("""
            SELECT name, total_fights, total_wins, total_losses, total_knockdowns, 
                   total_significant_strikes, total_takedowns 
            FROM ufc_stats_fighters 
            WHERE total_fights > 0 
            ORDER BY total_fights DESC 
            LIMIT 10
        """).fetchall()
        
        return {
            "total_fighters": total_fighters,
            "top_fighters": [{"name": f[0], "total_fights": f[1], "total_wins": f[2], 
                            "total_losses": f[3], "total_knockdowns": f[4],
                            "total_significant_strikes": f[5], "total_takedowns": f[6]} for f in top_fighters]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/ufc-stats/update")
async def update_ufc_stats_data():
    """Обновить данные ufc.stats"""
    try:
        import subprocess
        result = subprocess.run(['python', 'update_ufc_stats.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return {"message": "Данные ufc.stats обновлены", "output": result.stdout}
        else:
            return {"error": "Ошибка обновления", "output": result.stderr}
    except Exception as e:
        return {"error": str(e)}
'''
    
    print("📝 API код для ufc.stats:")
    print(api_code)
    
    # Сохраняем в файл
    with open('ufc_stats_api_endpoints.py', 'w', encoding='utf-8') as f:
        f.write(api_code)
    
    print("\n✅ API код сохранен в ufc_stats_api_endpoints.py")
    print("📋 Добавьте этот код в backend/app.py после существующих endpoints")

if __name__ == "__main__":
    add_ufc_stats_endpoints()
