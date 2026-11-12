import 'package:flutter/material.dart';

import '../core/theme.dart';
import '../data/api.dart';

class Carregando extends StatelessWidget {
  const Carregando({super.key, this.mensagem});
  final String? mensagem;
  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(Espaco.xl),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const CircularProgressIndicator(color: Cores.verde),
            if (mensagem != null) ...[
              const SizedBox(height: Espaco.m),
              Text(mensagem!, style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center),
            ],
          ]),
        ),
      );
}

/// Estado de erro com tentativa de novo; diferencia "sem conexão" dos demais erros.
class Erro extends StatelessWidget {
  const Erro({super.key, required this.erro, this.aoTentar});
  final Object erro;
  final VoidCallback? aoTentar;
  @override
  Widget build(BuildContext context) {
    final semConexao = erro is ApiException && (erro as ApiException).semConexao;
    return Vazio(
      icone: semConexao ? Icons.wifi_off_rounded : Icons.error_outline_rounded,
      titulo: semConexao ? 'Sem conexão' : 'Algo deu errado',
      mensagem: erro.toString(),
      acao: aoTentar == null ? null : OutlinedButton(onPressed: aoTentar, child: const Text('Tentar de novo')),
      corIcone: semConexao ? Cores.secundario : Cores.erro,
    );
  }
}

class Vazio extends StatelessWidget {
  const Vazio({super.key, required this.icone, required this.titulo, this.mensagem, this.acao, this.corIcone});
  final IconData icone;
  final String titulo;
  final String? mensagem;
  final Widget? acao;
  final Color? corIcone;
  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(Espaco.xl),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Container(
              padding: const EdgeInsets.all(Espaco.l),
              decoration: const BoxDecoration(color: Cores.verdeClaro, shape: BoxShape.circle),
              child: Icon(icone, size: 32, color: corIcone ?? Cores.verdeEscuro),
            ),
            const SizedBox(height: Espaco.l),
            Text(titulo, style: Theme.of(context).textTheme.titleMedium, textAlign: TextAlign.center),
            if (mensagem != null) ...[
              const SizedBox(height: Espaco.s),
              Text(mensagem!, style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center),
            ],
            if (acao != null) ...[const SizedBox(height: Espaco.l), SizedBox(width: 220, child: acao!)],
          ]),
        ),
      );
}

class Secao extends StatelessWidget {
  const Secao(this.titulo, {super.key, this.acao});
  final String titulo;
  final Widget? acao;
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(0, Espaco.xl, 0, Espaco.s),
        child: Row(children: [
          Expanded(child: Text(titulo, style: Theme.of(context).textTheme.titleMedium)),
          ?acao,
        ]),
      );
}

class Etiqueta extends StatelessWidget {
  const Etiqueta(this.texto, {super.key, this.fundo = Cores.verdeClaro, this.cor = Cores.verdeEscuro, this.icone});
  final String texto;
  final Color fundo;
  final Color cor;
  final IconData? icone;
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(color: fundo, borderRadius: BorderRadius.circular(6)),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          if (icone != null) ...[Icon(icone, size: 13, color: cor), const SizedBox(width: 4)],
          Text(texto, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: cor)),
        ]),
      );
}

/// Aviso fixo de que os dados exibidos são de demonstração (não são preços reais).
class AvisoDemo extends StatelessWidget {
  const AvisoDemo({super.key});
  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(Espaco.m),
        decoration: BoxDecoration(color: Cores.alertaClaro, borderRadius: BorderRadius.circular(raio)),
        child: const Row(children: [
          Icon(Icons.info_outline_rounded, size: 18, color: Cores.alerta),
          SizedBox(width: Espaco.s),
          Expanded(
            child: Text(
              'Ambiente de demonstração: lojas e preços iniciais são fictícios. Os preços que você registrar são reais.',
              style: TextStyle(fontSize: 12, color: Cores.alerta, fontWeight: FontWeight.w500),
            ),
          ),
        ]),
      );
}

void avisar(BuildContext context, String texto, {bool erro = false}) {
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(content: Text(texto), backgroundColor: erro ? Cores.erro : Cores.verdeEscuro));
}

/// Logo: "P" com ponto verde (mesmo desenho do ícone do app) + nome.
class Logo extends StatelessWidget {
  const Logo({super.key, this.tamanho = 56, this.claro = false});
  final double tamanho;
  final bool claro;
  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
        Container(
          width: tamanho,
          height: tamanho,
          decoration: BoxDecoration(
            color: claro ? Cores.branco : Cores.verdeEscuro,
            borderRadius: BorderRadius.circular(tamanho * 0.24),
          ),
          child: Stack(children: [
            Center(
              child: Text('P',
                  style: TextStyle(
                      fontSize: tamanho * 0.62,
                      height: 1,
                      fontWeight: FontWeight.w700,
                      color: claro ? Cores.verdeEscuro : Cores.branco)),
            ),
            Positioned(
              right: tamanho * 0.2,
              bottom: tamanho * 0.2,
              child: Container(
                width: tamanho * 0.15,
                height: tamanho * 0.15,
                decoration: const BoxDecoration(color: Cores.verde, shape: BoxShape.circle),
              ),
            ),
          ]),
        ),
        SizedBox(width: tamanho * 0.25),
        Text('Picped',
            style: TextStyle(
                fontSize: tamanho * 0.6, fontWeight: FontWeight.w700, color: claro ? Cores.branco : Cores.verdeEscuro)),
      ]);
}
