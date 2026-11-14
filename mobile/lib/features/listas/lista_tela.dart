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

class ListaTela extends ConsumerWidget {
  const ListaTela({super.key, required this.id});
  final int id;

  void _atualizar(WidgetRef ref) {
    ref.invalidate(listaProvider(id));
    ref.invalidate(comparacaoListaProvider(id));
    ref.invalidate(listasProvider);
  }

  Future<void> _executar(BuildContext context, WidgetRef ref, Future<void> Function() acao) async {
    try {
      await acao();
      _atualizar(ref);
    } on ApiException catch (e) {
      if (context.mounted) {
        avisar(context, e.status == 409 ? 'Este produto já está na lista.' : e.mensagem, erro: true);
      }
    }
  }

  Future<void> _adicionar(BuildContext context, WidgetRef ref) async {
    final p = await escolherProduto(context);
    if (p == null || !context.mounted) return;
    await _executar(context, ref, () => ref.read(apiProvider).adicionarItem(id, p.id, 1));
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lista = ref.watch(listaProvider(id));
    final api = ref.read(apiProvider);
    return Scaffold(
      appBar: AppBar(title: Text(lista.value?.nome ?? 'Lista')),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: Cores.verde,
        foregroundColor: Cores.branco,
        onPressed: () => _adicionar(context, ref),
        icon: const Icon(Icons.add_rounded),
        label: const Text('Adicionar item'),
      ),
      body: lista.when(
        loading: () => const Carregando(),
        error: (e, _) => Erro(erro: e, aoTentar: () => _atualizar(ref)),
        data: (l) {
          if (l.itens.isEmpty) {
            return Vazio(
              icone: Icons.add_shopping_cart_rounded,
              titulo: 'Lista vazia',
              mensagem: 'Adicione produtos para ver o total e onde a compra sai mais barata.',
              acao: FilledButton(onPressed: () => _adicionar(context, ref), child: const Text('Adicionar item')),
            );
          }
          final comprados = l.itens.where((i) => i.comprado).length;
          return RefreshIndicator(
            color: Cores.verde,
            onRefresh: () async => _atualizar(ref),
            child: ListView(padding: const EdgeInsets.fromLTRB(Espaco.l, 0, Espaco.l, 96), children: [
              Row(children: [
                Expanded(
                  child: Text('$comprados de ${l.itens.length} comprados',
                      style: const TextStyle(color: Cores.secundario, fontWeight: FontWeight.w500)),
                ),
              ]),
              const SizedBox(height: Espaco.s),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: comprados / l.itens.length,
                  minHeight: 6,
                  backgroundColor: Cores.borda,
                  color: Cores.verde,
                ),
              ),
              const SizedBox(height: Espaco.m),
              for (final item in l.itens) ...[
                _ItemCard(
                    item: item,
                    aoMarcar: (v) => _executar(context, ref, () => api.alterarItem(id, item.id, comprado: v)),
                    aoMudarQtd: (q) => _executar(context, ref, () => api.alterarItem(id, item.id, quantidade: q)),
                    aoRemover: () => _executar(context, ref, () => api.removerItem(id, item.id)),
                ),
                const SizedBox(height: Espaco.s),
              ],
              const Secao('Onde comprar esta lista'),
              _ComparacaoLista(listaId: id),
            ]),
          );
        },
      ),
    );
  }
}

class _ItemCard extends StatelessWidget {
  const _ItemCard({required this.item, required this.aoMarcar, required this.aoMudarQtd, required this.aoRemover});
  final ItemLista item;
  final ValueChanged<bool> aoMarcar;
  final ValueChanged<double> aoMudarQtd;
  final VoidCallback aoRemover;

  @override
  Widget build(BuildContext context) {
    final fracionado = item.unidadeMedida != 'un';
    final passo = fracionado ? 0.5 : 1.0;
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: Espaco.xs, vertical: Espaco.xs),
        child: Row(children: [
          Checkbox(
            value: item.comprado,
            activeColor: Cores.verde,
            onChanged: (v) => aoMarcar(v ?? false),
          ),
          Expanded(
            child: InkWell(
              onTap: () => context.push('/produto/${item.produtoId}'),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(
                  item.produtoNome,
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    decoration: item.comprado ? TextDecoration.lineThrough : null,
                    color: item.comprado ? Cores.secundario : Cores.texto,
                  ),
                ),
                if (item.produtoMarca != null)
                  Text(item.produtoMarca!, style: const TextStyle(color: Cores.secundario, fontSize: 12)),
              ]),
            ),
          ),
          IconButton(
            tooltip: 'Diminuir',
            icon: const Icon(Icons.remove_circle_outline),
            onPressed: item.quantidade - passo <= 0 ? aoRemover : () => aoMudarQtd(item.quantidade - passo),
          ),
          Text('${f.numero(item.quantidade)} ${item.unidadeMedida}',
              style: const TextStyle(fontWeight: FontWeight.w600)),
          IconButton(
            tooltip: 'Aumentar',
            icon: const Icon(Icons.add_circle_outline, color: Cores.verde),
            onPressed: () => aoMudarQtd(item.quantidade + passo),
          ),
        ]),
      ),
    );
  }
}

class _ComparacaoLista extends ConsumerWidget {
  const _ComparacaoLista({required this.listaId});
  final int listaId;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final comp = ref.watch(comparacaoListaProvider(listaId));
    return comp.when(
      loading: () => const Padding(padding: EdgeInsets.all(Espaco.xl), child: Carregando()),
      error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(comparacaoListaProvider(listaId))),
      data: (c) {
        if (c.supermercados.isEmpty) {
          return const Vazio(
            icone: Icons.price_change_outlined,
            titulo: 'Sem preços para comparar',
            mensagem: 'Nenhum item desta lista tem preço registrado ainda.',
          );
        }
        final melhor = c.melhorOpcao;
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          if (melhor != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(Espaco.l),
              decoration: BoxDecoration(color: Cores.verdeEscuro, borderRadius: BorderRadius.circular(raio)),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Melhor opção', style: TextStyle(color: Cores.verdeClaro, fontSize: 13)),
                Text(melhor.supermercadoNome,
                    style: const TextStyle(color: Cores.branco, fontSize: 18, fontWeight: FontWeight.w700)),
                const SizedBox(height: Espaco.xs),
                Text(f.moeda(melhor.total),
                    style: const TextStyle(color: Cores.branco, fontSize: 28, fontWeight: FontWeight.w700)),
                if (c.economia > 0)
                  Text('Economia potencial de ${f.moeda(c.economia)} (${f.percentual(c.economiaPercentual)})',
                      style: const TextStyle(color: Cores.verdeClaro, fontWeight: FontWeight.w600)),
              ]),
            )
          else
            const Text('Nenhum supermercado tem preço para todos os itens. Veja os parciais abaixo.',
                style: TextStyle(color: Cores.alerta)),
          const SizedBox(height: Espaco.m),
          for (final m in c.supermercados)
            Padding(
              padding: const EdgeInsets.only(bottom: Espaco.s),
              child: Card(
                child: ListTile(
                  title: Text(m.supermercadoNome, style: const TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text(
                    m.completo
                        ? 'Todos os ${c.totalItens} itens com preço'
                        : 'Faltam ${m.itensFaltando} de ${c.totalItens} itens (total parcial)',
                    style: TextStyle(color: m.completo ? Cores.secundario : Cores.alerta, fontSize: 12),
                  ),
                  trailing: Text(f.moeda(m.total),
                      style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: m == melhor || m.supermercadoId == melhor?.supermercadoId ? Cores.verde : Cores.texto)),
                ),
              ),
            ),
          const SizedBox(height: Espaco.xs),
          Text('Como calculamos: ${c.referencia}', style: const TextStyle(fontSize: 12, color: Cores.secundario)),
        ]);
      },
    );
  }
}
