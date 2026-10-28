import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..config import settings
from ..engine.models import QueryResponse

DB_PATH = settings.BASE_DIR / "osint_history.db"

class HistoryStorage:
    def __init__(self):
        self._enabled = settings.ENABLE_HISTORY

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def _init_db(self):
        if not self._enabled:
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id TEXT PRIMARY KEY,
                category TEXT,
                target_masked TEXT,
                timestamp TEXT,
                duration_seconds REAL,
                summary_json TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save(self, response: QueryResponse):
        """Salva a consulta SOMENTE se o histórico tiver sido explicitamente ativado pelo usuário."""
        if not self._enabled:
            return

        self._init_db()
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO query_history (id, category, target_masked, timestamp, duration_seconds, summary_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                response.query_id,
                response.category,
                response.target_masked,  # NUNCA grava target_raw
                response.started_at,
                response.duration_seconds,
                json.dumps(response.summary.model_dump())
            ))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self._enabled or not DB_PATH.exists():
            return []

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT id, category, target_masked, timestamp, duration_seconds, summary_json
                FROM query_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cur.fetchall()
            conn.close()

            history = []
            for r in rows:
                history.append({
                    "id": r[0],
                    "category": r[1],
                    "target_masked": r[2],
                    "timestamp": r[3],
                    "duration_seconds": r[4],
                    "summary": json.loads(r[5]) if r[5] else {},
                })
            return history
        except Exception:
            return []

    def clear(self):
        if DB_PATH.exists():
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM query_history")
                conn.commit()
                conn.close()
            except Exception:
                pass

history_storage = HistoryStorage()

