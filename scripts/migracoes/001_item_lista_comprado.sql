-- Migração 001 (app Picped): marca itens da lista como comprados.
-- Só é necessária em bancos criados ANTES desta versão (o schema.sql já inclui a coluna).
--   docker compose exec -T db psql -U postgres -d picped < scripts/migracoes/001_item_lista_comprado.sql
ALTER TABLE item_lista ADD COLUMN IF NOT EXISTS comprado BOOLEAN NOT NULL DEFAULT FALSE;
