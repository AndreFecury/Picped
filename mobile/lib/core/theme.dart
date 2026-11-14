import 'package:flutter/material.dart';

/// Tokens da identidade visual do Picped.
abstract final class Cores {
  static const verdeEscuro = Color(0xFF063B2E);
  static const verde = Color(0xFF18A34A);
  static const verdeClaro = Color(0xFFE8F5EE);
  static const cinzaClaro = Color(0xFFF4F6F5);
  static const branco = Color(0xFFFFFFFF);
  static const texto = Color(0xFF17211C);
  static const secundario = Color(0xFF68736D);
  static const borda = Color(0xFFE2E8E4);
  static const erro = Color(0xFFB42318);
  static const alerta = Color(0xFFB54708);
  static const alertaClaro = Color(0xFFFEF0C7);
}

abstract final class Espaco {
  static const xs = 4.0;
  static const s = 8.0;
  static const m = 12.0;
  static const l = 16.0;
  static const xl = 24.0;
  static const xxl = 32.0;
}

const raio = 12.0;

ThemeData temaPicped() {
  final esquema = ColorScheme.fromSeed(
    seedColor: Cores.verde,
    primary: Cores.verde,
    onPrimary: Cores.branco,
    secondary: Cores.verdeEscuro,
    surface: Cores.branco,
    onSurface: Cores.texto,
    error: Cores.erro,
  );
  final borda = OutlineInputBorder(
    borderRadius: BorderRadius.circular(raio),
    borderSide: const BorderSide(color: Cores.borda),
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: esquema,
    fontFamily: 'Inter',
    scaffoldBackgroundColor: Cores.cinzaClaro,
    appBarTheme: const AppBarTheme(
      backgroundColor: Cores.cinzaClaro,
      foregroundColor: Cores.texto,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(fontFamily: 'Inter', fontSize: 20, fontWeight: FontWeight.w700, color: Cores.texto),
    ),
    textTheme: const TextTheme(
      headlineSmall: TextStyle(fontWeight: FontWeight.w700, color: Cores.texto),
      titleLarge: TextStyle(fontWeight: FontWeight.w700, color: Cores.texto),
      titleMedium: TextStyle(fontWeight: FontWeight.w600, color: Cores.texto),
      bodyMedium: TextStyle(color: Cores.texto),
      bodySmall: TextStyle(color: Cores.secundario),
      labelLarge: TextStyle(fontWeight: FontWeight.w600),
    ),
    cardTheme: CardThemeData(
      color: Cores.branco,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(raio),
        side: const BorderSide(color: Cores.borda),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Cores.branco,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: borda,
      enabledBorder: borda,
      focusedBorder: borda.copyWith(borderSide: const BorderSide(color: Cores.verde, width: 1.5)),
      errorBorder: borda.copyWith(borderSide: const BorderSide(color: Cores.erro)),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(48),
        backgroundColor: Cores.verde,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(raio)),
        textStyle: const TextStyle(fontFamily: 'Inter', fontWeight: FontWeight.w600, fontSize: 15),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size.fromHeight(48),
        foregroundColor: Cores.verdeEscuro,
        side: const BorderSide(color: Cores.borda),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(raio)),
        textStyle: const TextStyle(fontFamily: 'Inter', fontWeight: FontWeight.w600, fontSize: 15),
      ),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: Cores.branco,
      indicatorColor: Cores.verdeClaro,
      surfaceTintColor: Colors.transparent,
      labelTextStyle: WidgetStateProperty.resolveWith(
        (s) => TextStyle(
          fontFamily: 'Inter',
          fontSize: 12,
          fontWeight: s.contains(WidgetState.selected) ? FontWeight.w600 : FontWeight.w500,
          color: s.contains(WidgetState.selected) ? Cores.verdeEscuro : Cores.secundario,
        ),
      ),
      iconTheme: WidgetStateProperty.resolveWith(
        (s) => IconThemeData(color: s.contains(WidgetState.selected) ? Cores.verdeEscuro : Cores.secundario),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: Cores.branco,
      selectedColor: Cores.verdeClaro,
      side: const BorderSide(color: Cores.borda),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      labelStyle: const TextStyle(fontFamily: 'Inter', color: Cores.texto, fontWeight: FontWeight.w500),
    ),
    dividerTheme: const DividerThemeData(color: Cores.borda, space: 1),
    snackBarTheme: const SnackBarThemeData(behavior: SnackBarBehavior.floating),
  );
}
