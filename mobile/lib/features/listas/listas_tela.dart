import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/formatos.dart' as f;
import '../../core/theme.dart';
import '../../data/api.dart';
import '../../data/modelos.dart';
import '../../data/providers.dart';
import '../../shared/produto_widgets.dart';
import '../../shared/widgets.dart';

class ListasTela extends ConsumerWidget {
  const ListasTela({super.key});

  Future<void> _nova(BuildContext context, WidgetRef ref) async {
    final nome = await pedirTexto(context, titulo: 'Nova lista', rotulo: 'Nome da lista', inicial: 'Compra do mês');
    if (nome == null) return;
    try {
      final id = await ref.read(apiProvider).criarLista(nome);
      ref.invalidate(listasProvider);
      if (context.mounted) context.push('/lista/$id');
    } on ApiException catch (e) {
      if (context.mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final listas = ref.watch(listasProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Minhas listas')),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: Cores.verde,
        foregroundColor: Cores.branco,
        onPressed: () => _nova(context, ref),
        icon: const Icon(Icons.add_rounded),
        label: const Text('Nova lista'),
      ),
      body: listas.when(
        loading: () => const Carregando(),
        error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(listasProvider)),
        data: (l) => l.isEmpty
            ? Vazio(
                icone: Icons.checklist_rounded,
                titulo: 'Nenhuma lista ainda',
                mensagem: 'Crie uma lista e descubra em qual mercado ela sai mais barata.',
                acao: FilledButton(onPressed: () => _nova(context, ref), child: const Text('Criar lista')),
              )
            : RefreshIndicator(
                color: Cores.verde,
                onRefresh: () => ref.refresh(listasProvider.future),
                child: ListView.separated(
                  padding: const EdgeInsets.fromLTRB(Espaco.l, 0, Espaco.l, 96),
                  itemCount: l.length,
                  separatorBuilder: (_, _) => const SizedBox(height: Espaco.s),
                  itemBuilder: (_, i) => _ListaCard(lista: l[i]),
                ),
              ),
      ),
    );
  }
}

class _ListaCard extends ConsumerWidget {
  const _ListaCard({required this.lista});
  final ListaResumo lista;

  Future<void> _menu(BuildContext context, WidgetRef ref, String acao) async {
    final api = ref.read(apiProvider);
    try {
      if (acao == 'renomear') {
        final nome = await pedirTexto(context, titulo: 'Renomear lista', rotulo: 'Nome', inicial: lista.nome);
        if (nome == null) return;
        await api.renomearLista(lista.id, nome);
      } else if (acao == 'excluir') {
        final ok = await showDialog<bool>(
          context: context,
          builder: (c) => AlertDialog(
            title: const Text('Excluir lista?'),
            content: Text('"${lista.nome}" e seus ${lista.totalItens} itens serão apagados.'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancelar')),
              TextButton(
                onPressed: () => Navigator.pop(c, true),
                child: const Text('Excluir', style: TextStyle(color: Cores.erro)),
              ),
            ],
          ),
        );
        if (ok != true) return;
        await api.excluirLista(lista.id);
      }
      ref.invalidate(listasProvider);
    } on ApiException catch (e) {
      if (context.mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) => Card(
        child: ListTile(
          contentPadding: const EdgeInsets.fromLTRB(Espaco.l, Espaco.xs, Espaco.xs, Espaco.xs),
          onTap: () => context.push('/lista/${lista.id}'),
          leading: Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(color: Cores.verdeClaro, borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.checklist_rounded, color: Cores.verdeEscuro),
          ),
          title: Text(lista.nome, style: const TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text('${lista.totalItens} itens · criada em ${f.data(lista.criadaEm)}',
              style: const TextStyle(color: Cores.secundario, fontSize: 13)),
          trailing: PopupMenuButton<String>(
            tooltip: 'Opções da lista',
            onSelected: (a) => _menu(context, ref, a),
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'renomear', child: Text('Renomear')),
              PopupMenuItem(value: 'excluir', child: Text('Excluir')),
            ],
          ),
        ),
      );
}
