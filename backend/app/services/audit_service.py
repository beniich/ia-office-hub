
import sqlite3
from datetime import datetime

class AuditLogger:
    def log(self, project_id, action, status):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ai_logs (project_id, action_performed, status, timestamp) VALUES (?, ?, ?, ?)", 
                       (project_id, action, status, datetime.now()))
        conn.commit()
        conn.close()
