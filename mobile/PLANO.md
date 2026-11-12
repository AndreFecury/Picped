> Plano de desenvolvimento original escrito pelo San (arquivo "PICPAD_Prompt_Mestre.md"), colado na íntegra.
> O nome correto do app é **Picped** ("PICPAD" abaixo se refere ao mesmo app).

# PICPAD --- Especificação e Prompt Mestre de Desenvolvimento

## Objetivo

Desenvolva o **PICPAD**, aplicativo brasileiro para registrar, pesquisar
e comparar preços de supermercados e organizar compras com economia
mensurável.

**Slogan:** Compare mais. Pague menos.\
**Plataforma inicial:** Android. **Expansão:** iOS e outras
categorias/estabelecimentos.\
**Princípio:** entregar produto funcional, integrado, seguro, testado e
documentado --- não apenas protótipo visual.

Atue como equipe sênior de Produto, UX/UI, Flutter, Backend, Banco de
Dados, Segurança e QA. Analise primeiro o repositório existente.
Preserve tecnologias e decisões válidas; não reescreva sem
justificativa. Se começar do zero, siga a arquitetura sugerida abaixo.

## 1. Produto e experiência

O PICPAD deve responder: 1. Onde encontro este produto pelo menor preço?
2. Qual supermercado oferece a melhor opção? 3. Quanto posso economizar
organizando minha compra?

Experiência simples, rápida e acessível a qualquer consumidor. Comece
por supermercados, mas modele o domínio para futura expansão a
farmácias, eletrônicos, lojas e outros segmentos.

### Identidade visual

Use a identidade conceitual: - Verde escuro `#063B2E`; verde `#18A34A`;
verde claro `#E8F5EE`. - Cinza claro `#F4F6F5`; branco `#FFFFFF`; texto
`#17211C`; secundário `#68736D`; borda `#E2E8E4`. - Tipografia Inter
(400, 500, 600, 700). - Estética minimalista premium, hierarquia clara,
preços em destaque, ícones lineares, espaçamento consistente,
componentes reutilizáveis e contraste acessível. - Evite neon, sombras
excessivas, cantos exagerados, visual de panfleto e decoração
supérflua. - Interface em português brasileiro; moeda `R$`, vírgula
decimal e datas brasileiras.

## 2. Telas e navegação

Navegação inferior consistente: **Início \| Pesquisar \| Adicionar preço
(ação central) \| Lista \| Perfil**.

Implementar: - Splash e onboarding. - Login, cadastro, recuperação de
senha e perfil. - Início: pesquisa, região, economia, ofertas,
populares, favoritos e listas recentes. - Busca/resultados: nome, marca,
categoria e EAN/GTIN; sugestões, filtros, ordenação, favoritos e
histórico. - Detalhes do produto: imagem, marca, categoria, descrição,
embalagem, unidade e código de barras. - Comparação: mesmo produto em
lojas distintas, menor preço, preço unitário, data de atualização,
distância e condições promocionais. - Histórico: evolução, mínimo,
máximo, média e variação percentual, somente com registros existentes. -
Cadastro de preço: produto, loja/unidade, valor, quantidade/unidade,
data/hora, tipo (regular/promocional), validade, origem e comprovante
opcional. - Lista: múltiplas listas, adicionar/remover/editar itens e
quantidades, marcar como comprado, duplicar, salvar e compartilhar;
total e economia estimados. - Otimização: comparar compra em uma loja,
compra por item no menor preço e divisão entre lojas; considerar
distância, deslocamento, disponibilidade e condições quando houver
dados. - Favoritos, notificações, configurações, privacidade, exportação
e exclusão de conta.

Toda ação visível deve funcionar. Implementar estados de carregamento,
erro, vazio, sucesso e ausência de conexão.

## 3. Funcionalidades e regras de negócio

### Produtos e equivalência

Cada produto deve ter identificador, nome, marca, categoria, imagem,
descrição, embalagem, quantidade, unidade e EAN/GTIN quando disponível.
Normalizar nomes e códigos para evitar duplicatas. Não tratar produtos
de marcas, tamanhos ou variantes diferentes como equivalentes sem regra
explícita.

### Supermercados

Separar rede e loja física. Cada unidade pode ter nome, endereço,
cidade/UF, coordenadas, horários e contatos, quando disponíveis.

### Registro colaborativo de preços

Cada registro relaciona produto e unidade específica e contém valor,
quantidade/unidade, data/hora, usuário/origem, tipo de preço, validade e
status de validação. Permitir comprovante/foto opcional. Implementar
detecção de duplicatas e anomalias, histórico de alterações,
confirmação/contestação, moderação e reputação. Exibir sempre origem e
data da coleta. Sinalizar registros antigos; nunca apresentar preço
desatualizado como atual.

### Comparação

Ordenar por menor preço; comparar preço por unidade apenas quando as
unidades forem compatíveis. Evidenciar embalagem, quantidade, marca,
validade e condições de promoção. Exibir data de atualização,
localização e distância quando disponíveis. Não comparar itens
incompatíveis nem ocultar restrições de ofertas.

### Listas e economia

Calcular: - Total: soma de preço unitário aplicável × quantidade
necessária. - Preço por unidade: preço da embalagem ÷ quantidade
comercializada, com conversão válida de unidades. - Economia estimada:
preço de referência comparável − preço escolhido. - Economia percentual:
economia ÷ preço de referência × 100.

Definir e informar a origem do preço de referência. Diferenciar economia
**potencial** de economia **realizada**. Tratar preços ausentes,
vencidos, conflitantes e ofertas condicionais. Para otimização,
apresentar premissas, custos de deslocamento e diferenças entre comprar
em uma loja ou dividir a compra. Não prometer economia sem dados
suficientes.

### Notificações

Alertas configuráveis para queda de preço, novos preços de favoritos,
ofertas próximas e mudanças relevantes. Permitir desativar por categoria
ou totalmente.

## 4. Arquitetura sugerida

Se o projeto não tiver stack estabelecida: - **Mobile:** Flutter/Dart,
Material 3 personalizado, Riverpod, GoRouter, Dio;
Freezed/json_serializable quando úteis. - **Backend:** Supabase,
PostgreSQL, Auth, Storage, REST e Edge Functions quando necessário. -
**Persistência:** cache/local para listas e uso offline, com
sincronização e resolução de conflitos. - **Qualidade/infra:** Git,
migrações versionadas, ambientes dev/homologação/produção, CI/CD, logs e
monitoramento.

Organize por módulos e camadas: Presentation, Application, Domain, Data,
Core, Shared e Services. Separe funcionalidades por domínio. Evite
arquivos gigantes, duplicação e dependências desnecessárias.

### Modelo de dados inicial

Considere entidades: `profiles`, `products`, `product_categories`,
`brands`, `product_barcodes`, `supermarket_chains`,
`supermarket_stores`, `price_records`, `price_validations`,
`price_history`, `shopping_lists`, `shopping_list_items`, `favorites`,
`notifications`, `user_reputation`, `reports`.

Defina PK/FK, índices, constraints, relacionamentos, timestamps,
retenção e consultas. Use migrações versionadas. Aplique RLS por usuário
e papel. Valide regras no servidor; não confie apenas no cliente.

## 5. Segurança, privacidade e acessibilidade

Atenda à LGPD. Implementar autorização no backend, validação de entrada,
proteção contra SQL injection, rate limiting, auditoria de operações
críticas, armazenamento seguro de tokens, gestão de permissões,
exportação e exclusão de dados. Nunca incluir chaves privadas ou
credenciais administrativas no app. Criar política de privacidade.
Garantir contraste, leitores de tela, áreas de toque adequadas,
escalabilidade de texto, mensagens compreensíveis e suporte a diferentes
telas.

## 6. Dados e integrações

Não invente preços, ofertas, lojas ou histórico como dados reais. Dados
fictícios só em ambiente demonstrativo, claramente identificados e
isolados da produção. Se não houver fonte/API autorizada para preços,
implementar registro colaborativo e documentar a limitação. Não realizar
scraping ou integração sem avaliar autorização, termos e confiabilidade.
Credenciais e serviços externos ausentes devem ser documentados; criar
interfaces/adapters e modo demonstrativo sem fingir integração real.

## 7. Testes e QA

Criar testes unitários, widget/UI, integração, API, segurança e
navegação. Cobrir: - Autenticação, autorização e RLS. - Pesquisa,
normalização e duplicidade de produtos. - Registros simultâneos e preços
conflitantes. - Preços antigos e promoções expiradas. - Embalagens e
unidades incompatíveis. - Quantidades fracionadas e arredondamento
monetário. - Listas vazias, sincronização e falhas de rede. - Cálculo de
total, economia e otimização. - Usuários não autenticados e acesso
indevido.

Corrigir causa raiz, não mascarar erros. Não deixar botões sem ação nem
telas com dados estáticos apresentados como integração real.

## 8. Plano de execução

1.  **Auditoria:** inspecionar repositório, stack, dependências,
    funcionalidades, erros e riscos; apresentar plano objetivo.
2.  **Design system:** implementar marca, tokens, componentes e quatro
    telas centrais.
3.  **Fundação:** configurar arquitetura, banco, migrações, autenticação
    e segurança.
4.  **MVP:** produtos, lojas, pesquisa, registro de preços, comparação e
    listas.
5.  **Evolução:** histórico, favoritos, localização, otimização,
    reputação, moderação e notificações.
6.  **Integração:** conectar UI e APIs, cache, sincronização e
    tratamento de falhas.
7.  **QA:** executar testes, corrigir defeitos, avaliar desempenho e
    segurança em emuladores/dispositivos.
8.  **Entrega:** preparar build, documentação, configuração e
    publicação.

Trabalhe incrementalmente. Após cada etapa, mantenha o projeto
executável e informe arquivos alterados, decisões, testes executados,
resultados e pendências. Não avance ocultando falhas.

## 9. Critérios de aceite

O MVP estará pronto quando: - O app compilar e iniciar sem erros. -
Navegação e ações estiverem funcionais. - Cadastro/login e permissões
funcionarem. - Produtos e lojas forem persistidos e consultáveis. -
Usuários puderem registrar preços. - Comparações respeitarem
equivalência, unidade e atualização. - Listas permitirem CRUD completo e
totais corretos. - Economia tiver cálculo e referência transparentes. -
RLS e regras de segurança estiverem ativas. - Testes essenciais
passarem. - Instalação, configuração, banco, APIs e limitações estiverem
documentados.

## 10. Entrega final

Entregar código-fonte organizado, aplicativo Android funcional, backend
e migrações, documentação de arquitetura/API/banco, instruções de
configuração e execução, testes automatizados, dados demonstrativos
isolados e build de desenvolvimento.

**Instrução final:** compreenda o projeto antes de editar; priorize
funcionamento real, qualidade dos dados, segurança, UX, manutenibilidade
e transparência. Não entregue apenas telas, não simule integrações, não
invente dados reais e não declare concluído o que não foi implementado e
testado. O resultado deve ser um MVP PICPAD executável, integrado,
testado e preparado para evoluir.
