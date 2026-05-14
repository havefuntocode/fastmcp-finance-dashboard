# fastmcp-finance-dashboard

Create a little bar-chart dashboard with PostgreSQL and Claude.

This project connects a local PostgreSQL database to Claude Desktop via a FastMCP server, aggregates monthly revenue data into quarterly totals, and visualizes the result as an interactive Chart.js bar chart in the browser.

---

## Stack

| Layer | Technologie |
|---|---|
| KI-Integration | [FastMCP](https://github.com/jlowin/fastmcp) |
| REST-Endpunkt | [FastAPI](https://fastapi.tiangolo.com/) |
| Datenbank | PostgreSQL |
| Visualisierung | [Chart.js](https://www.chartjs.org/) |
| Frontend | HTML + Vanilla JS |

---

## Projektstruktur

```
fastmcp-finance-dashboard/
├── umsatz_server_pg.py      # FastMCP + FastAPI Server
├── finance_db_postgresql.sql # CREATE TABLE + INSERT Beispieldaten
├── finance_dashboard.html   # Chart.js Dashboard
├── .env.example             # Umgebungsvariablen (Vorlage)
├── .gitignore
├── LICENSE
└── README.md
```

---

## Voraussetzungen

- Python 3.11+
- PostgreSQL (lokal installiert)
- Claude Desktop

---

## Installation

```bash
# 1. Repository klonen
git clone https://github.com/dein-username/fastmcp-finance-dashboard.git
cd fastmcp-finance-dashboard

# 2. Abhängigkeiten installieren
pip install fastapi uvicorn fastmcp psycopg2-binary python-dotenv

# 3. Umgebungsvariablen anlegen
cp .env.example .env
# .env mit deinen PostgreSQL-Zugangsdaten befüllen
```

---

## Datenbank einrichten

SQL-Skript in pgAdmin oder psql ausführen:

```bash
psql -U postgres -f finance_db_postgresql.sql
```

Das Skript legt die Datenbank `finance_db`, die Tabelle `monatsumsatz` und Beispieldaten für 2024 und 2025 an.

---

## Server starten

```bash
python umsatz_server_pg.py
```

Der Server läuft auf `http://localhost:8000`.

| Endpunkt | Beschreibung |
|---|---|
| `POST /query` | Liefert Chart.js-Datenobjekt (Brücke zum Browser) |
| `GET /health` | Health-Check |
| `/mcp` | MCP SSE Endpunkt für Claude Desktop |

---

## Dashboard aufrufen

`finance_dashboard.html` im Browser öffnen – der `fetch()`-Call geht automatisch auf `http://localhost:8000/query`.

```bash
# Optional: kleiner HTTP-Server
python -m http.server 3000
# → http://localhost:3000/finance_dashboard.html
```

---

## Claude Desktop konfigurieren

In `claude_desktop_config.json` eintragen:

```json
{
  "mcpServers": {
    "umsatz-server": {
      "command": "python",
      "args": ["C:/Pfad/zum/umsatz_server_pg.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "finance_db",
        "DB_USER": "postgres",
        "DB_PASSWORD": "dein_passwort"
      }
    }
  }
}
```

---

## Datenfluss

```
Claude Desktop / Browser
        │
        │  POST /query { tool: "get_chart_data", jahr: 2024 }
        ▼
   FastAPI /query
        │
        ▼
   get_chart_data()   ← MCP Tool
        │
        ▼
   _query_quartalsumsatz()
        │  SELECT jahr, CEIL(monat/3.0)::INT AS quartal, SUM(umsatz)
        ▼
   PostgreSQL finance_db
        │
        ▼
   _build_chart_data()   ← Mapping auf Chart.js-Format
        │
        ▼
   { labels, datasets }  → Chart.js rendert Balkendiagramm
```

---

## Aggregationsabfrage

```sql
SELECT
    jahr,
    CEIL(monat / 3.0)::INT  AS quartal,
    SUM(umsatz)             AS quartalsumsatz
FROM monatsumsatz
GROUP BY jahr, quartal
ORDER BY jahr, quartal;
```

---

## Lizenz

MIT
