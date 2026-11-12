import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../data/providers.dart';
import '../../shared/servidor_dialogo.dart';
import '../../shared/widgets.dart';

class SplashTela extends ConsumerWidget {
  const SplashTela({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessao = ref.watch(sessaoProvider);
    return Scaffold(
      backgroundColor: Cores.verdeEscuro,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(Espaco.xl),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              const Logo(tamanho: 64, claro: true),
              const SizedBox(height: Espaco.m),
              const Text('Compare mais. Pague menos.',
                  style: TextStyle(color: Cores.verdeClaro, fontSize: 16, fontWeight: FontWeight.w500)),
              const SizedBox(height: Espaco.xxl),
              if (sessao.hasError) ...[
                const Icon(Icons.wifi_off_rounded, color: Cores.verdeClaro),
                const SizedBox(height: Espaco.s),
                Text(sessao.error.toString(),
                    textAlign: TextAlign.center, style: const TextStyle(color: Cores.verdeClaro)),
                const SizedBox(height: Espaco.l),
                FilledButton(onPressed: () => ref.invalidate(sessaoProvider), child: const Text('Tentar de novo')),
                TextButton(
                  onPressed: () async {
                    await configurarServidor(context, ref);
                    ref.invalidate(sessaoProvider);
                  },
                  child: const Text('Configurar servidor', style: TextStyle(color: Cores.branco)),
                ),
              ] else
                const CircularProgressIndicator(color: Cores.verdeClaro),
            ]),
          ),
        ),
      ),
    );
  }
}
