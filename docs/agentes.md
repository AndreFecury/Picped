# Trabalhando com mais de um agente

Quatro jeitos de usar vários agentes neste projeto, do mais simples ao mais automático.

## 1. Subagentes dentro de uma sessão

No Claude Code, peça em linguagem natural: *"use subagentes para revisar o backend e o app ao mesmo tempo"*.
Cada subagente trabalha num contexto separado e devolve só o resultado. Bom para pesquisa e revisão;
para edição, cada um deve cuidar de arquivos diferentes.

## 2. Sessões em paralelo com git worktree

Cada sessão do Claude Code numa pasta própria, cada pasta numa branch própria, sem uma pisar na outra:

```powershell
cd C:\Users\Fecur\Programas\picped
git worktree add ..\picped-app  -b feat/app-ajustes  github/main
git worktree add ..\picped-api  -b feat/api-ajustes  github/main
# terminal 1
cd ..\picped-app; claude
# terminal 2
cd ..\picped-api; claude
```

Quando cada um terminar: `git push`, abra um PR por branch e o CI testa tudo antes do merge.
Para remover depois: `git worktree remove ..\picped-app`.

## 3. Claude Code no GitHub (`@claude`)

Dentro do Claude Code, no repositório: `/install-github-app`. Depois é só comentar `@claude` numa
issue ou num PR, por exemplo na issue `falha-producao` que o pipeline abre: *"@claude investigue e
abra um PR com a correção e um teste de regressão"*. Usa a assinatura (token de `claude setup-token`)
ou uma chave de API.

## 4. Divisão de papéis sugerida

| Agente | Cuida de | Não mexe em |
|---|---|---|
| API | `app/`, `tests/`, `scripts/` | `mobile/` |
| App | `mobile/` | `app/` |
| Infra | `Dockerfile`, `render.yaml`, `.github/` | código de negócio |

Regra de ouro: um agente por pasta, uma branch por agente, e o CI decide o que entra na `main`.
