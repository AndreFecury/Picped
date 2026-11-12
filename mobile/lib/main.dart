import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/router.dart';
import 'core/theme.dart';
import 'data/api.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Intl.defaultLocale = 'pt_BR';
  await initializeDateFormatting('pt_BR');
  final prefs = await SharedPreferences.getInstance();
  runApp(ProviderScope(
    overrides: [prefsProvider.overrideWithValue(prefs)],
    // sem nova tentativa automática: o usuário vê o erro e decide "Tentar de novo"
    retry: (_, _) => null,
    child: const PicpedApp(),
  ));
}

class PicpedApp extends ConsumerWidget {
  const PicpedApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => MaterialApp.router(
        title: 'Picped',
        debugShowCheckedModeBanner: false,
        theme: temaPicped(),
        routerConfig: ref.watch(routerProvider),
        locale: const Locale('pt', 'BR'),
        supportedLocales: const [Locale('pt', 'BR')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        // na versão web aberta no computador, mantém o layout com largura de celular
        builder: kIsWeb
            ? (context, child) => ColoredBox(
                  color: const Color(0xFFE2E8E4),
                  child: Center(
                    child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 480), child: child),
                  ),
                )
            : null,
      );
}
