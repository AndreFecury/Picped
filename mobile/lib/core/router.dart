import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/providers.dart';
import '../features/auth/cadastro_tela.dart';
import '../features/auth/login_tela.dart';
import '../features/auth/splash_tela.dart';
import '../features/busca/busca_tela.dart';
import '../features/busca/novo_produto_tela.dart';
import '../features/inicio/inicio_tela.dart';
import '../features/listas/lista_tela.dart';
import '../features/listas/listas_tela.dart';
import '../features/perfil/perfil_tela.dart';
import '../features/preco/adicionar_preco_tela.dart';
import '../features/produto/produto_tela.dart';
import 'shell.dart';

final routerProvider = Provider<GoRouter>((ref) {
  // reavalia o redirect sempre que a sessão muda (login, logout, token expirado)
  final aviso = ValueNotifier(0);
  ref.listen(sessaoProvider, (_, _) => aviso.value++);
  ref.onDispose(aviso.dispose);

  return GoRouter(
    initialLocation: '/splash',
    refreshListenable: aviso,
    redirect: (context, estado) {
      final sessao = ref.read(sessaoProvider);
      final rota = estado.matchedLocation;
      final publica = rota == '/login' || rota == '/cadastro';
      if (sessao.isLoading || sessao.hasError) return rota == '/splash' ? null : '/splash';
      final logado = sessao.value != null;
      if (!logado) return publica ? null : '/login';
      if (publica || rota == '/splash') return '/inicio';
      return null;
    },
    routes: [
      GoRoute(path: '/splash', builder: (_, _) => const SplashTela()),
      GoRoute(path: '/login', builder: (_, _) => const LoginTela()),
      GoRoute(path: '/cadastro', builder: (_, _) => const CadastroTela()),
      StatefulShellRoute.indexedStack(
        builder: (context, estado, navegacao) => Shell(navegacao: navegacao),
        branches: [
          StatefulShellBranch(routes: [GoRoute(path: '/inicio', builder: (_, _) => const InicioTela())]),
          StatefulShellBranch(routes: [GoRoute(path: '/pesquisar', builder: (_, _) => const BuscaTela())]),
          StatefulShellBranch(routes: [
            GoRoute(
              path: '/adicionar',
              builder: (_, e) => AdicionarPrecoTela(produtoId: int.tryParse(e.uri.queryParameters['produto'] ?? '')),
            ),
          ]),
          StatefulShellBranch(routes: [GoRoute(path: '/listas', builder: (_, _) => const ListasTela())]),
          StatefulShellBranch(routes: [GoRoute(path: '/perfil', builder: (_, _) => const PerfilTela())]),
        ],
      ),
      GoRoute(path: '/produto/:id', builder: (_, e) => ProdutoTela(id: int.parse(e.pathParameters['id']!))),
      GoRoute(path: '/lista/:id', builder: (_, e) => ListaTela(id: int.parse(e.pathParameters['id']!))),
      GoRoute(
        path: '/novo-produto',
        builder: (_, e) => NovoProdutoTela(
          codigoBarras: e.uri.queryParameters['ean'],
          nome: e.uri.queryParameters['nome'],
        ),
      ),
    ],
  );
});
