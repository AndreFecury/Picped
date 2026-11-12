import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/formatos.dart' as f;
import '../../core/theme.dart';
import '../../data/api.dart';
import '../../data/providers.dart';
import '../../shared/servidor_dialogo.dart';
import '../../shared/widgets.dart';

class PerfilTela extends ConsumerWidget {
  const PerfilTela({super.key});

  Future<void> _excluir(BuildContext context, WidgetRef ref) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Excluir conta?'),
        content: const Text(
            'Sua conta, suas listas e os preços que você registrou serão apagados permanentemente. Não dá para desfazer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancelar')),
          TextButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Excluir conta', style: TextStyle(color: Cores.erro)),
          ),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await ref.read(sessaoProvider.notifier).excluirConta();
    } on ApiException catch (e) {
      if (context.mounted) avisar(context, e.mensagem, erro: true);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final u = ref.watch(sessaoProvider).value;
    final url = ref.watch(urlApiProvider);
    if (u == null) return const Scaffold(body: Carregando());
    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: ListView(padding: const EdgeInsets.fromLTRB(Espaco.l, 0, Espaco.l, Espaco.xxl), children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(Espaco.l),
            child: Row(children: [
              CircleAvatar(
                radius: 28,
                backgroundColor: Cores.verdeClaro,
                child: Text(u.nome.characters.first.toUpperCase(),
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: Cores.verdeEscuro)),
              ),
              const SizedBox(width: Espaco.l),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(u.nome, style: Theme.of(context).textTheme.titleMedium),
                  Text(u.email, style: const TextStyle(color: Cores.secundario)),
                  Text('Membro desde ${f.data(u.criadoEm)}', style: const TextStyle(color: Cores.secundario, fontSize: 12)),
                ]),
              ),
            ]),
          ),
        ),
        const Secao('Configurações'),
        Card(
          child: Column(children: [
            ListTile(
              leading: const Icon(Icons.dns_outlined),
              title: const Text('Servidor da API'),
              subtitle: Text(url),
              trailing: const Icon(Icons.edit_outlined),
              onTap: () => configurarServidor(context, ref),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.location_on_outlined),
              title: const Text('Localização'),
              subtitle: const Text('Usada só para identificar o mercado e mostrar distâncias. Não é armazenada.'),
            ),
          ]),
        ),
        const Secao('Sobre'),
        const Card(
          child: Padding(
            padding: EdgeInsets.all(Espaco.l),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Picped 1.0.0', style: TextStyle(fontWeight: FontWeight.w600)),
              SizedBox(height: Espaco.xs),
              Text(
                'Plataforma colaborativa de comparação de preços. Os preços são registrados pelos próprios usuários '
                'e sempre exibidos com a data da coleta. Lojas e preços iniciais deste ambiente são demonstrativos.',
                style: TextStyle(color: Cores.secundario, fontSize: 13),
              ),
              SizedBox(height: Espaco.s),
              Text('Equipe PSICODE · UNIP Manaus', style: TextStyle(color: Cores.secundario, fontSize: 12)),
            ]),
          ),
        ),
        const SizedBox(height: Espaco.xl),
        OutlinedButton.icon(
          onPressed: () => ref.read(sessaoProvider.notifier).sair(),
          icon: const Icon(Icons.logout_rounded),
          label: const Text('Sair'),
        ),
        const SizedBox(height: Espaco.s),
        TextButton(
          onPressed: () => _excluir(context, ref),
          child: const Text('Excluir minha conta', style: TextStyle(color: Cores.erro)),
        ),
      ]),
    );
  }
}
