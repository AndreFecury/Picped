# Picped — aplicativo Android (APS)

> **Compare mais. Pague menos.** App colaborativo para registrar, pesquisar e comparar preços de supermercados.

O app consome a **API Picped** (FastAPI + PostgreSQL) que está na raiz deste repositório — a mesma
apresentada na disciplina de Linguagem de Programação de Banco de Dados.

## Funcionalidades (MVP)

| Tela | O que faz | Endpoints usados |
|---|---|---|
| Splash / Entrar / Criar conta | Login com token, cadastro, servidor configurável | `POST /auth/login`, `GET /auth/me`, `POST /usuarios` |
| Início | Busca, supermercados por distância (GPS), listas recentes, categorias | `GET /supermercados`, `GET /listas`, `GET /categorias` |
| Pesquisar | Nome, marca, categoria e **código de barras pela câmera**; cadastrar produto novo | `GET /produtos?busca=&codigo_barras=&categoria_id=`, `POST /produtos` |
| Produto | Comparação entre lojas (menor preço, data da coleta, distância, aviso de preço antigo), economia e histórico (mín/média/máx/variação + gráfico) | `GET /produtos/{id}/comparacao`, `GET /produtos/{id}/historico` |
| **+ Preço** | GPS identifica o mercado (ou escolhe na lista / cadastra o mercado no local), produto e valor | `GET /supermercados/proximos`, `POST /precos`, `POST /supermercados` |
| Lista | Várias listas, itens e quantidades, marcar comprado, **onde a lista sai mais barata** | `/listas`, `/listas/{id}/itens`, `GET /listas/{id}/comparacao` |
| Perfil | Dados, servidor da API, sair, **excluir conta** (LGPD) | `DELETE /auth/me` |

Todas as telas têm estados de carregando, erro, vazio e sem conexão.

## Arquitetura

```
lib/
  core/      tema (tokens de cor/tipografia), rotas (go_router), formatos pt-BR, geolocalização
  data/      cliente HTTP (Dio + token Bearer), modelos, providers (Riverpod)
  shared/    componentes reutilizáveis (estados, etiquetas, scanner, seletor de produto)
  features/  auth, inicio, busca, produto, preco, listas, perfil
```

- **Flutter 3.50 / Dart 3.14**, Material 3 com a identidade visual do Picped (fonte Inter).
- **Riverpod** (estado), **go_router** (navegação + redirecionamento por sessão), **Dio** (HTTP).
- Token guardado no **flutter_secure_storage** (Keystore do Android). Senha nunca fica no app.
- **geolocator** (GPS) e **mobile_scanner** (EAN/GTIN). As regras de negócio ficam na API.

## Usar só no computador (sem celular)

A API também serve a **versão web do app**: com o `docker compose` rodando, abra
**http://localhost:8000/app/** no navegador do mesmo computador. Ela já aponta para a API local
(não precisa configurar servidor). Para atualizar essa versão depois de mudar o código do app:

```bash
flutter build web --release --base-href /app/ --no-web-resources-cdn
# copiar build/web para ../web_app (sem os arquivos *.symbols e *.map)
```

## Como rodar a apresentação (celular)

1. **API no notebook:** na raiz do repositório, `docker compose up -d --build`
   (banco novo: `docker compose down -v` antes, para carregar schema + seed + demo).
   Se o banco já existia antes desta versão: `docker compose exec -T db psql -U postgres -d picped < scripts/migracoes/001_item_lista_comprado.sql`.
2. Descobrir o IP do notebook: `ipconfig` → "Endereço IPv4" (ex.: `192.168.0.10`).
   Na primeira vez, o Windows pode pedir para liberar a porta 8000 no firewall — permitir em **redes privadas**.
3. **Celular no mesmo Wi-Fi.** Instalar o `app-release.apk` (permitir "instalar apps desconhecidos").
4. No app: **Configurar servidor** → `http://192.168.0.10:8000` → Salvar e testar.
5. Entrar com a conta demo `ana@picped.dev` / `picped123` ou criar uma conta.

> Dica: se o Wi-Fi da faculdade isolar os aparelhos, use o **roteador do celular** (hotspot) com o notebook conectado nele.

## Gerar o APK

```bash
flutter pub get
flutter build apk --release          # build/app/outputs/flutter-apk/app-release.apk
flutter test                         # testes unitários
```

## Dados e limitações (transparência)

- Lojas e preços iniciais são **demonstrativos** (fictícios) e o app avisa isso na tela inicial.
- Não há integração com fonte oficial de preços: o modelo é **colaborativo** (usuários registram).
- Preço com mais de 30 dias aparece como **"pode estar desatualizado"**.
- Economia mostrada é **potencial** e a referência é explicada na tela.
- Ainda não implementado (próximas etapas): recuperação de senha, favoritos, notificações, preço
  promocional/validade, foto de comprovante, moderação/reputação, modo offline, otimização entre
  várias lojas com custo de deslocamento, preço por unidade de medida, iOS.
