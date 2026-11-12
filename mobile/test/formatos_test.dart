import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:picped/core/formatos.dart';
import 'package:picped/core/geo.dart';

void main() {
  setUpAll(() => initializeDateFormatting('pt_BR'));

  group('lerValor (entrada de preço)', () {
    test('aceita vírgula e ponto decimal', () {
      expect(lerValor('27,90'), 27.90);
      expect(lerValor('27.90'), 27.90);
      expect(lerValor(r'R$ 1.234,56'), 1234.56);
    });
    test('rejeita vazio e texto inválido', () {
      expect(lerValor(''), isNull);
      expect(lerValor('abc'), isNull);
    });
  });

  test('moeda no formato brasileiro', () {
    expect(moeda(1234.5).replaceAll(' ', ' '), r'R$ 1.234,50');
  });

  test('distância formatada em m e km', () {
    expect(distancia(80), '80 m');
    expect(distancia(1500), '1,5 km');
  });

  test('preço com mais de 30 dias é marcado como desatualizado', () {
    expect(desatualizado(DateTime.now().subtract(const Duration(days: 31))), isTrue);
    expect(desatualizado(DateTime.now().subtract(const Duration(days: 2))), isFalse);
  });

  test('Haversine igual à função SQL da API (ordem de grandeza)', () {
    // ~1 grau de latitude ≈ 111 km
    expect(distanciaMetros(0, 0, 1, 0), closeTo(111195, 50));
    expect(distanciaMetros(-3.03, -59.99, -3.03, -59.99), 0);
  });
}
