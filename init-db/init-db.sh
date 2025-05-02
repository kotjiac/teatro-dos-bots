#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE DATABASE n8n;
  CREATE TABLE IF NOT EXISTS agents (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name TEXT NOT NULL,
      instruction TEXT NOT NULL,
      temperature REAL DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
      top_p REAL DEFAULT 1.0 CHECK (top_p >= 0 AND top_p <= 1),
      presence_penalty REAL DEFAULT 0.0 CHECK (presence_penalty >= -2 AND presence_penalty <= 2),
      frequency_penalty REAL DEFAULT 0.0 CHECK (frequency_penalty >= -2 AND frequency_penalty <= 2),
      created_at TIMESTAMPTZ DEFAULT NOW()
  );
EOSQL
