-- =====================================================================
-- Picped - seed.sql  (DADOS DEMONSTRATIVOS - fictícios, não são preços reais)
-- Usuários de demonstração: ana@ / bruno@ / carla@picped.dev  — senha: picped123
-- ATENÇÃO: coordenadas aproximadas/ilustrativas. Ajuste com o Google Maps.
-- =====================================================================

INSERT INTO usuario (nome, email, senha_hash) VALUES
    ('Ana Teste',   'ana@picped.dev',   'pbkdf2_sha256$600000$6fdac514a89d2dda918c89d8be4b11f6$327adf6c5654a6239a1f5d177ed54b653af9f0ae7793d786295fb421890b5564'),
    ('Bruno Teste', 'bruno@picped.dev', 'pbkdf2_sha256$600000$920897d2d3cfec2e78e5c2e3022cfad3$ebb1873c44d79e887b268a9ebfb1cc9c11070b0bee2e08caf60ba60b3c52a592'),
    ('Carla Teste', 'carla@picped.dev', 'pbkdf2_sha256$600000$cb44c98e9233c1499ddeacc1e2ef986e$21878aa4e48a82029cfdcf0b78a2bc85d99c4437dc24028d3e71a618f76da068');

INSERT INTO categoria (nome) VALUES
    ('Grãos e Cereais'), ('Laticínios'), ('Bebidas'), ('Carnes e Ovos'),
    ('Hortifrúti'), ('Higiene e Limpeza'), ('Mercearia');

INSERT INTO produto (nome, marca, unidade_medida, categoria_id) VALUES
    ('Arroz Branco Tipo 1 5kg', 'Tio João',  'un', (SELECT id FROM categoria WHERE nome = 'Grãos e Cereais')),
    ('Feijão Carioca 1kg',      'Camil',     'un', (SELECT id FROM categoria WHERE nome = 'Grãos e Cereais')),
    ('Leite Integral 1L',       'Itambé',    'un', (SELECT id FROM categoria WHERE nome = 'Laticínios')),
    ('Queijo Mussarela',        'Tirolez',   'kg', (SELECT id FROM categoria WHERE nome = 'Laticínios')),
    ('Refrigerante Guaraná 2L', 'Antarctica','un', (SELECT id FROM categoria WHERE nome = 'Bebidas')),
    ('Café Torrado 500g',       'Pilão',     'un', (SELECT id FROM categoria WHERE nome = 'Mercearia')),
    ('Açúcar Refinado 1kg',     'União',     'un', (SELECT id FROM categoria WHERE nome = 'Mercearia')),
    ('Óleo de Soja 900ml',      'Soya',      'un', (SELECT id FROM categoria WHERE nome = 'Mercearia')),
    ('Ovos Brancos 12 un',      'Mantiqueira','un',(SELECT id FROM categoria WHERE nome = 'Carnes e Ovos')),
    ('Frango Inteiro Congelado','Sadia',     'kg', (SELECT id FROM categoria WHERE nome = 'Carnes e Ovos')),
    ('Banana Prata',            NULL,        'kg', (SELECT id FROM categoria WHERE nome = 'Hortifrúti')),
    ('Detergente Líquido 500ml','Ypê',       'un', (SELECT id FROM categoria WHERE nome = 'Higiene e Limpeza'));

INSERT INTO supermercado (nome, cidade, bairro, endereco, latitude, longitude, raio_metros) VALUES
    ('Atacadão',   'Manaus', 'Cidade Nova',  'Endereço de exemplo, Cidade Nova',  -3.030000, -59.990000, 100),
    ('Carvalho',   'Manaus', 'Adrianópolis', 'Endereço de exemplo, Adrianópolis', -3.111500, -60.012800,  80),
    ('DB',         'Manaus', 'Ponta Negra',  'Endereço de exemplo, Ponta Negra',  -3.085000, -60.090000,  80),
    ('Nova Era',   'Manaus', 'Centro',       'Endereço de exemplo, Centro',       -3.133000, -60.023000,  60),
    ('Super Mais', 'Manaus', 'Flores',       'Endereço de exemplo, Flores',       -3.083000, -60.005000,  80);

-- Histórico de preços (dois registros por produto/mercado em datas diferentes)
INSERT INTO preco (produto_id, supermercado_id, usuario_id, valor, coletado_em, distancia_metros)
SELECT p.id, s.id, u.id, v.valor, v.coletado_em::timestamp, v.dist
FROM (VALUES
    ('Arroz Branco Tipo 1 5kg', 'Atacadão',   'ana@picped.dev',   27.90, '2026-10-05 10:15', 12),
    ('Arroz Branco Tipo 1 5kg', 'Atacadão',   'bruno@picped.dev', 28.50, '2026-10-19 18:40', 25),
    ('Arroz Branco Tipo 1 5kg', 'Carvalho',   'carla@picped.dev', 31.49, '2026-10-12 09:20', 30),
    ('Arroz Branco Tipo 1 5kg', 'DB',         'ana@picped.dev',   32.90, '2026-10-14 17:05', 18),
    ('Feijão Carioca 1kg',      'Atacadão',   'bruno@picped.dev',  7.99, '2026-10-05 10:20', 15),
    ('Feijão Carioca 1kg',      'Carvalho',   'carla@picped.dev',  8.79, '2026-10-12 09:25', 22),
    ('Feijão Carioca 1kg',      'Nova Era',   'ana@picped.dev',    8.49, '2026-10-20 11:00', 10),
    ('Leite Integral 1L',       'Atacadão',   'ana@picped.dev',    5.19, '2026-10-05 10:25', 14),
    ('Leite Integral 1L',       'DB',         'bruno@picped.dev',  5.89, '2026-10-14 17:10', 20),
    ('Leite Integral 1L',       'Super Mais', 'carla@picped.dev',  5.49, '2026-10-21 15:30', 35),
    ('Queijo Mussarela',        'Carvalho',   'carla@picped.dev', 49.90, '2026-10-12 09:30', 28),
    ('Queijo Mussarela',        'Nova Era',   'bruno@picped.dev', 52.90, '2026-10-20 11:05', 12),
    ('Refrigerante Guaraná 2L', 'Atacadão',   'ana@picped.dev',    8.49, '2026-10-05 10:30', 16),
    ('Refrigerante Guaraná 2L', 'DB',         'bruno@picped.dev',  9.99, '2026-10-14 17:15', 21),
    ('Café Torrado 500g',       'Carvalho',   'carla@picped.dev', 21.90, '2026-10-12 09:35', 26),
    ('Café Torrado 500g',       'Super Mais', 'ana@picped.dev',   23.50, '2026-10-21 15:35', 33),
    ('Açúcar Refinado 1kg',     'Atacadão',   'bruno@picped.dev',  4.49, '2026-10-05 10:35', 13),
    ('Açúcar Refinado 1kg',     'Nova Era',   'carla@picped.dev',  4.99, '2026-10-20 11:10', 11),
    ('Óleo de Soja 900ml',      'Atacadão',   'ana@picped.dev',    6.99, '2026-10-05 10:40', 17),
    ('Óleo de Soja 900ml',      'DB',         'carla@picped.dev',  7.89, '2026-10-14 17:20', 19),
    ('Ovos Brancos 12 un',      'Carvalho',   'bruno@picped.dev', 12.90, '2026-10-12 09:40', 24),
    ('Ovos Brancos 12 un',      'Super Mais', 'ana@picped.dev',   13.50, '2026-10-21 15:40', 31),
    ('Frango Inteiro Congelado','Atacadão',   'carla@picped.dev', 12.99, '2026-10-05 10:45', 18),
    ('Banana Prata',            'Nova Era',   'bruno@picped.dev',  6.99, '2026-10-20 11:15', 9),
    ('Detergente Líquido 500ml','Atacadão',   'ana@picped.dev',    2.49, '2026-10-05 10:50', 12),
    ('Detergente Líquido 500ml','Super Mais', 'bruno@picped.dev',  2.99, '2026-10-21 15:45', 30)
) AS v (produto, mercado, email, valor, coletado_em, dist)
JOIN produto      p ON p.nome = v.produto
JOIN supermercado s ON s.nome = v.mercado
JOIN usuario      u ON u.email = v.email;

-- Listas de compras de exemplo
INSERT INTO lista_compras (usuario_id, nome) VALUES
    ((SELECT id FROM usuario WHERE email = 'ana@picped.dev'),   'Compras do mês'),
    ((SELECT id FROM usuario WHERE email = 'bruno@picped.dev'), 'Churrasco de domingo');

INSERT INTO item_lista (lista_id, produto_id, quantidade)
SELECT l.id, p.id, v.qtd
FROM (VALUES
    ('Compras do mês',       'Arroz Branco Tipo 1 5kg', 2),
    ('Compras do mês',       'Feijão Carioca 1kg',      3),
    ('Compras do mês',       'Leite Integral 1L',       12),
    ('Compras do mês',       'Café Torrado 500g',       1),
    ('Churrasco de domingo', 'Refrigerante Guaraná 2L', 4),
    ('Churrasco de domingo', 'Frango Inteiro Congelado',3)
) AS v (lista, produto, qtd)
JOIN lista_compras l ON l.nome = v.lista
JOIN produto      p ON p.nome = v.produto;
