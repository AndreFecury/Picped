import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../core/theme.dart';

/// Abre a câmera e devolve o código EAN/GTIN lido (ou null se o usuário voltar).
Future<String?> lerCodigoDeBarras(BuildContext context) =>
    Navigator.of(context).push<String>(MaterialPageRoute(builder: (_) => const _ScannerTela()));

class _ScannerTela extends StatefulWidget {
  const _ScannerTela();
  @override
  State<_ScannerTela> createState() => _ScannerTelaState();
}

class _ScannerTelaState extends State<_ScannerTela> {
  final _controle = MobileScannerController(
    formats: const [BarcodeFormat.ean13, BarcodeFormat.ean8, BarcodeFormat.upcA, BarcodeFormat.upcE],
  );
  bool _lido = false;

  @override
  void dispose() {
    _controle.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          backgroundColor: Colors.black,
          foregroundColor: Cores.branco,
          title: const Text('Ler código de barras', style: TextStyle(color: Cores.branco)),
          actions: [
            IconButton(
              tooltip: 'Lanterna',
              icon: const Icon(Icons.flashlight_on_outlined),
              onPressed: () => _controle.toggleTorch(),
            ),
          ],
        ),
        body: Stack(children: [
          MobileScanner(
            controller: _controle,
            onDetect: (captura) {
              final valor = captura.barcodes.firstOrNull?.rawValue;
              if (_lido || valor == null || !RegExp(r'^[0-9]{8,14}$').hasMatch(valor)) return;
              _lido = true;
              Navigator.of(context).pop(valor);
            },
            errorBuilder: (context, erro) => Center(
              child: Padding(
                padding: const EdgeInsets.all(Espaco.xl),
                child: Text(
                  'Não foi possível abrir a câmera (${erro.errorCode.name}). Verifique a permissão de câmera do app.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Cores.branco),
                ),
              ),
            ),
          ),
          Center(
            child: Container(
              width: 280,
              height: 160,
              decoration: BoxDecoration(
                border: Border.all(color: Cores.verde, width: 3),
                borderRadius: BorderRadius.circular(raio),
              ),
            ),
          ),
          const Positioned(
            left: 0,
            right: 0,
            bottom: 48,
            child: Text('Aponte para o código de barras do produto',
                textAlign: TextAlign.center, style: TextStyle(color: Cores.branco, fontWeight: FontWeight.w500)),
          ),
        ]),
      );
}
