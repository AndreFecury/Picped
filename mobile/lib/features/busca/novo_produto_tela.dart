import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';
import '../../data/api.dart';
import '../../data/providers.dart';
import '../../shared/scanner.dart';
import '../../shared/widgets.dart';

const _unidades = {'un': 'Unidade', 'kg': 'Quilo (kg)', 'g': 'Grama (g)', 'l': 'Litro (l)', 'ml': 'Mililitro (ml)'};

class NovoProdutoTela extends ConsumerStatefulWidget {
  const NovoProdutoTela({super.key, this.codigoBarras, this.nome});
  final String? codigoBarras;
  final String? nome;
  @override
  ConsumerState<NovoProdutoTela> createState() => _NovoProdutoTelaState();
}

class _NovoProdutoTelaState extends ConsumerState<NovoProdutoTela> {
  final _form = GlobalKey<FormState>();
  late final _nome = TextEditingController(text: widget.nome ?? '');
  final _marca = TextEditingController();
  late final _ean = TextEditingController(text: widget.codigoBarras ?? '');
  String _unidade = 'un';
  int? _categoria;
  bool _enviando = false;

  Future<void> _salvar() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _enviando = true);
    try {
      final p = await ref.read(apiProvider).criarProduto({
        'nome': _nome.text.trim(),
        if (_marca.text.trim().isNotEmpty) 'marca': _marca.text.trim(),
        'unidade_medida': _unidade,
        if (_ean.text.trim().isNotEmpty) 'codigo_barras': _ean.text.trim(),
        'categoria_id': _categoria,
      });
      if (!mounted) return;
      avisar(context, 'Produto cadastrado.');
      context.pushReplacement('/produto/${p.id}');
    } on ApiException catch (e) {
      if (mounted) {
        avisar(context, e.status == 409 ? 'Já existe um produto com esse nome/marca ou código.' : e.mensagem,
            erro: true);
      }
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final categorias = ref.watch(categoriasProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Cadastrar produto')),
      body: Form(
        key: _form,
        child: ListView(padding: const EdgeInsets.all(Espaco.l), children: [
          TextFormField(
            controller: _nome,
            textCapitalization: TextCapitalization.sentences,
            decoration: const InputDecoration(labelText: 'Nome *', hintText: 'Ex.: Café Torrado 500g'),
            validator: (v) => v == null || v.trim().length < 2 ? 'Informe o nome com a embalagem' : null,
          ),
          const SizedBox(height: Espaco.m),
          TextFormField(
            controller: _marca,
            textCapitalization: TextCapitalization.words,
            decoration: const InputDecoration(labelText: 'Marca'),
          ),
          const SizedBox(height: Espaco.m),
          DropdownButtonFormField<String>(
            initialValue: _unidade,
            decoration: const InputDecoration(labelText: 'Vendido por *'),
            items: [for (final e in _unidades.entries) DropdownMenuItem(value: e.key, child: Text(e.value))],
            onChanged: (v) => setState(() => _unidade = v!),
          ),
          const SizedBox(height: Espaco.m),
          categorias.when(
            loading: () => const LinearProgressIndicator(),
            error: (e, _) => Text(e.toString(), style: const TextStyle(color: Cores.erro)),
            data: (lista) => DropdownButtonFormField<int>(
              initialValue: _categoria,
              decoration: const InputDecoration(labelText: 'Categoria *'),
              items: [for (final c in lista) DropdownMenuItem(value: c.id, child: Text(c.nome))],
              onChanged: (v) => setState(() => _categoria = v),
              validator: (v) => v == null ? 'Escolha a categoria' : null,
            ),
          ),
          const SizedBox(height: Espaco.m),
          TextFormField(
            controller: _ean,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: 'Código de barras (EAN)',
              suffixIcon: IconButton(
                tooltip: 'Ler com a câmera',
                icon: const Icon(Icons.qr_code_scanner_rounded),
                onPressed: () async {
                  final c = await lerCodigoDeBarras(context);
                  if (c != null) setState(() => _ean.text = c);
                },
              ),
            ),
            validator: (v) =>
                v == null || v.isEmpty || RegExp(r'^[0-9]{8,14}$').hasMatch(v) ? null : 'Use de 8 a 14 dígitos',
          ),
          const SizedBox(height: Espaco.xl),
          FilledButton(onPressed: _enviando ? null : _salvar, child: const Text('Salvar produto')),
        ]),
      ),
    );
  }
}
