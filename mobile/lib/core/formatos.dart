import 'package:intl/intl.dart';

final _moeda = NumberFormat.currency(locale: 'pt_BR', symbol: r'R$');
final _data = DateFormat('dd/MM/yyyy', 'pt_BR');
final _dataHora = DateFormat("dd/MM/yyyy 'às' HH:mm", 'pt_BR');
final _num = NumberFormat.decimalPattern('pt_BR');

String moeda(num valor) => _moeda.format(valor);
String data(DateTime d) => _data.format(d);
String dataHora(DateTime d) => _dataHora.format(d);
String numero(num n) => _num.format(n);
String percentual(num p) => '${NumberFormat('0.0', 'pt_BR').format(p)}%';

String distancia(int metros) =>
    metros < 1000 ? '$metros m' : '${NumberFormat('0.0', 'pt_BR').format(metros / 1000)} km';

/// Preço com mais de 30 dias é sinalizado como desatualizado (nunca mostrado como "atual").
const diasParaDesatualizar = 30;

bool desatualizado(DateTime coletadoEm) => DateTime.now().difference(coletadoEm).inDays > diasParaDesatualizar;

String haQuantoTempo(DateTime d) {
  final dias = DateTime.now().difference(d).inDays;
  if (dias <= 0) return 'hoje';
  if (dias == 1) return 'ontem';
  if (dias < 30) return 'há $dias dias';
  final meses = (dias / 30).floor();
  return meses == 1 ? 'há 1 mês' : 'há $meses meses';
}

/// Converte "27,90" ou "27.90" em número (null se inválido).
double? lerValor(String texto) {
  final t = texto.trim().replaceAll(RegExp(r'[R$\s]'), '');
  if (t.isEmpty) return null;
  final normalizado = t.contains(',') ? t.replaceAll('.', '').replaceAll(',', '.') : t;
  return double.tryParse(normalizado);
}
