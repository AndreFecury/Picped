import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/geo.dart';
import 'api.dart';
import 'modelos.dart';

// ---------------- sessão ----------------

class Sessao extends AsyncNotifier<Usuario?> {
  @override
  Future<Usuario?> build() async {
    final api = ref.read(apiProvider);
    if (await api.tokens.ler() == null) return null;
    try {
      return await api.eu();
    } on ApiException catch (e) {
      if (e.status == 401) await api.tokens.apagar(); // token expirado
      if (e.semConexao) rethrow; // splash mostra "sem conexão" com opção de tentar de novo
      return null;
    }
  }

  Future<void> entrar(String email, String senha) async {
    final api = ref.read(apiProvider);
    final (token, usuario) = await api.login(email, senha);
    await api.tokens.salvar(token);
    state = AsyncData(usuario);
  }

  Future<void> cadastrar(String nome, String email, String senha) async {
    await ref.read(apiProvider).cadastrar(nome, email, senha);
    await entrar(email, senha);
  }

  Future<void> sair() async {
    await ref.read(apiProvider).tokens.apagar();
    state = const AsyncData(null);
  }

  Future<void> excluirConta() async {
    await ref.read(apiProvider).excluirConta();
    await sair();
  }
}

final sessaoProvider = AsyncNotifierProvider<Sessao, Usuario?>(Sessao.new);

Usuario usuarioLogado(Ref ref) => ref.read(sessaoProvider).value!;

// ---------------- dados ----------------

final categoriasProvider = FutureProvider<List<Categoria>>((ref) => ref.watch(apiProvider).categorias());

final supermercadosProvider = FutureProvider<List<Supermercado>>((ref) => ref.watch(apiProvider).supermercados());

final listasProvider = FutureProvider.autoDispose<List<ListaResumo>>((ref) => ref.watch(apiProvider).listas());

final listaProvider = FutureProvider.autoDispose.family<Lista, int>((ref, id) => ref.watch(apiProvider).lista(id));

final comparacaoListaProvider =
    FutureProvider.autoDispose.family<ComparacaoLista, int>((ref, id) => ref.watch(apiProvider).comparacaoLista(id));

final produtoProvider = FutureProvider.autoDispose.family<Produto, int>((ref, id) => ref.watch(apiProvider).produto(id));

final comparacaoProvider =
    FutureProvider.autoDispose.family<Comparacao, int>((ref, id) => ref.watch(apiProvider).comparacao(id));

final historicoProvider =
    FutureProvider.autoDispose.family<Historico, int>((ref, id) => ref.watch(apiProvider).historico(id));

typedef FiltroBusca = ({String texto, int? categoriaId});

final buscaProvider = FutureProvider.autoDispose.family<List<Produto>, FiltroBusca>((ref, f) {
  if (f.texto.trim().length < 2 && f.categoriaId == null) return Future.value(const []);
  return ref.watch(apiProvider).produtos(busca: f.texto, categoriaId: f.categoriaId);
});

/// Posição atual (null se o usuário negar ou o GPS falhar) — usada só para mostrar distâncias.
final posicaoProvider = FutureProvider<({double lat, double lon})?>((ref) async {
  try {
    final p = await posicaoAtual();
    return (lat: p.latitude, lon: p.longitude);
  } catch (_) {
    return null;
  }
});
