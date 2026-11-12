import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/formatos.dart' as f;
import '../../core/geo.dart';
import '../../core/theme.dart';
import '../../data/modelos.dart';
import '../../data/providers.dart';
import '../../shared/widgets.dart';

class InicioTela extends ConsumerWidget {
  const InicioTela({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usuario = ref.watch(sessaoProvider).value;
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          color: Cores.verde,
          onRefresh: () async {
            ref.invalidate(listasProvider);
            ref.invalidate(supermercadosProvider);
            ref.invalidate(posicaoProvider);
            ref.invalidate(categoriasProvider);
          },
          child: ListView(padding: const EdgeInsets.fromLTRB(Espaco.l, Espaco.l, Espaco.l, Espaco.xxl), children: [
            Row(children: [
              const Logo(tamanho: 32),
              const Spacer(),
              IconButton(
                tooltip: 'Perfil',
                onPressed: () => context.go('/perfil'),
                icon: const Icon(Icons.person_outline_rounded),
              ),
            ]),
            const SizedBox(height: Espaco.l),
            Text('Olá, ${usuario?.primeiroNome ?? ''}!', style: Theme.of(context).textTheme.headlineSmall),
            const Text('Compare mais. Pague menos.', style: TextStyle(color: Cores.secundario)),
            const SizedBox(height: Espaco.l),
            InkWell(
              borderRadius: BorderRadius.circular(raio),
              onTap: () => context.go('/pesquisar'),
              child: const IgnorePointer(
                child: TextField(
                  decoration: InputDecoration(hintText: 'Buscar produto, marca ou código', prefixIcon: Icon(Icons.search)),
                ),
              ),
            ),
            const SizedBox(height: Espaco.m),
            const AvisoDemo(),
            const Secao('Atalhos'),
            Row(children: [
              _Atalho(icone: Icons.add_rounded, texto: 'Registrar\npreço', aoTocar: () => context.go('/adicionar')),
              const SizedBox(width: Espaco.s),
              _Atalho(icone: Icons.qr_code_scanner_rounded, texto: 'Ler\ncódigo', aoTocar: () => context.go('/pesquisar')),
              const SizedBox(width: Espaco.s),
              _Atalho(icone: Icons.checklist_rounded, texto: 'Minhas\nlistas', aoTocar: () => context.go('/listas')),
            ]),
            const Secao('Supermercados perto de você'),
            const _Proximos(),
            Secao('Suas listas',
                acao: TextButton(onPressed: () => context.go('/listas'), child: const Text('Ver todas'))),
            const _ListasRecentes(),
            const Secao('Categorias'),
            const _Categorias(),
          ]),
        ),
      ),
    );
  }
}

class _Atalho extends StatelessWidget {
  const _Atalho({required this.icone, required this.texto, required this.aoTocar});
  final IconData icone;
  final String texto;
  final VoidCallback aoTocar;
  @override
  Widget build(BuildContext context) => Expanded(
        child: Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(raio),
            onTap: aoTocar,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: Espaco.l),
              child: Column(children: [
                Icon(icone, color: Cores.verde),
                const SizedBox(height: Espaco.s),
                Text(texto, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
              ]),
            ),
          ),
        ),
      );
}

class _Proximos extends ConsumerWidget {
  const _Proximos();
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mercados = ref.watch(supermercadosProvider);
    final pos = ref.watch(posicaoProvider);
    return mercados.when(
      loading: () => const Carregando(),
      error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(supermercadosProvider)),
      data: (lista) {
        final ativos = lista.where((m) => m.ativo).toList();
        if (ativos.isEmpty) {
          return const Vazio(icone: Icons.store_outlined, titulo: 'Nenhum supermercado cadastrado');
        }
        final p = pos.value;
        final comDist = [
          for (final m in ativos)
            (m: m, d: p == null ? null : distanciaMetros(p.lat, p.lon, m.latitude, m.longitude)),
        ]..sort((a, b) => (a.d ?? 1 << 30).compareTo(b.d ?? 1 << 30));
        return Column(children: [
          if (p == null && !pos.isLoading)
            const Padding(
              padding: EdgeInsets.only(bottom: Espaco.s),
              child: Text('Ative a localização para ordenar pela distância.',
                  style: TextStyle(fontSize: 12, color: Cores.secundario)),
            ),
          SizedBox(
            height: 104,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: comDist.length,
              separatorBuilder: (_, _) => const SizedBox(width: Espaco.s),
              itemBuilder: (_, i) => _MercadoCard(mercado: comDist[i].m, distancia: comDist[i].d),
            ),
          ),
        ]);
      },
    );
  }
}

class _MercadoCard extends StatelessWidget {
  const _MercadoCard({required this.mercado, this.distancia});
  final Supermercado mercado;
  final int? distancia;
  @override
  Widget build(BuildContext context) => SizedBox(
        width: 180,
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(Espaco.m),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Icon(Icons.storefront_outlined, color: Cores.verde),
              const Spacer(),
              Text(mercado.nome, maxLines: 1, overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.w600)),
              Text(distancia != null ? f.distancia(distancia!) : mercado.bairro,
                  maxLines: 1, overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 12, color: Cores.secundario)),
            ]),
          ),
        ),
      );
}

class _ListasRecentes extends ConsumerWidget {
  const _ListasRecentes();
  @override
  Widget build(BuildContext context, WidgetRef ref) => ref.watch(listasProvider).when(
        loading: () => const Carregando(),
        error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(listasProvider)),
        data: (l) => l.isEmpty
            ? Card(
                child: ListTile(
                  leading: const Icon(Icons.add_rounded, color: Cores.verde),
                  title: const Text('Criar sua primeira lista'),
                  onTap: () => context.go('/listas'),
                ),
              )
            : Column(children: [
                for (final lista in l.take(3))
                  Padding(
                    padding: const EdgeInsets.only(bottom: Espaco.s),
                    child: Card(
                      child: ListTile(
                        leading: const Icon(Icons.checklist_rounded, color: Cores.verdeEscuro),
                        title: Text(lista.nome, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('${lista.totalItens} itens'),
                        trailing: const Icon(Icons.chevron_right_rounded),
                        onTap: () => context.push('/lista/${lista.id}'),
                      ),
                    ),
                  ),
              ]),
      );
}

class _Categorias extends ConsumerWidget {
  const _Categorias();
  @override
  Widget build(BuildContext context, WidgetRef ref) => ref.watch(categoriasProvider).maybeWhen(
        data: (l) => Wrap(spacing: Espaco.s, runSpacing: Espaco.s, children: [
          for (final c in l) ActionChip(label: Text(c.nome), onPressed: () => context.go('/pesquisar')),
        ]),
        orElse: () => const SizedBox.shrink(),
      );
}
