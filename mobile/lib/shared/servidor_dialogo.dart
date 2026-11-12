import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/theme.dart';
import '../data/api.dart';
import 'widgets.dart';

/// Configura o endereço da API (ex.: http://192.168.0.10:8000 — IP do notebook no mesmo Wi-Fi).
Future<void> configurarServidor(BuildContext context, WidgetRef ref) async {
  final controle = TextEditingController(text: ref.read(urlApiProvider));
  final salvar = await showDialog<bool>(
    context: context,
    builder: (c) => AlertDialog(
      title: const Text('Servidor da API'),
      content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        TextField(
          controller: controle,
          keyboardType: TextInputType.url,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Endereço', hintText: 'http://192.168.0.10:8000'),
        ),
        const SizedBox(height: Espaco.s),
        const Text(
          'No celular, use o IP do computador que roda a API (mesmo Wi-Fi). '
          'No emulador Android, use http://10.0.2.2:8000.',
          style: TextStyle(fontSize: 12, color: Cores.secundario),
        ),
      ]),
      actions: [
        TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancelar')),
        TextButton(onPressed: () => Navigator.pop(c, true), child: const Text('Salvar e testar')),
      ],
    ),
  );
  if (salvar != true) return;
  await ref.read(urlApiProvider.notifier).definir(controle.text);
  try {
    await ref.read(apiProvider).saude();
    if (context.mounted) avisar(context, 'Conectado ao servidor com sucesso.');
  } on ApiException catch (e) {
    if (context.mounted) avisar(context, e.mensagem, erro: true);
  }
}
