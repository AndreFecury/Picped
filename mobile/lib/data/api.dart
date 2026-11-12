import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'modelos.dart';

/// Erro já traduzido para o usuário (vem do formato {"erro": {...}} da API).
class ApiException implements Exception {
  ApiException(this.mensagem, {this.status, this.semConexao = false});
  final String mensagem;
  final int? status;
  final bool semConexao;
  @override
  String toString() => mensagem;
}

// ---------------- configuração ----------------

/// Endereço padrão: 10.0.2.2 é o "localhost" do PC visto de dentro do emulador Android.
const urlPadrao = 'http://10.0.2.2:8000';
const _chaveUrl = 'api_url';
const _chaveToken = 'token';

final prefsProvider = Provider<SharedPreferences>((ref) => throw UnimplementedError('sobrescrito no main'));

class UrlApi extends Notifier<String> {
  @override
  String build() => ref.read(prefsProvider).getString(_chaveUrl) ?? urlPadrao;

  Future<void> definir(String url) async {
    var u = url.trim();
    if (!u.startsWith('http')) u = 'http://$u';
    if (u.endsWith('/')) u = u.substring(0, u.length - 1);
    await ref.read(prefsProvider).setString(_chaveUrl, u);
    state = u;
  }
}

final urlApiProvider = NotifierProvider<UrlApi, String>(UrlApi.new);

/// Token guardado no armazenamento seguro do Android (Keystore), nunca em texto puro.
class TokenStore {
  TokenStore([FlutterSecureStorage? s]) : _s = s ?? const FlutterSecureStorage();
  final FlutterSecureStorage _s;
  String? emMemoria;

  Future<String?> ler() async => emMemoria ??= await _s.read(key: _chaveToken);
  Future<void> salvar(String t) async {
    emMemoria = t;
    await _s.write(key: _chaveToken, value: t);
  }

  Future<void> apagar() async {
    emMemoria = null;
    await _s.delete(key: _chaveToken);
  }
}

final tokenStoreProvider = Provider<TokenStore>((ref) => TokenStore());

final apiProvider = Provider<PicpedApi>((ref) {
  final url = ref.watch(urlApiProvider);
  return PicpedApi(url, ref.read(tokenStoreProvider));
});

// ---------------- cliente ----------------

class PicpedApi {
  PicpedApi(String baseUrl, this.tokens)
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 8),
          receiveTimeout: const Duration(seconds: 15),
          contentType: 'application/json',
        )) {
    _dio.interceptors.add(InterceptorsWrapper(onRequest: (o, h) async {
      final t = await tokens.ler();
      if (t != null) o.headers['Authorization'] = 'Bearer $t';
      h.next(o);
    }));
  }

  final Dio _dio;
  final TokenStore tokens;

  Future<T> _req<T>(Future<Response> Function() chamada, T Function(dynamic) converter) async {
    try {
      final r = await chamada();
      return converter(r.data);
    } on DioException catch (e) {
      throw _traduzir(e);
    }
  }

  ApiException _traduzir(DioException e) {
    final r = e.response;
    if (r == null) {
      return ApiException(
        'Sem conexão com o servidor. Confira o Wi-Fi e o endereço da API em Perfil › Servidor.',
        semConexao: true,
      );
    }
    final corpo = r.data;
    if (corpo is Map && corpo['erro'] is Map) {
      final erro = corpo['erro'] as Map;
      var msg = erro['mensagem']?.toString() ?? 'Erro ${r.statusCode}';
      final detalhes = erro['detalhes'];
      if (detalhes is List && detalhes.isNotEmpty) {
        msg = '$msg ${detalhes.map((d) => '${d['campo']}: ${d['mensagem']}').join('; ')}';
      }
      return ApiException(msg, status: r.statusCode);
    }
    return ApiException('Erro ${r.statusCode} ao falar com o servidor.', status: r.statusCode);
  }

  List<T> _lista<T>(dynamic d, T Function(Map<String, dynamic>) f) =>
      (d as List).map((e) => f(e as Map<String, dynamic>)).toList();

  // ---- saúde ----
  Future<bool> saude() => _req(() => _dio.get('/health'), (d) => d['status'] == 'ok');

  // ---- autenticação ----
  Future<(String, Usuario)> login(String email, String senha) => _req(
        () => _dio.post('/auth/login', data: {'email': email.trim(), 'senha': senha}),
        (d) => (d['access_token'] as String, Usuario.fromJson(d['usuario'])),
      );
  Future<Usuario> eu() => _req(() => _dio.get('/auth/me'), (d) => Usuario.fromJson(d));
  Future<void> cadastrar(String nome, String email, String senha) =>
      _req(() => _dio.post('/usuarios', data: {'nome': nome.trim(), 'email': email.trim(), 'senha': senha}), (_) {});
  Future<void> excluirConta() => _req(() => _dio.delete('/auth/me'), (_) {});

  // ---- catálogo ----
  Future<List<Categoria>> categorias() =>
      _req(() => _dio.get('/categorias', queryParameters: {'limit': 200}), (d) => _lista(d, Categoria.fromJson));

  Future<List<Produto>> produtos({String? busca, String? codigoBarras, int? categoriaId}) => _req(
        () => _dio.get('/produtos', queryParameters: {
          'limit': 100,
          if (busca != null && busca.trim().length >= 2) 'busca': busca.trim(),
          'codigo_barras': ?codigoBarras,
          'categoria_id': ?categoriaId,
        }),
        (d) => _lista(d, Produto.fromJson),
      );
  Future<Produto> produto(int id) => _req(() => _dio.get('/produtos/$id'), (d) => Produto.fromJson(d));
  Future<Produto> criarProduto(Map<String, dynamic> dados) =>
      _req(() => _dio.post('/produtos', data: dados), (d) => Produto.fromJson(d));
  Future<Comparacao> comparacao(int produtoId) =>
      _req(() => _dio.get('/produtos/$produtoId/comparacao'), (d) => Comparacao.fromJson(d));
  Future<Historico> historico(int produtoId) =>
      _req(() => _dio.get('/produtos/$produtoId/historico'), (d) => Historico.fromJson(d));

  // ---- supermercados ----
  Future<List<Supermercado>> supermercados() =>
      _req(() => _dio.get('/supermercados', queryParameters: {'limit': 200}), (d) => _lista(d, Supermercado.fromJson));
  Future<List<SupermercadoProximo>> proximos(double lat, double lon) => _req(
        () => _dio.get('/supermercados/proximos', queryParameters: {'latitude': lat, 'longitude': lon}),
        (d) => _lista(d, SupermercadoProximo.fromJson),
      );
  Future<Supermercado> criarSupermercado(Map<String, dynamic> dados) =>
      _req(() => _dio.post('/supermercados', data: dados), (d) => Supermercado.fromJson(d));

  // ---- preços ----
  Future<void> registrarPreco({
    required int produtoId,
    required int supermercadoId,
    required int usuarioId,
    required double valor,
    int? distanciaMetros,
  }) =>
      _req(
        () => _dio.post('/precos', data: {
          'produto_id': produtoId,
          'supermercado_id': supermercadoId,
          'usuario_id': usuarioId,
          'valor': valor.toStringAsFixed(2),
          'distancia_metros': ?distanciaMetros,
        }),
        (_) {},
      );

  // ---- listas ----
  Future<List<ListaResumo>> listas() => _req(() => _dio.get('/listas'), (d) => _lista(d, ListaResumo.fromJson));
  Future<Lista> lista(int id) => _req(() => _dio.get('/listas/$id'), (d) => Lista.fromJson(d));
  Future<int> criarLista(String nome) => _req(() => _dio.post('/listas', data: {'nome': nome.trim()}), (d) => d['id'] as int);
  Future<void> renomearLista(int id, String nome) =>
      _req(() => _dio.patch('/listas/$id', data: {'nome': nome.trim()}), (_) {});
  Future<void> excluirLista(int id) => _req(() => _dio.delete('/listas/$id'), (_) {});
  Future<void> adicionarItem(int listaId, int produtoId, double quantidade) => _req(
        () => _dio.post('/listas/$listaId/itens', data: {'produto_id': produtoId, 'quantidade': quantidade}),
        (_) {},
      );
  Future<void> alterarItem(int listaId, int itemId, {double? quantidade, bool? comprado}) => _req(
        () => _dio.patch('/listas/$listaId/itens/$itemId', data: {
          'quantidade': ?quantidade,
          'comprado': ?comprado,
        }),
        (_) {},
      );
  Future<void> removerItem(int listaId, int itemId) => _req(() => _dio.delete('/listas/$listaId/itens/$itemId'), (_) {});
  Future<ComparacaoLista> comparacaoLista(int id) =>
      _req(() => _dio.get('/listas/$id/comparacao'), (d) => ComparacaoLista.fromJson(d));
}
