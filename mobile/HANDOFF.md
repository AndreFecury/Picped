# HANDOFF — App Picped (mobile/)

> Documento de passagem para continuar o desenvolvimento em outra máquina/sessão.
> App da **APS** (apresentação em **14/11/2026**). Plano completo: [`PLANO.md`](PLANO.md).
> Nome correto do app: **Picped** (o plano usa "PICPAD").

---

## 1. Tecnologia e versões

| Item | Versão usada no build |
|---|---|
| Flutter | **3.50.0** (canal stable) |
| Dart | **3.14.0** (`environment: sdk: ^3.14.0` no `pubspec.yaml`) |
| Android Gradle Plugin | **9.3.1** (`android/settings.gradle.kts`) |
| Kotlin (Gradle plugin) | **2.4.20** |
| Gradle (wrapper) | **9.5.0** (`android/gradle/wrapper/gradle-wrapper.properties`) |
| JDK | **21** (OpenJDK 21.0.12); o projeto compila com `sourceCompatibility`/`jvmTarget` **17** |
| Android SDK | `compileSdk` **36**, `targetSdk` **36**, `minSdk` **24** (Android 7.0) — padrões do Flutter 3.50 |
| NDK | 28.2.13676358 (baixado automaticamente pelo Gradle) |
| Build tools | 35.0.0 |
| Pacote Android | `br.unip.psicode.picped` · versão `1.0.0+1` |

Dependências principais (`pubspec.lock`):

| Pacote | Versão | Uso |
|---|---|---|
| flutter_riverpod | 3.5.0 | estado / injeção (providers) |
| go_router | 18.1.4 | navegação + redirecionamento por sessão |
| dio | 5.11.1 | HTTP |
| flutter_secure_storage | 11.2.0 | token no Keystore do Android |
| shared_preferences | 2.5.6 | URL da API configurada |
| geolocator | 14.1.2 | GPS |
| mobile_scanner | 7.5.0 | leitura de EAN/GTIN pela câmera |
| intl | 0.20.3 | moeda R$, datas pt-BR |
| flutter_localizations | SDK | textos do Material em pt-BR |

Observação: o Flutter 3.47+ marcou `package:flutter/material.dart` como *deprecated* em favor do
pacote `material_ui`. O app continua usando `flutter/material.dart` (os pacotes como go_router ainda
usam) e o aviso está silenciado em `analysis_options.yaml` (`deprecated_member_use: ignore`).

Fonte **Inter** (400/500/600/700) embutida em `assets/fonts/` (licença SIL OFL).

---

## 2. Status em relação ao plano (`PLANO.md`)

### Pronto (implementado e testado)

- **Identidade visual** (seção 1): tokens de cor do plano, Inter, Material 3, ícone do app ("P" + ponto verde), splash verde-escuro — `lib/core/theme.dart`, `lib/shared/widgets.dart`.
- **Navegação inferior** Início | Pesquisar | **+ Preço** (ação central) | Lista | Perfil — `lib/core/shell.dart`, `lib/core/router.dart`.
- **Splash, login, cadastro, sair, excluir conta (LGPD)** — `features/auth`, `features/perfil`.
- **Início**: busca, aviso de dados demonstrativos, atalhos, supermercados ordenados por distância (GPS), listas recentes, categorias.
- **Pesquisar**: nome/marca (com debounce), filtro por categoria, **código de barras pela câmera**; produto não encontrado → **cadastrar produto**.
- **Produto + comparação**: lojas do menor para o maior preço, selo "Menor preço", data da coleta, distância, aviso **"pode estar desatualizado"** (> 30 dias), card de economia com a referência do cálculo.
- **Histórico**: mínimo, média, máximo, variação % e gráfico — só com registros existentes.
- **Adicionar preço**: GPS identifica o mercado (`/supermercados/proximos`), escolha manual da lista, **cadastrar supermercado no local atual**, produto por busca ou câmera, valor com vírgula.
- **Listas**: várias listas, criar/renomear/excluir, adicionar item, quantidade (+/−, fracionado para kg/l), marcar comprado, progresso, **onde a lista sai mais barata** (total por mercado, parciais, economia potencial e "como calculamos").
- **Perfil**: dados, configurar servidor da API, sobre, sair, excluir conta.
- **Estados** de carregando / erro / vazio / sem conexão em todas as telas.
- **Testes**: `test/formatos_test.dart` (6 testes unitários: entrada de valor, moeda, distância, preço desatualizado, Haversine).
- **Build**: APK release gerado (73 MB, arm64-v8a + armeabi-v7a + x86_64). Versão web gerada (servida pela API em `/app/` na branch `feat/app`).

### Pela metade / simplificado

- **Comparação por unidade**: não há preço por kg/litro — o produto só tem `unidade_medida`, não o tamanho da embalagem (precisa de campo novo na API).
- **Otimização de compra**: só "comprar tudo em uma loja"; não há divisão entre lojas nem custo de deslocamento.
- **Distância**: calculada no app (Haversine) a partir das coordenadas dos mercados; sem rota real.
- **Busca**: sem sugestões, ordenação configurável nem histórico de buscas.
- **Testes**: só unitários; faltam testes de widget/integração/navegação.

### Falta (fica como "próximas etapas")

Recuperação de senha, favoritos, notificações, ofertas/populares na Início, preço promocional e
validade, foto de comprovante, confirmação/contestação, moderação e reputação, modo offline com
sincronização, exportação de dados, política de privacidade, rede vs. loja física separadas, iOS.

---

## 3. Como rodar e gerar o APK

Pré-requisitos: Flutter 3.50 (`flutter doctor` sem erros na parte Android), Android SDK 36, JDK 17 ou 21.

```bash
cd mobile
flutter pub get
flutter analyze                 # deve dar "No issues found!"
flutter test                    # 6 testes

# rodar num emulador/celular conectado
flutter run

# APK de release (assinado com a chave de DEBUG — serve para instalar/apresentar, não para a Play Store)
flutter build apk --release
#   -> build/app/outputs/flutter-apk/app-release.apk

# APKs menores, um por arquitetura (celulares modernos usam o arm64-v8a)
flutter build apk --release --split-per-abi
#   -> build/app/outputs/flutter-apk/app-arm64-v8a-release.apk

# versão web (opcional; a API serve em /app/)
flutter build web --release --base-href /app/ --no-web-resources-cdn
```

Na primeira compilação o Gradle baixa muita coisa (AGP, Kotlin, NDK, CMake); leva vários minutos.
Se o Maven Central responder **429 Too Many Requests**, basta rodar o build de novo.

**Assinatura:** não existe keystore de release no projeto. `android/app/build.gradle.kts` assina o
release com a chave de debug (padrão do Flutter). Nenhuma chave/senha está versionada.

---

## 4. Conexão com a API

### URL base

- Arquivo: **`lib/data/api.dart`**
- Padrão: getter **`urlPadrao`** → no Android `http://10.0.2.2:8000` (o "localhost" do PC visto pelo **emulador**); na versão web, o mesmo endereço da página.
- Em tempo de execução: tela **Configurar servidor** (login, splash e Perfil) grava a URL em `SharedPreferences` (chave `api_url`) — provider `urlApiProvider`. No celular real use o IP do PC: `http://192.168.x.x:8000`.
- `AndroidManifest.xml` tem `android:usesCleartextTraffic="true"` (API local em HTTP) e permissões INTERNET, localização e câmera.

### Autenticação

`POST /auth/login` devolve `access_token`; o app guarda no `flutter_secure_storage` e envia
`Authorization: Bearer <token>` em todas as chamadas (interceptor do Dio em `PicpedApi`).
401 na abertura → token apagado e volta ao login.

### Erros

A API responde sempre `{"erro": {"codigo", "mensagem", "detalhes": [{campo, mensagem}]}}`.
O app converte em `ApiException(mensagem, status, semConexao)`; sem resposta = "Sem conexão".

### Endpoints usados (e o que o app espera)

| Método e rota | Envia | Espera (campos usados) |
|---|---|---|
| `GET /health` | — | `{"status":"ok"}` (testar servidor) |
| `POST /auth/login` | `{email, senha}` | `{access_token, token_type, expira_em, usuario:{id,nome,email,criado_em}}` |
| `GET /auth/me` | token | `{id, nome, email, criado_em}` |
| `DELETE /auth/me` | token | 204 (apaga conta, listas e preços do usuário) |
| `POST /usuarios` | `{nome, email, senha}` (senha ≥ 8) | 201 + usuário; 409 se e-mail já existe |
| `GET /categorias?limit=200` | — | `[{id, nome}]` |
| `GET /produtos?busca=&codigo_barras=&categoria_id=&limit=100` | `busca` ≥ 2 letras; EAN 8–14 dígitos | `[{id, nome, marca, unidade_medida, codigo_barras, categoria_id}]` |
| `GET /produtos/{id}` | — | produto (acima) |
| `POST /produtos` | `{nome, marca?, unidade_medida ∈ un/kg/g/l/ml, codigo_barras?, categoria_id}` | 201 + produto; 409 duplicado |
| `GET /produtos/{id}/comparacao` | — | `{produto_id, produto_nome, menor_preco, maior_preco, economia, economia_percentual, ofertas:[{supermercado_id, supermercado_nome, valor, coletado_em}]}` (ofertas do mais barato ao mais caro) |
| `GET /produtos/{id}/historico` | — | `{registros, minimo, maximo, media, variacao_percentual, pontos:[{valor, coletado_em, supermercado_id, supermercado_nome}]}` |
| `GET /supermercados?limit=200` | — | `[{id, nome, cidade, bairro, endereco, latitude, longitude, raio_metros, ativo}]` |
| `GET /supermercados/proximos?latitude=&longitude=` | — | `[{id, nome, distancia_metros}]` (mercados cujo raio contém o ponto) |
| `POST /supermercados` | `{nome, cidade, bairro, latitude, longitude, raio_metros}` | 201 + supermercado |
| `POST /precos` | `{produto_id, supermercado_id, usuario_id, valor:"27.90", distancia_metros?}` | 201; 422 regra de negócio (fora do raio, mercado inativo); 403 se `usuario_id` ≠ usuário do token |
| `GET /listas` | token | `[{id, nome, criada_em, total_itens}]` |
| `POST /listas` | `{nome}` | 201 `{id, nome, criada_em, itens:[]}` |
| `GET /listas/{id}` | token | `{id, nome, criada_em, itens:[{id, lista_id, produto_id, quantidade, comprado, produto_nome, produto_marca, unidade_medida}]}`; 403 lista de outro usuário |
| `PATCH /listas/{id}` | `{nome}` | 200 |
| `DELETE /listas/{id}` | — | 204 |
| `POST /listas/{id}/itens` | `{produto_id, quantidade}` | 201; 409 produto já na lista |
| `PATCH /listas/{id}/itens/{item}` | `{quantidade?}` e/ou `{comprado?}` | 200 |
| `DELETE /listas/{id}/itens/{item}` | — | 204 |
| `GET /listas/{id}/comparacao` | token | `{total_itens, referencia, melhor_opcao, economia, economia_percentual, supermercados:[{supermercado_id, supermercado_nome, total, itens_encontrados, itens_faltando, completo}]}` |

**Importante — qual API usar:** as rotas `/auth/*`, `/listas/*`, `/produtos?busca=`, `/produtos/{id}/historico`
e a coluna `item_lista.comprado` **não existem na `main`** (etapas 1–4). Elas estão na branch
**`feat/app`** do mesmo repositório (commit `1006ae8`), que também tem `scripts/demo.sql`,
`subir-picped.bat` e a versão web do app em `/app/`. Para apresentar o app, suba a API a partir
da `feat/app`:

```powershell
git checkout feat/app
.\subir-picped.bat        # recria banco (schema + seed + demo), sobe API, libera porta 8000, mostra o IP
```

Conta demo do seed: `ana@picped.dev` / `picped123` (dados demonstrativos, avisados no app).

---

## 5. Erros e pendências conhecidos

1. **APK não foi testado em celular real** — só build + `flutter analyze` + testes unitários + fluxo completo na versão web (login, busca, comparação, registrar preço pelo GPS, listas, perfil). Câmera e GPS nativos precisam ser conferidos no aparelho.
2. **Rede na apresentação:** o celular precisa alcançar o PC da API (mesmo Wi-Fi, porta 8000 liberada). Wi-Fi de faculdade costuma isolar aparelhos → usar o roteador do celular. VPN no celular/navegador quebra o acesso (no Opera GX de um notebook apareceu "HTTP ERROR 400" com o IP local; não foi investigado a fundo — no próprio notebook `http://localhost:8000/app/` funcionou).
3. **Sem mercado perto na faculdade:** os mercados do seed são fictícios em outros bairros; na demonstração use "Cadastrar um supermercado neste local".
4. **Divergência de branches da API:** a versão da etapa 4 do André (etapas 4–7, testes e CI, ainda sem push na época) e a `feat/app` alteram os mesmos arquivos da API. Precisa de merge cuidadoso depois.
5. **APK grande (73 MB)** por ser universal + ML Kit do scanner; usar `--split-per-abi` se for compartilhar.
6. **Release assinado com chave de debug** — ok para apresentação; para publicar seria preciso criar keystore (não versionar).
7. A busca de produto exige ≥ 2 letras (validação da API devolve 422 para 1 letra; o app só busca a partir de 2).

---

## 6. Estrutura

```
mobile/
  lib/
    main.dart                 ProviderScope, MaterialApp.router, pt-BR, layout de celular na web
    core/  theme.dart  router.dart  shell.dart  formatos.dart  geo.dart
    data/  api.dart (Dio, URL, token, endpoints)  modelos.dart  providers.dart (Riverpod)
    shared/ widgets.dart  produto_widgets.dart  scanner.dart  servidor_dialogo.dart
    features/ auth/  inicio/  busca/  produto/  preco/  listas/  perfil/
  test/formatos_test.dart
  assets/fonts/Inter-*.ttf
  android/   (ícones em res/mipmap-*, manifest com permissões)
  web/       (index.html, manifest e ícones da versão web)
  README.md  HANDOFF.md  PLANO.md
```
