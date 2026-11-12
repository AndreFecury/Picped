import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';
import '../../data/api.dart';
import '../../data/providers.dart';
import '../../shared/produto_widgets.dart';
import '../../shared/scanner.dart';
import '../../shared/widgets.dart';

class BuscaTela extends ConsumerStatefulWidget {
  const BuscaTela({super.key});
  @override
  ConsumerState<BuscaTela> createState() => _BuscaTelaState();
}

class _BuscaTelaState extends ConsumerState<BuscaTela> {
  final _campo = TextEditingController();
  Timer? _espera;
  String _texto = '';
  int? _categoria;

  @override
  void dispose() {
    _espera?.cancel();
    _campo.dispose();
    super.dispose();
  }

  void _digitou(String v) {
    _espera?.cancel();
    _espera = Timer(const Duration(milliseconds: 350), () => setState(() => _texto = v));
  }

  Future<void> _escanear() async {
    final ean = await lerCodigoDeBarras(context);
    if (ean == null || !mounted) return;
    try {
      final achados = await ref.read(apiProvider).produtos(codigoBarras: ean);
      if (!mounted) return;
      if (achados.isNotEmpty) {
        context.push('/produto/${achados.first.id}');
      } else {
        final cadastrar = await showDialog<bool>(
          context: context,
          builder: (c) => AlertDialog(
            title: const Text('Produto não cadastrado'),
            content: Text('Nenhum produto com o código $ean. Deseja cadastrá-lo?'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Agora não')),
              TextButton(onPressed: () => Navigator.pop(c, true), child: const Text('Cadastrar')),
            ],
          ),
        );
        if (cadastrar == true && mounted) context.push('/novo-produto?ean=$ean');
      }
    } on ApiException catch (e) {
      if (mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final categorias = ref.watch(categoriasProvider);
    final filtro = (texto: _texto, categoriaId: _categoria);
    final resultado = ref.watch(buscaProvider(filtro));
    final buscando = _texto.trim().length >= 2 || _categoria != null;

    return Scaffold(
      appBar: AppBar(title: const Text('Pesquisar')),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: Espaco.l),
          child: Row(children: [
            Expanded(
              child: TextField(
                controller: _campo,
                onChanged: _digitou,
                textInputAction: TextInputAction.search,
                decoration: InputDecoration(
                  hintText: 'Nome ou marca do produto',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _campo.text.isEmpty
                      ? null
                      : IconButton(
                          tooltip: 'Limpar',
                          icon: const Icon(Icons.close),
                          onPressed: () => setState(() {
                            _campo.clear();
                            _texto = '';
                          }),
                        ),
                ),
              ),
            ),
            const SizedBox(width: Espaco.s),
            IconButton.filled(
              tooltip: 'Ler código de barras',
              style: IconButton.styleFrom(backgroundColor: Cores.verdeEscuro, minimumSize: const Size(48, 48)),
              onPressed: _escanear,
              icon: const Icon(Icons.qr_code_scanner_rounded),
            ),
          ]),
        ),
        SizedBox(
          height: 56,
          child: categorias.maybeWhen(
            data: (lista) => ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: Espaco.l, vertical: Espaco.s),
              children: [
                for (final c in lista)
                  Padding(
                    padding: const EdgeInsets.only(right: Espaco.s),
                    child: FilterChip(
                      label: Text(c.nome),
                      selected: _categoria == c.id,
                      showCheckmark: false,
                      onSelected: (s) => setState(() => _categoria = s ? c.id : null),
                    ),
                  ),
              ],
            ),
            orElse: () => const SizedBox.shrink(),
          ),
        ),
        Expanded(
          child: !buscando
              ? const Vazio(
                  icone: Icons.manage_search_rounded,
                  titulo: 'O que você procura?',
                  mensagem: 'Pesquise pelo nome, marca, categoria ou leia o código de barras.',
                )
              : resultado.when(
                  loading: () => const Carregando(),
                  error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(buscaProvider(filtro))),
                  data: (lista) => lista.isEmpty
                      ? Vazio(
                          icone: Icons.search_off_rounded,
                          titulo: 'Nenhum produto encontrado',
                          mensagem: 'Ele ainda não está no Picped. Você pode cadastrá-lo.',
                          acao: OutlinedButton(
                            onPressed: () => context.push('/novo-produto?nome=${Uri.encodeComponent(_texto)}'),
                            child: const Text('Cadastrar produto'),
                          ),
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.fromLTRB(Espaco.l, Espaco.xs, Espaco.l, Espaco.xl),
                          itemCount: lista.length,
                          separatorBuilder: (_, _) => const SizedBox(height: Espaco.s),
                          itemBuilder: (_, i) => ProdutoTile(
                            produto: lista[i],
                            aoTocar: () => context.push('/produto/${lista[i].id}'),
                          ),
                        ),
                ),
        ),
      ]),
    );
  }
}
