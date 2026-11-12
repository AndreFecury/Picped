import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/theme.dart';
import '../data/api.dart';
import '../data/modelos.dart';
import '../data/providers.dart';
import 'widgets.dart';

class ProdutoTile extends StatelessWidget {
  const ProdutoTile({super.key, required this.produto, this.aoTocar, this.trailing});
  final Produto produto;
  final VoidCallback? aoTocar;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) => Card(
        child: ListTile(
          onTap: aoTocar,
          contentPadding: const EdgeInsets.symmetric(horizontal: Espaco.l, vertical: Espaco.xs),
          leading: Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(color: Cores.verdeClaro, borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.shopping_basket_outlined, color: Cores.verdeEscuro),
          ),
          title: Text(produto.nome, style: const TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text(produto.descricao, style: const TextStyle(color: Cores.secundario, fontSize: 13)),
          trailing: trailing ?? const Icon(Icons.chevron_right_rounded, color: Cores.secundario),
        ),
      );
}

/// Folha inferior para escolher um produto (busca por nome). Devolve o produto escolhido.
Future<Produto?> escolherProduto(BuildContext context) => showModalBottomSheet<Produto>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      backgroundColor: Cores.cinzaClaro,
      builder: (_) => const _EscolherProduto(),
    );

class _EscolherProduto extends ConsumerStatefulWidget {
  const _EscolherProduto();
  @override
  ConsumerState<_EscolherProduto> createState() => _EscolherProdutoState();
}

class _EscolherProdutoState extends ConsumerState<_EscolherProduto> {
  String _texto = '';

  @override
  Widget build(BuildContext context) {
    final resultado = ref.watch(buscaProvider((texto: _texto, categoriaId: null)));
    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.8,
        child: Column(children: [
          Padding(
            padding: const EdgeInsets.all(Espaco.l),
            child: TextField(
              autofocus: true,
              decoration: const InputDecoration(hintText: 'Buscar produto (ex.: arroz)', prefixIcon: Icon(Icons.search)),
              onChanged: (v) => setState(() => _texto = v),
            ),
          ),
          Expanded(
            child: _texto.trim().length < 2
                ? const Vazio(icone: Icons.search_rounded, titulo: 'Digite ao menos 2 letras')
                : resultado.when(
                    loading: () => const Carregando(),
                    error: (e, _) => Erro(erro: e),
                    data: (lista) => lista.isEmpty
                        ? const Vazio(icone: Icons.search_off_rounded, titulo: 'Nenhum produto encontrado')
                        : ListView.separated(
                            padding: const EdgeInsets.symmetric(horizontal: Espaco.l),
                            itemCount: lista.length,
                            separatorBuilder: (_, _) => const SizedBox(height: Espaco.s),
                            itemBuilder: (_, i) =>
                                ProdutoTile(produto: lista[i], aoTocar: () => Navigator.pop(context, lista[i])),
                          ),
                  ),
          ),
        ]),
      ),
    );
  }
}

/// Adiciona o produto a uma lista do usuário (escolhe a lista ou cria uma nova).
Future<void> adicionarALista(BuildContext context, WidgetRef ref, Produto produto) async {
  final api = ref.read(apiProvider);
  List<ListaResumo> listas;
  try {
    listas = await api.listas();
  } on ApiException catch (e) {
    if (context.mounted) avisar(context, e.mensagem, erro: true);
    return;
  }
  if (!context.mounted) return;
  final escolha = await showModalBottomSheet<int>(
    context: context,
    useSafeArea: true,
    builder: (c) => SafeArea(
      child: ListView(shrinkWrap: true, children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(Espaco.l, Espaco.l, Espaco.l, Espaco.s),
          child: Text('Adicionar à lista', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
        ),
        for (final l in listas)
          ListTile(
            leading: const Icon(Icons.checklist_rounded),
            title: Text(l.nome),
            subtitle: Text('${l.totalItens} itens'),
            onTap: () => Navigator.pop(c, l.id),
          ),
        ListTile(
          leading: const Icon(Icons.add_rounded, color: Cores.verde),
          title: const Text('Nova lista', style: TextStyle(color: Cores.verde, fontWeight: FontWeight.w600)),
          onTap: () => Navigator.pop(c, -1),
        ),
      ]),
    ),
  );
  if (escolha == null || !context.mounted) return;
  try {
    var listaId = escolha;
    if (escolha == -1) {
      final nome = await pedirTexto(context, titulo: 'Nova lista', rotulo: 'Nome da lista', inicial: 'Minha lista');
      if (nome == null) return;
      listaId = await api.criarLista(nome);
    }
    await api.adicionarItem(listaId, produto.id, 1);
    ref.invalidate(listasProvider);
    ref.invalidate(listaProvider(listaId));
    if (context.mounted) avisar(context, '${produto.nome} adicionado à lista.');
  } on ApiException catch (e) {
    if (context.mounted) {
      avisar(context, e.status == 409 ? 'Este produto já está nessa lista.' : e.mensagem, erro: true);
    }
  }
}

Future<String?> pedirTexto(BuildContext context,
    {required String titulo, required String rotulo, String inicial = ''}) async {
  final c = TextEditingController(text: inicial);
  final r = await showDialog<String>(
    context: context,
    builder: (d) => AlertDialog(
      title: Text(titulo),
      content: TextField(
        controller: c,
        autofocus: true,
        textCapitalization: TextCapitalization.sentences,
        decoration: InputDecoration(labelText: rotulo),
        onSubmitted: (v) => Navigator.pop(d, v),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(d), child: const Text('Cancelar')),
        TextButton(onPressed: () => Navigator.pop(d, c.text), child: const Text('Salvar')),
      ],
    ),
  );
  if (r == null || r.trim().length < 2) return null;
  return r.trim();
}
