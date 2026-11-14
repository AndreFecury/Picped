import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/formatos.dart' as f;
import '../../core/geo.dart';
import '../../core/theme.dart';
import '../../data/modelos.dart';
import '../../data/providers.dart';
import '../../shared/produto_widgets.dart';
import '../../shared/widgets.dart';

class ProdutoTela extends ConsumerWidget {
  const ProdutoTela({super.key, required this.id});
  final int id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final produto = ref.watch(produtoProvider(id));
    return Scaffold(
      appBar: AppBar(title: const Text('Produto')),
      body: produto.when(
        loading: () => const Carregando(),
        error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(produtoProvider(id))),
        data: (p) => RefreshIndicator(
          color: Cores.verde,
          onRefresh: () async {
            ref.invalidate(comparacaoProvider(id));
            ref.invalidate(historicoProvider(id));
            await ref.read(comparacaoProvider(id).future);
          },
          child: ListView(padding: const EdgeInsets.fromLTRB(Espaco.l, 0, Espaco.l, Espaco.xxl), children: [
            _Cabecalho(produto: p),
            const SizedBox(height: Espaco.m),
            Row(children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => adicionarALista(context, ref, p),
                  icon: const Icon(Icons.playlist_add_rounded),
                  label: const Text('Lista'),
                ),
              ),
              const SizedBox(width: Espaco.m),
              Expanded(
                child: FilledButton.icon(
                  onPressed: () => context.go('/adicionar?produto=${p.id}'),
                  icon: const Icon(Icons.add_rounded),
                  label: const Text('Registrar preço'),
                ),
              ),
            ]),
            const Secao('Onde está mais barato'),
            _Comparacao(produtoId: id),
            const Secao('Histórico de preços'),
            _Historico(produtoId: id),
          ]),
        ),
      ),
    );
  }
}

class _Cabecalho extends ConsumerWidget {
  const _Cabecalho({required this.produto});
  final Produto produto;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final categoria = ref.watch(categoriasProvider).value?.where((c) => c.id == produto.categoriaId).firstOrNull;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Espaco.l),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(color: Cores.verdeClaro, borderRadius: BorderRadius.circular(raio)),
            child: const Icon(Icons.shopping_basket_outlined, color: Cores.verdeEscuro, size: 32),
          ),
          const SizedBox(width: Espaco.l),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(produto.nome, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 18)),
              if (produto.marca != null) Text(produto.marca!, style: const TextStyle(color: Cores.secundario)),
              const SizedBox(height: Espaco.s),
              Wrap(spacing: Espaco.s, runSpacing: Espaco.xs, children: [
                if (categoria != null) Etiqueta(categoria.nome),
                Etiqueta('Vendido por ${produto.unidadeMedida}', fundo: Cores.cinzaClaro, cor: Cores.secundario),
                if (produto.codigoBarras != null)
                  Etiqueta(produto.codigoBarras!,
                      fundo: Cores.cinzaClaro, cor: Cores.secundario, icone: Icons.qr_code_2_rounded),
              ]),
            ]),
          ),
        ]),
      ),
    );
  }
}

class _Comparacao extends ConsumerWidget {
  const _Comparacao({required this.produtoId});
  final int produtoId;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final comp = ref.watch(comparacaoProvider(produtoId));
    final mercados = ref.watch(supermercadosProvider).value ?? const <Supermercado>[];
    final pos = ref.watch(posicaoProvider).value;

    int? distanciaAte(int mercadoId) {
      final m = mercados.where((m) => m.id == mercadoId).firstOrNull;
      if (m == null || pos == null) return null;
      return distanciaMetros(pos.lat, pos.lon, m.latitude, m.longitude);
    }

    return comp.when(
      loading: () => const Padding(padding: EdgeInsets.all(Espaco.xl), child: Carregando()),
      error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(comparacaoProvider(produtoId))),
      data: (c) {
        if (c.ofertas.isEmpty) {
          return Vazio(
            icone: Icons.price_change_outlined,
            titulo: 'Ainda sem preços',
            mensagem: 'Seja o primeiro a registrar o preço deste produto.',
            acao: FilledButton(
              onPressed: () => context.go('/adicionar?produto=$produtoId'),
              child: const Text('Registrar preço'),
            ),
          );
        }
        return Column(children: [
          if (c.ofertas.length >= 2 && c.economia > 0)
            Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: Espaco.m),
              padding: const EdgeInsets.all(Espaco.l),
              decoration: BoxDecoration(color: Cores.verdeEscuro, borderRadius: BorderRadius.circular(raio)),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Economia possível', style: TextStyle(color: Cores.verdeClaro, fontSize: 13)),
                const SizedBox(height: 2),
                Text('${f.moeda(c.economia)}  (${f.percentual(c.economiaPercentual)})',
                    style: const TextStyle(color: Cores.branco, fontSize: 24, fontWeight: FontWeight.w700)),
                const SizedBox(height: Espaco.xs),
                Text(
                  'Comprando no ${c.menorPreco!.supermercadoNome} em vez do ${c.maiorPreco!.supermercadoNome}. '
                  'Referência: preço mais recente registrado em cada mercado.',
                  style: const TextStyle(color: Cores.verdeClaro, fontSize: 12),
                ),
              ]),
            ),
          for (final (i, o) in c.ofertas.indexed) ...[
            _OfertaCard(oferta: o, maisBarata: i == 0, distancia: distanciaAte(o.supermercadoId)),
            const SizedBox(height: Espaco.s),
          ],
        ]);
      },
    );
  }
}

class _OfertaCard extends StatelessWidget {
  const _OfertaCard({required this.oferta, required this.maisBarata, this.distancia});
  final Oferta oferta;
  final bool maisBarata;
  final int? distancia;
  @override
  Widget build(BuildContext context) {
    final antigo = f.desatualizado(oferta.coletadoEm);
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(raio),
        side: BorderSide(color: maisBarata ? Cores.verde : Cores.borda, width: maisBarata ? 1.5 : 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(Espaco.l),
        child: Row(children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(oferta.supermercadoNome, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
              const SizedBox(height: Espaco.xs),
              Text(
                [
                  'Coletado ${f.haQuantoTempo(oferta.coletadoEm)} (${f.data(oferta.coletadoEm)})',
                  if (distancia != null) f.distancia(distancia!),
                ].join(' · '),
                style: const TextStyle(color: Cores.secundario, fontSize: 12),
              ),
              if (maisBarata || antigo) const SizedBox(height: Espaco.s),
              Wrap(spacing: Espaco.s, children: [
                if (maisBarata) const Etiqueta('Menor preço', icone: Icons.check_rounded),
                if (antigo)
                  const Etiqueta('Pode estar desatualizado',
                      fundo: Cores.alertaClaro, cor: Cores.alerta, icone: Icons.schedule_rounded),
              ]),
            ]),
          ),
          Text(f.moeda(oferta.valor),
              style: TextStyle(
                  fontSize: 20, fontWeight: FontWeight.w700, color: maisBarata ? Cores.verde : Cores.texto)),
        ]),
      ),
    );
  }
}

class _Historico extends ConsumerWidget {
  const _Historico({required this.produtoId});
  final int produtoId;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final h = ref.watch(historicoProvider(produtoId));
    return h.when(
      loading: () => const Padding(padding: EdgeInsets.all(Espaco.xl), child: Carregando()),
      error: (e, _) => Erro(erro: e, aoTentar: () => ref.invalidate(historicoProvider(produtoId))),
      data: (h) => h.registros == 0
          ? const Vazio(icone: Icons.show_chart_rounded, titulo: 'Sem histórico ainda')
          : Card(
              child: Padding(
                padding: const EdgeInsets.all(Espaco.l),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Row(children: [
                    _Indicador('Mínimo', f.moeda(h.minimo!)),
                    _Indicador('Média', f.moeda(h.media!)),
                    _Indicador('Máximo', f.moeda(h.maximo!)),
                  ]),
                  if (h.pontos.length >= 2) ...[
                    const SizedBox(height: Espaco.l),
                    SizedBox(height: 90, width: double.infinity, child: CustomPaint(painter: _Grafico(h.pontos))),
                  ],
                  const SizedBox(height: Espaco.m),
                  Text(
                    '${h.registros} registro(s) de ${f.data(h.pontos.first.coletadoEm)} a ${f.data(h.pontos.last.coletadoEm)}'
                    '${h.variacaoPercentual == null ? '' : ' · variação ${h.variacaoPercentual! > 0 ? '+' : ''}${f.percentual(h.variacaoPercentual!)}'}',
                    style: const TextStyle(color: Cores.secundario, fontSize: 12),
                  ),
                  const Text('Calculado só com os preços registrados, em todos os mercados.',
                      style: TextStyle(color: Cores.secundario, fontSize: 12)),
                ]),
              ),
            ),
    );
  }
}

class _Indicador extends StatelessWidget {
  const _Indicador(this.rotulo, this.valor);
  final String rotulo;
  final String valor;
  @override
  Widget build(BuildContext context) => Expanded(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(rotulo, style: const TextStyle(color: Cores.secundario, fontSize: 12)),
          Text(valor, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
        ]),
      );
}

class _Grafico extends CustomPainter {
  _Grafico(this.pontos);
  final List<PontoHistorico> pontos;

  @override
  void paint(Canvas canvas, Size size) {
    final valores = pontos.map((p) => p.valor).toList();
    final mn = valores.reduce(min), mx = valores.reduce(max);
    final faixa = (mx - mn) == 0 ? 1 : (mx - mn);
    final t0 = pontos.first.coletadoEm.millisecondsSinceEpoch.toDouble();
    final dt = max(1.0, pontos.last.coletadoEm.millisecondsSinceEpoch - t0);
    Offset ponto(PontoHistorico p) => Offset(
          (p.coletadoEm.millisecondsSinceEpoch - t0) / dt * size.width,
          size.height - 6 - (p.valor - mn) / faixa * (size.height - 12),
        );
    final linha = Path()..moveTo(ponto(pontos.first).dx, ponto(pontos.first).dy);
    for (final p in pontos.skip(1)) {
      linha.lineTo(ponto(p).dx, ponto(p).dy);
    }
    canvas.drawPath(
        linha,
        Paint()
          ..color = Cores.verde
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2.5
          ..strokeJoin = StrokeJoin.round);
    for (final p in pontos) {
      canvas.drawCircle(ponto(p), 3.5, Paint()..color = Cores.verdeEscuro);
    }
  }

  @override
  bool shouldRepaint(covariant _Grafico old) => old.pontos != pontos;
}
