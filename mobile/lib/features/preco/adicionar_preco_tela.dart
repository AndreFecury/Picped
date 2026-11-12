import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/formatos.dart' as f;
import '../../core/geo.dart';
import '../../core/theme.dart';
import '../../data/api.dart';
import '../../data/modelos.dart';
import '../../data/providers.dart';
import '../../shared/produto_widgets.dart';
import '../../shared/scanner.dart';
import '../../shared/widgets.dart';

class AdicionarPrecoTela extends ConsumerStatefulWidget {
  const AdicionarPrecoTela({super.key, this.produtoId});
  final int? produtoId;
  @override
  ConsumerState<AdicionarPrecoTela> createState() => _AdicionarPrecoTelaState();
}

class _AdicionarPrecoTelaState extends ConsumerState<AdicionarPrecoTela> {
  Produto? _produto;
  int? _mercadoId;
  String? _mercadoNome;
  int? _distancia; // só preenchida quando o mercado foi identificado pelo GPS
  final _valor = TextEditingController();

  bool _localizando = false;
  String? _avisoLocal;
  List<SupermercadoProximo>? _proximos;
  ({double lat, double lon})? _posicao;
  bool _enviando = false;

  @override
  void initState() {
    super.initState();
    _carregarProduto(widget.produtoId);
  }

  @override
  void didUpdateWidget(covariant AdicionarPrecoTela antigo) {
    super.didUpdateWidget(antigo);
    if (widget.produtoId != antigo.produtoId) _carregarProduto(widget.produtoId);
  }

  Future<void> _carregarProduto(int? id) async {
    if (id == null) return;
    try {
      final p = await ref.read(apiProvider).produto(id);
      if (mounted) setState(() => _produto = p);
    } on ApiException catch (e) {
      if (mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  Future<void> _escanear() async {
    final ean = await lerCodigoDeBarras(context);
    if (ean == null || !mounted) return;
    try {
      final achados = await ref.read(apiProvider).produtos(codigoBarras: ean);
      if (!mounted) return;
      if (achados.isEmpty) {
        avisar(context, 'Código $ean não cadastrado. Cadastre o produto primeiro.', erro: true);
        context.push('/novo-produto?ean=$ean');
      } else {
        setState(() => _produto = achados.first);
      }
    } on ApiException catch (e) {
      if (mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  Future<void> _localizar() async {
    setState(() {
      _localizando = true;
      _avisoLocal = null;
      _proximos = null;
    });
    try {
      final p = await posicaoAtual();
      _posicao = (lat: p.latitude, lon: p.longitude);
      final lista = await ref.read(apiProvider).proximos(p.latitude, p.longitude);
      if (!mounted) return;
      setState(() {
        _proximos = lista;
        if (lista.length == 1) _selecionar(lista.first.id, lista.first.nome, lista.first.distanciaMetros);
        if (lista.isEmpty) _avisoLocal = 'Nenhum supermercado cadastrado no raio da sua localização.';
      });
    } on LocalizacaoException catch (e) {
      setState(() => _avisoLocal = e.mensagem);
    } on ApiException catch (e) {
      setState(() => _avisoLocal = e.mensagem);
    } catch (e) {
      setState(() => _avisoLocal = 'Não foi possível obter sua localização ($e).');
    } finally {
      if (mounted) setState(() => _localizando = false);
    }
  }

  void _selecionar(int id, String nome, int? distancia) {
    _mercadoId = id;
    _mercadoNome = nome;
    _distancia = distancia;
  }

  Future<void> _escolherDaLista() async {
    final mercados = await ref.read(supermercadosProvider.future).catchError((_) => <Supermercado>[]);
    if (!mounted) return;
    final ativos = mercados.where((m) => m.ativo).toList();
    final m = await showModalBottomSheet<Supermercado>(
      context: context,
      useSafeArea: true,
      isScrollControlled: true,
      builder: (c) => SizedBox(
        height: MediaQuery.of(c).size.height * 0.7,
        child: ListView(children: [
          const Padding(
            padding: EdgeInsets.all(Espaco.l),
            child: Text('Escolha o supermercado', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          ),
          if (ativos.isEmpty) const Vazio(icone: Icons.store_outlined, titulo: 'Nenhum supermercado cadastrado'),
          for (final m in ativos)
            ListTile(
              leading: const Icon(Icons.storefront_outlined),
              title: Text(m.nome),
              subtitle: Text(m.local),
              onTap: () => Navigator.pop(c, m),
            ),
        ]),
      ),
    );
    if (m != null) setState(() => _selecionar(m.id, m.nome, null));
  }

  Future<void> _cadastrarMercadoAqui() async {
    final pos = _posicao;
    if (pos == null) return;
    final nome = TextEditingController();
    final bairro = TextEditingController();
    final cidade = TextEditingController(text: 'Manaus');
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Cadastrar supermercado aqui'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: nome, decoration: const InputDecoration(labelText: 'Nome do supermercado')),
          const SizedBox(height: Espaco.s),
          TextField(controller: bairro, decoration: const InputDecoration(labelText: 'Bairro')),
          const SizedBox(height: Espaco.s),
          TextField(controller: cidade, decoration: const InputDecoration(labelText: 'Cidade')),
          const SizedBox(height: Espaco.s),
          Text('Localização: ${pos.lat.toStringAsFixed(5)}, ${pos.lon.toStringAsFixed(5)}',
              style: const TextStyle(fontSize: 12, color: Cores.secundario)),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancelar')),
          TextButton(onPressed: () => Navigator.pop(c, true), child: const Text('Cadastrar')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      final m = await ref.read(apiProvider).criarSupermercado({
        'nome': nome.text.trim(),
        'bairro': bairro.text.trim(),
        'cidade': cidade.text.trim(),
        'latitude': pos.lat,
        'longitude': pos.lon,
        'raio_metros': 150,
      });
      ref.invalidate(supermercadosProvider);
      if (mounted) {
        setState(() {
          _selecionar(m.id, m.nome, 0);
          _avisoLocal = null;
        });
      }
    } on ApiException catch (e) {
      if (mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  Future<void> _salvar() async {
    final valor = f.lerValor(_valor.text);
    if (_produto == null || _mercadoId == null || valor == null || valor <= 0) {
      avisar(context, 'Escolha o produto, o supermercado e informe um valor válido.', erro: true);
      return;
    }
    setState(() => _enviando = true);
    try {
      await ref.read(apiProvider).registrarPreco(
            produtoId: _produto!.id,
            supermercadoId: _mercadoId!,
            usuarioId: ref.read(sessaoProvider).value!.id,
            valor: valor,
            distanciaMetros: _distancia,
          );
      ref.invalidate(comparacaoProvider(_produto!.id));
      ref.invalidate(historicoProvider(_produto!.id));
      if (!mounted) return;
      final produto = _produto!;
      await showDialog<void>(
        context: context,
        builder: (c) => AlertDialog(
          icon: const Icon(Icons.check_circle_rounded, color: Cores.verde, size: 40),
          title: const Text('Preço registrado!'),
          content: Text('${produto.nome}\n${f.moeda(valor)} no $_mercadoNome.\nObrigado por colaborar.',
              textAlign: TextAlign.center),
          actions: [
            TextButton(onPressed: () => Navigator.pop(c), child: const Text('Registrar outro')),
            TextButton(
              onPressed: () {
                Navigator.pop(c);
                context.push('/produto/${produto.id}');
              },
              child: const Text('Ver comparação'),
            ),
          ],
        ),
      );
      setState(() {
        _produto = null;
        _valor.clear();
      });
    } on ApiException catch (e) {
      if (mounted) avisar(context, e.mensagem, erro: true);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Adicionar preço')),
        body: ListView(padding: const EdgeInsets.fromLTRB(Espaco.l, 0, Espaco.l, Espaco.xxl), children: [
          const Text('Viu um preço no mercado? Registre e ajude todo mundo a economizar.',
              style: TextStyle(color: Cores.secundario)),
          const Secao('1. Produto'),
          if (_produto != null)
            ProdutoTile(
              produto: _produto!,
              trailing: IconButton(
                tooltip: 'Trocar produto',
                icon: const Icon(Icons.close),
                onPressed: () => setState(() => _produto = null),
              ),
            )
          else
            Row(children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () async {
                    final p = await escolherProduto(context);
                    if (p != null) setState(() => _produto = p);
                  },
                  icon: const Icon(Icons.search),
                  label: const Text('Buscar'),
                ),
              ),
              const SizedBox(width: Espaco.m),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _escanear,
                  icon: const Icon(Icons.qr_code_scanner_rounded),
                  label: const Text('Ler código'),
                ),
              ),
            ]),
          const Secao('2. Supermercado'),
          if (_mercadoId != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.storefront_rounded, color: Cores.verde),
                title: Text(_mercadoNome!, style: const TextStyle(fontWeight: FontWeight.w600)),
                subtitle: Text(_distancia != null
                    ? 'Identificado pela localização · ${f.distancia(_distancia!)}'
                    : 'Escolhido manualmente'),
                trailing: IconButton(
                  tooltip: 'Trocar supermercado',
                  icon: const Icon(Icons.close),
                  onPressed: () => setState(() {
                    _mercadoId = null;
                    _distancia = null;
                  }),
                ),
              ),
            )
          else ...[
            FilledButton.icon(
              style: FilledButton.styleFrom(backgroundColor: Cores.verdeEscuro),
              onPressed: _localizando ? null : _localizar,
              icon: _localizando
                  ? const SizedBox(
                      width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Cores.branco))
                  : const Icon(Icons.my_location_rounded),
              label: Text(_localizando ? 'Localizando...' : 'Usar minha localização'),
            ),
            if (_proximos != null && _proximos!.length > 1) ...[
              const SizedBox(height: Espaco.m),
              const Text('Encontramos mais de um mercado perto de você. Qual é o seu?'),
              for (final m in _proximos!)
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.storefront_outlined),
                    title: Text(m.nome),
                    subtitle: Text(f.distancia(m.distanciaMetros)),
                    onTap: () => setState(() => _selecionar(m.id, m.nome, m.distanciaMetros)),
                  ),
                ),
            ],
            if (_avisoLocal != null) ...[
              const SizedBox(height: Espaco.m),
              Text(_avisoLocal!, style: const TextStyle(color: Cores.alerta)),
              if (_posicao != null && (_proximos?.isEmpty ?? false))
                TextButton.icon(
                  onPressed: _cadastrarMercadoAqui,
                  icon: const Icon(Icons.add_business_outlined),
                  label: const Text('Cadastrar um supermercado neste local'),
                ),
            ],
            const SizedBox(height: Espaco.s),
            OutlinedButton.icon(
              onPressed: _escolherDaLista,
              icon: const Icon(Icons.list_alt_rounded),
              label: const Text('Escolher da lista'),
            ),
          ],
          const Secao('3. Valor'),
          TextField(
            controller: _valor,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9,.]'))],
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
            decoration: const InputDecoration(prefixText: r'R$ ', hintText: '0,00'),
          ),
          const SizedBox(height: Espaco.s),
          const Text('Data e hora são registradas automaticamente. Seu nome fica como autor do registro.',
              style: TextStyle(fontSize: 12, color: Cores.secundario)),
          const SizedBox(height: Espaco.xl),
          FilledButton(
            onPressed: _enviando ? null : _salvar,
            child: _enviando
                ? const SizedBox(
                    width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Cores.branco))
                : const Text('Registrar preço'),
          ),
        ]),
      );
}
