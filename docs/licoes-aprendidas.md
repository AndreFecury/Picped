# Lições aprendidas

Cada falha detectada pelo pipeline (issue `falha-producao`) termina com uma entrada aqui e um teste
de regressão. Formato: o que quebrou, por quê, como corrigimos e qual teste impede que volte.

| Data | O que quebrou | Causa | Correção | Teste que protege |
|---|---|---|---|---|
| 2026-11 | Container não respondia no Render | O Render define a porta em `$PORT`; a imagem fixava 8000 | `CMD` usa `${PORT:-8000}` | `aguardar-deploy` (espera o `/health`) |
| 2026-11 | Banco novo sem tabelas no primeiro deploy | O Neon começa vazio e o `docker-entrypoint-initdb.d` só existe no Compose | `python -m app.init_db` antes do uvicorn, sem apagar dados existentes | E2E `test_saude_e_banco` |
| 2026-11 | App "sem conexão" na primeira abertura | O Render grátis leva ~1 min para acordar; o app desistia em 8 s | Timeouts do app em 75 s e workflow *Manter acordado* | E2E com espera de até 90 s |
