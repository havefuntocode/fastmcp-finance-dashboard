"""
umsatz_server_pg.py
FastMCP Server für Quartalsumsätze – stdio Transport
Datenbank: finance_db (PostgreSQL)
Start: wird automatisch von Claude Desktop gestartet
Zugangsdaten: werden von Claude Desktop via claude_desktop_config.json übergeben
"""

from mcp.server.fastmcp import FastMCP
import psycopg2
import psycopg2.extras  # RealDictCursor
import os

# ── Instanz ────────────────────────────────────────────────────
mcp = FastMCP(
    "Umsatz-Server-PG",
    instructions="""
        Dieser Server stellt Quartalsumsätze aus der PostgreSQL-Datenbank 
        finance_db bereit. Verwende get_chart_data um Umsätze abzufragen 
        und als Balkendiagramm darzustellen.
    """
)

# ── DB-Verbindung ──────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "finance_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )

# ── Hilfsfunktion: SQL-Abfrage ─────────────────────────────────
def _query_quartalsumsatz(jahr: int | None = None) -> list[dict]:
    conn   = get_connection()
    # RealDictCursor → liefert Zeilen als dict (wie dictionary=True bei mysql.connector)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if jahr:
        cursor.execute("""
            SELECT
                jahr,
                CEIL(monat / 3.0)::INT  AS quartal,
                SUM(umsatz)             AS umsatz
            FROM monatsumsatz
            WHERE jahr = %s
            GROUP BY jahr, quartal
            ORDER BY quartal
        """, (jahr,))
    else:
        cursor.execute("""
            SELECT
                jahr,
                CEIL(monat / 3.0)::INT  AS quartal,
                SUM(umsatz)             AS umsatz
            FROM monatsumsatz
            GROUP BY jahr, quartal
            ORDER BY jahr, quartal
        """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # NUMERIC → float für JSON-Serialisierung
    return [
        {
            "jahr":    row["jahr"],
            "quartal": row["quartal"],
            "umsatz":  float(row["umsatz"]),
        }
        for row in rows
    ]

# ── Mapping: DB-Rows → Chart.js dataset ───────────────────────
def _build_chart_data(rows: list[dict]) -> dict:
    farben = {
        2024: {"bg": "rgba(59,139,212,0.75)",  "border": "#3B8BD4"},
        2025: {"bg": "rgba(29,158,117,0.75)",  "border": "#1D9E75"},
    }
    fallback = {"bg": "rgba(90,100,120,0.75)", "border": "#5a6478"}

    grouped: dict[int, list[float]] = {}
    for row in rows:
        j = row["jahr"]
        if j not in grouped:
            grouped[j] = [0.0, 0.0, 0.0, 0.0]
        grouped[j][row["quartal"] - 1] = row["umsatz"]

    datasets = [
        {
            "label":           str(j),
            "data":            werte,
            "backgroundColor": farben.get(j, fallback)["bg"],
            "borderColor":     farben.get(j, fallback)["border"],
            "borderWidth":     1,
            "borderRadius":    4,
        }
        for j, werte in sorted(grouped.items())
    ]

    return {
        "labels":   ["Q1", "Q2", "Q3", "Q4"],
        "datasets": datasets,
    }

# ── MCP Tool ───────────────────────────────────────────────────
@mcp.tool()
def get_chart_data(jahr: int | None = None) -> dict:
    """
    Liefert ein fertiges Chart.js-Datenobjekt mit Quartalsumsätzen.
    Parameter:
        jahr: Filtert auf ein bestimmtes Jahr (z.B. 2024).
              Wird None übergeben, kommen alle Jahre.
    """
    rows = _query_quartalsumsatz(jahr)
    return _build_chart_data(rows)

# ── Start ──────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
