# fastmcp-finance-dashboard

Create a little bar-chart dashboard with PostgreSQL and Claude.

Ein MCP-Server (Model Context Protocol), der Claude Desktop ermöglicht, monatliche Umsatzdaten
aus einer PostgreSQL-Datenbank abzufragen, als Quartalssummen zu aggregieren und als interaktives
Balkendiagramm direkt im Claude Client darzustellen.

---

## 1. Projektübersicht

| Layer | Technologie |
|---|---|
| KI-Integration | [FastMCP](https://github.com/jlowin/fastmcp) |
| Datenbank | PostgreSQL |
| Visualisierung | Claude Client (Chart.js) |

---

## 2. Voraussetzungen

- Python 3.11 oder höher
- PostgreSQL 14 oder höher
- Claude Desktop (Windows, macOS)
- Folgende Python-Pakete:

```bash
pip install fastmcp psycopg2-binary
```

---

## 3. Datenbankeinrichtung

### Datenbank erstellen

```sql
CREATE DATABASE finance_db
    WITH
    ENCODING    = 'UTF8'
    LC_COLLATE  = 'de_DE.UTF-8'
    LC_CTYPE    = 'de_DE.UTF-8'
    TEMPLATE    = template0;
```

### Tabelle erstellen

```sql
\c finance_db

CREATE TABLE monatsumsatz (
    id      SERIAL          PRIMARY KEY,
    jahr    SMALLINT        NOT NULL,
    monat   SMALLINT        NOT NULL,  -- 1–12
    umsatz  NUMERIC(12, 2)  NOT NULL,
    CONSTRAINT uk_jahr_monat UNIQUE (jahr, monat)
);
```

### Beispieldaten einfügen

```sql
-- 2024
INSERT INTO monatsumsatz (jahr, monat, umsatz) VALUES
(2024,  1,  45200.00), (2024,  2,  48750.00), (2024,  3,  48550.00),
(2024,  4,  54300.00), (2024,  5,  57800.00), (2024,  6,  56800.00),
(2024,  7,  61200.00), (2024,  8,  67400.00), (2024,  9,  66700.00),
(2024, 10,  72100.00), (2024, 11,  75300.00), (2024, 12,  74300.00);

-- 2025
INSERT INTO monatsumsatz (jahr, monat, umsatz) VALUES
(2025,  1,  50400.00), (2025,  2,  53100.00), (2025,  3,  54700.00),
(2025,  4,  58900.00), (2025,  5,  62300.00), (2025,  6,  60200.00),
(2025,  7,  66800.00), (2025,  8,  72400.00), (2025,  9,  70400.00),
(2025, 10,  78200.00), (2025, 11,  83600.00), (2025, 12,  81300.00);
```

---

## 4. Installation & Setup

```bash
# Repository klonen
git clone https://github.com/havefuntocode/fastmcp-finance-dashboard.git
cd fastmcp-finance-dashboard

# Abhängigkeiten installieren
pip install mcp fastmcp psycopg2-binary
```

---

## 5. Projektstruktur

```
fastmcp-finance-dashboard/
├── umsatz_server_pg.py       # FastMCP Server (stdio)
├── finance_db_postgresql.sql # CREATE TABLE + INSERT Beispieldaten
├── .gitignore
├── LICENSE
└── README.md
```

---

## 6. Claude Desktop Konfiguration

Da der Server über **stdio** läuft, startet Claude Desktop den Server automatisch.
Es wird keine URL benötigt – nur der Pfad zum Python-Skript.

Pfad der Konfigurationsdatei:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

> **Hinweis:** Den Pfad in `args` an deinen tatsächlichen Speicherort anpassen.
> Nach dem Speichern Claude Desktop neu starten – der Server wird automatisch gestartet.

---

## 7. Das MCP-Tool im Überblick

| Tool | Beschreibung | Parameter |
|---|---|---|
| `get_chart_data` | Quartalsumsätze aggregiert als Chart.js-Objekt | `jahr` *(optional)*: z.B. `2024` |

---

## 8. Datenfluss

```
Claude Desktop
        │
        │  get_chart_data(jahr)  ← MCP Tool Aufruf
        ▼
   get_chart_data()
        │
        ▼
   _query_quartalsumsatz()
        │  SELECT jahr, CEIL(monat/3.0)::INT AS quartal, SUM(umsatz)
        ▼
   PostgreSQL finance_db
        │
        ▼
   _build_chart_data()      ← Mapping auf Chart.js-Format
        │
        ▼
   { labels, datasets }     → Chart.js rendert Balkendiagramm
```

---

## 9. Aggregationsabfrage

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

## 10. Startvorgang

Claude Desktop startet den Server automatisch beim Start – kein manueller Start erforderlich.
Das Balkendiagramm wird direkt im Claude Client angezeigt, sobald das MCP-Tool aufgerufen wird.

---

## 11. .gitignore

```
# Sensible Dateien
.env
*.env
claude_desktop_config.json

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Editor
.vscode/
.idea/
```

---

## 12. Lizenz

Dieses Projekt steht unter der [MIT License](https://opensource.org/licenses/MIT).
Du darfst es frei verwenden, anpassen und weitergeben.

---

## 13. Hinweis zur Erstellung

Diese README wurde in Zusammenarbeit mit **Claude (Anthropic)** erstellt. Claude hat mich
bei der Entwicklung dieses Projekts unterstützt — von der Datenbankmodellierung über die
Implementierung des FastMCP-Servers bis hin zur Chart.js-Visualisierung und Dokumentation.
Die Zusammenarbeit mit Claude ist auch Thema meiner
[LinkedIn-Erfahrungsberichte](https://www.linkedin.com/in/michael-laube-602562127/).
