/* Datenbank finance_db erstellen*/
CREATE DATABASE finance_db
    ENCODING    'UTF8'
    LC_COLLATE  'de_DE.UTF-8'
    LC_CTYPE    'de_DE.UTF-8'
    TEMPLATE    template0;

/* Tabelle monatsumsatz erstellen */
CREATE TABLE monatsumsatz (
    id      SERIAL          PRIMARY KEY,
    jahr    SMALLINT        NOT NULL,
    monat   SMALLINT        NOT NULL,  -- 1–12
    umsatz  NUMERIC(12, 2)  NOT NULL,
    CONSTRAINT uk_jahr_monat UNIQUE (jahr, monat)
);

/* 2024 */
INSERT INTO monatsumsatz (jahr, monat, umsatz) VALUES
(2024,  1,  45200.00),
(2024,  2,  48750.00),
(2024,  3,  48550.00),  -- Q1: 142.500
(2024,  4,  54300.00),
(2024,  5,  57800.00),
(2024,  6,  56800.00),  -- Q2: 168.900
(2024,  7,  61200.00),
(2024,  8,  67400.00),
(2024,  9,  66700.00),  -- Q3: 195.300
(2024, 10,  72100.00),
(2024, 11,  75300.00),
(2024, 12,  74300.00);  -- Q4: 221.700

/* 2025 */
INSERT INTO monatsumsatz (jahr, monat, umsatz) VALUES
(2025,  1,  50400.00),
(2025,  2,  53100.00),
(2025,  3,  54700.00),  -- Q1: 158.200
(2025,  4,  58900.00),
(2025,  5,  62300.00),
(2025,  6,  60200.00),  -- Q2: 181.400
(2025,  7,  66800.00),
(2025,  8,  72400.00),
(2025,  9,  70400.00),  -- Q3: 209.600
(2025, 10,  78200.00),
(2025, 11,  83600.00),
(2025, 12,  81300.00);  -- Q4: 243.100

-- 6. Kontrolle
SELECT
    jahr,
    CEIL(monat / 3.0)::INT  AS quartal,
    SUM(umsatz)             AS quartalsumsatz
FROM monatsumsatz
GROUP BY jahr, quartal
ORDER BY jahr, quartal;
