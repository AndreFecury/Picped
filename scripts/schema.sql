-- =====================================================================
-- Picped - Plataforma inteligente de comparação de preços e economia domésticos
-- schema.sql  (PostgreSQL 16)  -  DDL + índices + função de geolocalização
-- =====================================================================

DROP TABLE IF EXISTS item_lista     CASCADE;
DROP TABLE IF EXISTS lista_compras  CASCADE;
DROP TABLE IF EXISTS preco          CASCADE;
DROP TABLE IF EXISTS produto        CASCADE;
DROP TABLE IF EXISTS categoria      CASCADE;
DROP TABLE IF EXISTS supermercado   CASCADE;
DROP TABLE IF EXISTS usuario        CASCADE;

-- ---------------------------------------------------------------------
-- usuario
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id          SERIAL        PRIMARY KEY,
    nome        VARCHAR(100)  NOT NULL,
    email       VARCHAR(150)  NOT NULL UNIQUE,
    senha_hash  VARCHAR(255)  NOT NULL,
    criado_em   TIMESTAMP     NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_usuario_email CHECK (POSITION('@' IN email) > 1)
);

-- ---------------------------------------------------------------------
-- categoria
-- ---------------------------------------------------------------------
CREATE TABLE categoria (
    id    SERIAL       PRIMARY KEY,
    nome  VARCHAR(60)  NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- produto
-- ---------------------------------------------------------------------
CREATE TABLE produto (
    id              SERIAL        PRIMARY KEY,
    nome            VARCHAR(120)  NOT NULL,
    marca           VARCHAR(60),
    unidade_medida  VARCHAR(10)   NOT NULL,
    codigo_barras   VARCHAR(14)   UNIQUE,              -- EAN-8/13/14 (opcional)
    categoria_id    INTEGER       NOT NULL REFERENCES categoria (id),
    CONSTRAINT ck_produto_unidade CHECK (unidade_medida IN ('un','kg','g','l','ml')),
    CONSTRAINT ck_produto_ean     CHECK (codigo_barras IS NULL OR codigo_barras ~ '^[0-9]{8,14}$'),
    CONSTRAINT uq_produto_nome_marca UNIQUE (nome, marca)
);

-- ---------------------------------------------------------------------
-- supermercado  (latitude/longitude + raio permitem identificar o mercado
--                a partir da localização do celular do usuário)
-- ---------------------------------------------------------------------
CREATE TABLE supermercado (
    id           SERIAL         PRIMARY KEY,
    nome         VARCHAR(100)   NOT NULL,
    cidade       VARCHAR(80)    NOT NULL,
    bairro       VARCHAR(80)    NOT NULL,
    endereco     VARCHAR(200),
    latitude     NUMERIC(9,6)   NOT NULL,
    longitude    NUMERIC(9,6)   NOT NULL,
    raio_metros  INTEGER        NOT NULL DEFAULT 80,   -- tolerância do GPS
    ativo        BOOLEAN        NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_super_lat   CHECK (latitude  BETWEEN -90  AND 90),
    CONSTRAINT ck_super_lon   CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT ck_super_raio  CHECK (raio_metros > 0),
    CONSTRAINT uq_super_nome_bairro UNIQUE (nome, cidade, bairro)
);

-- ---------------------------------------------------------------------
-- preco  (histórico: N:N entre produto e supermercado, com data e autor)
-- ---------------------------------------------------------------------
CREATE TABLE preco (
    id                 SERIAL         PRIMARY KEY,
    produto_id         INTEGER        NOT NULL REFERENCES produto (id),
    supermercado_id    INTEGER        NOT NULL REFERENCES supermercado (id),
    usuario_id         INTEGER        NOT NULL REFERENCES usuario (id),
    valor              NUMERIC(10,2)  NOT NULL,
    coletado_em        TIMESTAMP      NOT NULL DEFAULT NOW(),
    distancia_metros   INTEGER,                         -- distância do usuário ao mercado no momento do registro
    CONSTRAINT ck_preco_valor     CHECK (valor > 0),
    CONSTRAINT ck_preco_distancia CHECK (distancia_metros IS NULL OR distancia_metros >= 0)
);

-- ---------------------------------------------------------------------
-- lista_compras
-- ---------------------------------------------------------------------
CREATE TABLE lista_compras (
    id          SERIAL        PRIMARY KEY,
    usuario_id  INTEGER       NOT NULL REFERENCES usuario (id) ON DELETE CASCADE,
    nome        VARCHAR(100)  NOT NULL,
    criada_em   TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- item_lista
-- ---------------------------------------------------------------------
CREATE TABLE item_lista (
    id          SERIAL         PRIMARY KEY,
    lista_id    INTEGER        NOT NULL REFERENCES lista_compras (id) ON DELETE CASCADE,
    produto_id  INTEGER        NOT NULL REFERENCES produto (id),
    quantidade  NUMERIC(8,3)   NOT NULL DEFAULT 1,
    comprado    BOOLEAN        NOT NULL DEFAULT FALSE,
    CONSTRAINT ck_item_quantidade CHECK (quantidade > 0),
    CONSTRAINT uq_item_lista_produto UNIQUE (lista_id, produto_id)
);

-- ---------------------------------------------------------------------
-- Índices
-- ---------------------------------------------------------------------
CREATE INDEX idx_preco_produto_super_data ON preco (produto_id, supermercado_id, coletado_em DESC);
CREATE INDEX idx_preco_supermercado       ON preco (supermercado_id);
CREATE INDEX idx_preco_usuario            ON preco (usuario_id);
CREATE INDEX idx_produto_categoria        ON produto (categoria_id);
CREATE INDEX idx_produto_nome             ON produto (LOWER(nome));
CREATE INDEX idx_supermercado_coord       ON supermercado (latitude, longitude);
CREATE INDEX idx_lista_usuario            ON lista_compras (usuario_id);

-- ---------------------------------------------------------------------
-- Função: supermercados cujo raio contém a posição informada (Haversine),
-- do mais próximo para o mais distante. Se retornar mais de uma linha,
-- o app pede ao usuário que confirme qual é o mercado.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION supermercados_proximos(p_lat DOUBLE PRECISION, p_lon DOUBLE PRECISION)
RETURNS TABLE (id INTEGER, nome VARCHAR, distancia_metros INTEGER)
LANGUAGE sql STABLE AS $$
    SELECT id, nome, distancia_metros
    FROM (
        SELECT s.id,
               s.nome,
               s.raio_metros,
               ROUND(6371000 * 2 * ASIN(SQRT(
                   POWER(SIN(RADIANS(s.latitude::double precision - p_lat) / 2), 2) +
                   COS(RADIANS(p_lat)) * COS(RADIANS(s.latitude::double precision)) *
                   POWER(SIN(RADIANS(s.longitude::double precision - p_lon) / 2), 2)
               )))::INTEGER AS distancia_metros
        FROM supermercado s
        WHERE s.ativo
    ) d
    WHERE d.distancia_metros <= d.raio_metros
    ORDER BY d.distancia_metros
    LIMIT 3;
$$;
