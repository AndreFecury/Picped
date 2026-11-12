import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';
import '../../data/providers.dart';
import '../../shared/servidor_dialogo.dart';
import '../../shared/widgets.dart';

class LoginTela extends ConsumerStatefulWidget {
  const LoginTela({super.key});
  @override
  ConsumerState<LoginTela> createState() => _LoginTelaState();
}

class _LoginTelaState extends ConsumerState<LoginTela> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _senha = TextEditingController();
  bool _enviando = false;
  bool _ocultar = true;

  Future<void> _entrar() async {
    if (!_form.currentState!.validate()) return;
    setState(() => _enviando = true);
    try {
      await ref.read(sessaoProvider.notifier).entrar(_email.text, _senha.text);
    } catch (e) {
      if (mounted) avisar(context, e.toString(), erro: true);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: Cores.branco,
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(Espaco.xl),
              child: Form(
                key: _form,
                child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  const Align(alignment: Alignment.centerLeft, child: Logo(tamanho: 44)),
                  const SizedBox(height: Espaco.xl),
                  Text('Entrar', style: Theme.of(context).textTheme.headlineSmall),
                  const SizedBox(height: Espaco.xs),
                  Text('Compare preços e economize nas suas compras.', style: Theme.of(context).textTheme.bodySmall),
                  const SizedBox(height: Espaco.xl),
                  TextFormField(
                    controller: _email,
                    keyboardType: TextInputType.emailAddress,
                    autofillHints: const [AutofillHints.email],
                    decoration: const InputDecoration(labelText: 'E-mail', prefixIcon: Icon(Icons.mail_outline)),
                    validator: (v) => v == null || !v.contains('@') ? 'Informe um e-mail válido' : null,
                  ),
                  const SizedBox(height: Espaco.m),
                  TextFormField(
                    controller: _senha,
                    obscureText: _ocultar,
                    autofillHints: const [AutofillHints.password],
                    onFieldSubmitted: (_) => _entrar(),
                    decoration: InputDecoration(
                      labelText: 'Senha',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        tooltip: _ocultar ? 'Mostrar senha' : 'Ocultar senha',
                        icon: Icon(_ocultar ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                        onPressed: () => setState(() => _ocultar = !_ocultar),
                      ),
                    ),
                    validator: (v) => v == null || v.isEmpty ? 'Informe a senha' : null,
                  ),
                  const SizedBox(height: Espaco.xl),
                  FilledButton(
                    onPressed: _enviando ? null : _entrar,
                    child: _enviando
                        ? const SizedBox(
                            width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Cores.branco))
                        : const Text('Entrar'),
                  ),
                  const SizedBox(height: Espaco.m),
                  OutlinedButton(onPressed: () => context.push('/cadastro'), child: const Text('Criar conta')),
                  const SizedBox(height: Espaco.xl),
                  Container(
                    padding: const EdgeInsets.all(Espaco.m),
                    decoration: BoxDecoration(color: Cores.cinzaClaro, borderRadius: BorderRadius.circular(raio)),
                    child: const Text(
                      'Conta de demonstração: ana@picped.dev · senha picped123',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 12, color: Cores.secundario),
                    ),
                  ),
                  TextButton.icon(
                    onPressed: () => configurarServidor(context, ref),
                    icon: const Icon(Icons.dns_outlined, size: 18),
                    label: const Text('Configurar servidor'),
                  ),
                ]),
              ),
            ),
          ),
        ),
      );
}
