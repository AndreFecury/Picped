-- =====================================================================
-- Picped - demo.sql  (DADOS DEMONSTRATIVOS extras para a apresentação do app)
-- Preços fictícios mais recentes, para que a lista "Compras do mês" tenha
-- supermercados com todos os itens. Rodado pelo docker compose após o seed.
-- Fica separado do seed.sql para não alterar os dados usados nos testes.
-- =====================================================================
INSERT INTO preco (produto_id, supermercado_id, usuario_id, valor, coletado_em, distancia_metros)
SELECT p.id, s.id, u.id, v.valor, v.coletado_em::timestamp, v.dist
FROM (VALUES
    ('Café Torrado 500g',       'Atacadão', 'bruno@picped.dev', 20.90, '2026-11-08 09:10', 14),
    ('Leite Integral 1L',       'Carvalho', 'ana@picped.dev',    5.69, '2026-11-06 18:20', 21),
    ('Arroz Branco Tipo 1 5kg', 'Carvalho', 'carla@picped.dev', 30.99, '2026-11-06 18:25', 19),
    ('Feijão Carioca 1kg',      'Atacadão', 'ana@picped.dev',    7.79, '2026-11-08 09:15', 11),
    ('Leite Integral 1L',       'Atacadão', 'carla@picped.dev',  4.99, '2026-11-08 09:20', 16)
) AS v (produto, mercado, email, valor, coletado_em, dist)
JOIN produto      p ON p.nome = v.produto
JOIN supermercado s ON s.nome = v.mercado
JOIN usuario      u ON u.email = v.email;
