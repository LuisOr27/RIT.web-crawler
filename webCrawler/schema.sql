-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS actas;

CREATE TABLE actas (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    downloadLink TEXT,
    UNIQUE(filename, downloadLink)
);
