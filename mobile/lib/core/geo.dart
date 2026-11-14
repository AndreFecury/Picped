import 'dart:math';

import 'package:geolocator/geolocator.dart';

class LocalizacaoException implements Exception {
  LocalizacaoException(this.mensagem);
  final String mensagem;
  @override
  String toString() => mensagem;
}

/// Pede permissão (se preciso) e devolve a posição atual.
Future<Position> posicaoAtual() async {
  if (!await Geolocator.isLocationServiceEnabled()) {
    throw LocalizacaoException('A localização do celular está desligada. Ative o GPS e tente de novo.');
  }
  var permissao = await Geolocator.checkPermission();
  if (permissao == LocationPermission.denied) {
    permissao = await Geolocator.requestPermission();
  }
  if (permissao == LocationPermission.denied) {
    throw LocalizacaoException('Sem permissão de localização. Você ainda pode escolher o mercado na lista.');
  }
  if (permissao == LocationPermission.deniedForever) {
    throw LocalizacaoException('Localização bloqueada nas configurações do Android. Escolha o mercado na lista.');
  }
  return Geolocator.getCurrentPosition(
    locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, timeLimit: Duration(seconds: 15)),
  );
}

/// Distância em metros entre dois pontos (Haversine) — mesma fórmula da função SQL da API.
int distanciaMetros(double lat1, double lon1, double lat2, double lon2) {
  const r = 6371000.0;
  double rad(double g) => g * pi / 180;
  final dLat = rad(lat2 - lat1);
  final dLon = rad(lon2 - lon1);
  final a = pow(sin(dLat / 2), 2) + cos(rad(lat1)) * cos(rad(lat2)) * pow(sin(dLon / 2), 2);
  return (r * 2 * asin(sqrt(a))).round();
}
