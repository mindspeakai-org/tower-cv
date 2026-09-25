from fastapi import FastAPI, Query, HTTPException
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

app = FastAPI(title="Tower Context API", description="Query historical events detected by Tower CV")

DB_PATH = "data/tower_events.db"

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database connection failed.")

@app.get("/api/events", response_model=List[Dict[str, Any]])
def get_events(
    limit: int = Query(50, ge=1, le=500, description="Max events to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type (e.g. stationary_prolonged)"),
    object_id: Optional[str] = Query(None, description="Filter by specific object (e.g. person_1)"),
    hours_ago: Optional[float] = Query(24, description="Events from the last X hours")
):
    """
    Retrieve historical contextual events.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate the timestamp cutoff
    current_time = datetime.now().timestamp()
    time_cutoff = current_time - (hours_ago * 3600)
    
    query = "SELECT * FROM events WHERE timestamp >= ?"
    params = [time_cutoff]
    
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)
        
    if object_id:
        query += " AND object_id = ?"
        params.append(object_id)
        
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Parse JSON payloads back to dicts
    events = []
    for row in rows:
        event = dict(row)
        if event.get("payload"):
            try:
                event["payload"] = json.loads(event["payload"])
            except json.JSONDecodeError:
                pass
        events.append(event)
        
    return events

@app.get("/api/summary")
def get_daily_summary():
    """
    Returns a quick aggregate summary of today's events.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    time_cutoff = datetime.now().timestamp() - (24 * 3600)
    
    cursor.execute('''
        SELECT event_type, COUNT(*) as count 
        FROM events 
        WHERE timestamp >= ? 
        GROUP BY event_type
    ''', (time_cutoff,))
    
    rows = cursor.fetchall()
    conn.close()
    
    summary = {row["event_type"]: row["count"] for row in rows}
    
    # Example AI-friendly summary string
    if summary:
        text_summary = "In the last 24 hours, Tower saw: " + ", ".join([f"{v} {k} events" for k, v in summary.items()]) + "."
    else:
        text_summary = "Tower hasn't recorded any events in the last 24 hours."
        
    return {
        "summary_data": summary,
        "text_summary": text_summary
    }

if __name__ == "__main__":
    import uvicorn
    # Run the API on port 8000
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
