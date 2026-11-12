import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../data/providers.dart';
import '../../shared/widgets.dart';

class CadastroTela extends ConsumerStatefulWidget {
  const CadastroTela({super.key});
  @override
  ConsumerState<CadastroTela> createState() => _CadastroTelaState();
}

class _CadastroTelaState extends ConsumerState<CadastroTela> {
  final _form = GlobalKey<FormState>();
  final _nome = TextEditingController();
  final _email = TextEditingController();
  final _senha = TextEditingController();
  final _confirma = TextEditingController();
  bool _enviando = false;

  Future<void> _criar() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _enviando = true);
    try {
      await ref.read(sessaoProvider.notifier).cadastrar(_nome.text, _email.text, _senha.text);
    } catch (e) {
      if (mounted) avisar(context, e.toString(), erro: true);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: Cores.branco,
        appBar: AppBar(backgroundColor: Cores.branco, title: const Text('Criar conta')),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(Espaco.xl),
            child: Form(
              key: _form,
              child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                TextFormField(
                  controller: _nome,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(labelText: 'Nome', prefixIcon: Icon(Icons.person_outline)),
                  validator: (v) => v == null || v.trim().length < 2 ? 'Informe seu nome' : null,
                ),
                const SizedBox(height: Espaco.m),
                TextFormField(
                  controller: _email,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(labelText: 'E-mail', prefixIcon: Icon(Icons.mail_outline)),
                  validator: (v) =>
                      v == null || !RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(v.trim()) ? 'E-mail inválido' : null,
                ),
                const SizedBox(height: Espaco.m),
                TextFormField(
                  controller: _senha,
                  obscureText: true,
                  decoration: const InputDecoration(
                      labelText: 'Senha', helperText: 'Mínimo de 8 caracteres', prefixIcon: Icon(Icons.lock_outline)),
                  validator: (v) => v == null || v.length < 8 ? 'Use pelo menos 8 caracteres' : null,
                ),
                const SizedBox(height: Espaco.m),
                TextFormField(
                  controller: _confirma,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: 'Confirmar senha', prefixIcon: Icon(Icons.lock_outline)),
                  validator: (v) => v != _senha.text ? 'As senhas não conferem' : null,
                ),
                const SizedBox(height: Espaco.xl),
                FilledButton(
                  onPressed: _enviando ? null : _criar,
                  child: _enviando
                      ? const SizedBox(
                          width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Cores.branco))
                      : const Text('Criar conta'),
                ),
                const SizedBox(height: Espaco.m),
                const Text(
                  'Sua senha é guardada apenas como hash no servidor. Você pode excluir a conta a qualquer momento em Perfil.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, color: Cores.secundario),
                ),
              ]),
            ),
          ),
        ),
      );
}
