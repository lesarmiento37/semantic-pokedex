-- Run once as admin against the existing RDS
CREATE DATABASE semantic_pokedex;
\c semantic_pokedex
CREATE EXTENSION IF NOT EXISTS vector;
CREATE ROLE pokedex_app LOGIN PASSWORD 'CHANGE_ME_VIA_SECRETS_MANAGER';
GRANT CONNECT ON DATABASE semantic_pokedex TO pokedex_app;
GRANT USAGE, CREATE ON SCHEMA public TO pokedex_app;
-- Then run src/pokedex/db/schema.sql as pokedex_app
