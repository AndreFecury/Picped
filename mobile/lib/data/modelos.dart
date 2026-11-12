// Modelos espelham os schemas da API (app/schemas/*.py).

double _d(Object? v) => (v as num).toDouble();
double? _dn(Object? v) => v == null ? null : (v as num).toDouble();
DateTime _dt(Object? v) => DateTime.parse(v as String);

class Usuario {
  Usuario({required this.id, required this.nome, required this.email, required this.criadoEm});
  final int id;
  final String nome;
  final String email;
  final DateTime criadoEm;

  factory Usuario.fromJson(Map<String, dynamic> j) =>
      Usuario(id: j['id'], nome: j['nome'], email: j['email'], criadoEm: _dt(j['criado_em']));

  String get primeiroNome => nome.split(' ').first;
}

class Categoria {
  Categoria({required this.id, required this.nome});
  final int id;
  final String nome;
  factory Categoria.fromJson(Map<String, dynamic> j) => Categoria(id: j['id'], nome: j['nome']);
}

class Produto {
  Produto({
    required this.id,
    required this.nome,
    this.marca,
    required this.unidadeMedida,
    this.codigoBarras,
    required this.categoriaId,
  });
  final int id;
  final String nome;
  final String? marca;
  final String unidadeMedida;
  final String? codigoBarras;
  final int categoriaId;

  factory Produto.fromJson(Map<String, dynamic> j) => Produto(
        id: j['id'],
        nome: j['nome'],
        marca: j['marca'],
        unidadeMedida: j['unidade_medida'],
        codigoBarras: j['codigo_barras'],
        categoriaId: j['categoria_id'],
      );

  String get descricao => [if (marca != null && marca!.isNotEmpty) marca!, 'unidade: $unidadeMedida'].join(' · ');
}

class Supermercado {
  Supermercado({
    required this.id,
    required this.nome,
    required this.cidade,
    required this.bairro,
    this.endereco,
    required this.latitude,
    required this.longitude,
    required this.raioMetros,
    required this.ativo,
  });
  final int id;
  final String nome;
  final String cidade;
  final String bairro;
  final String? endereco;
  final double latitude;
  final double longitude;
  final int raioMetros;
  final bool ativo;

  factory Supermercado.fromJson(Map<String, dynamic> j) => Supermercado(
        id: j['id'],
        nome: j['nome'],
        cidade: j['cidade'],
        bairro: j['bairro'],
        endereco: j['endereco'],
        latitude: _d(j['latitude']),
        longitude: _d(j['longitude']),
        raioMetros: j['raio_metros'],
        ativo: j['ativo'],
      );

  String get local => [bairro, cidade].join(' · ');
}

class SupermercadoProximo {
  SupermercadoProximo({required this.id, required this.nome, required this.distanciaMetros});
  final int id;
  final String nome;
  final int distanciaMetros;
  factory SupermercadoProximo.fromJson(Map<String, dynamic> j) =>
      SupermercadoProximo(id: j['id'], nome: j['nome'], distanciaMetros: j['distancia_metros']);
}

class Oferta {
  Oferta({required this.supermercadoId, required this.supermercadoNome, required this.valor, required this.coletadoEm});
  final int supermercadoId;
  final String supermercadoNome;
  final double valor;
  final DateTime coletadoEm;
  factory Oferta.fromJson(Map<String, dynamic> j) => Oferta(
        supermercadoId: j['supermercado_id'],
        supermercadoNome: j['supermercado_nome'],
        valor: _d(j['valor']),
        coletadoEm: _dt(j['coletado_em']),
      );
}

class Comparacao {
  Comparacao({
    required this.produtoId,
    required this.produtoNome,
    this.menorPreco,
    this.maiorPreco,
    required this.economia,
    required this.economiaPercentual,
    required this.ofertas,
  });
  final int produtoId;
  final String produtoNome;
  final Oferta? menorPreco;
  final Oferta? maiorPreco;
  final double economia;
  final double economiaPercentual;
  final List<Oferta> ofertas;

  factory Comparacao.fromJson(Map<String, dynamic> j) => Comparacao(
        produtoId: j['produto_id'],
        produtoNome: j['produto_nome'],
        menorPreco: j['menor_preco'] == null ? null : Oferta.fromJson(j['menor_preco']),
        maiorPreco: j['maior_preco'] == null ? null : Oferta.fromJson(j['maior_preco']),
        economia: _d(j['economia']),
        economiaPercentual: _d(j['economia_percentual']),
        ofertas: (j['ofertas'] as List).map((e) => Oferta.fromJson(e)).toList(),
      );
}

class PontoHistorico {
  PontoHistorico({required this.valor, required this.coletadoEm, required this.supermercadoNome});
  final double valor;
  final DateTime coletadoEm;
  final String supermercadoNome;
  factory PontoHistorico.fromJson(Map<String, dynamic> j) => PontoHistorico(
      valor: _d(j['valor']), coletadoEm: _dt(j['coletado_em']), supermercadoNome: j['supermercado_nome']);
}

class Historico {
  Historico({
    required this.registros,
    this.minimo,
    this.maximo,
    this.media,
    this.variacaoPercentual,
    required this.pontos,
  });
  final int registros;
  final double? minimo;
  final double? maximo;
  final double? media;
  final double? variacaoPercentual;
  final List<PontoHistorico> pontos;
  factory Historico.fromJson(Map<String, dynamic> j) => Historico(
        registros: j['registros'],
        minimo: _dn(j['minimo']),
        maximo: _dn(j['maximo']),
        media: _dn(j['media']),
        variacaoPercentual: _dn(j['variacao_percentual']),
        pontos: (j['pontos'] as List).map((e) => PontoHistorico.fromJson(e)).toList(),
      );
}

class ListaResumo {
  ListaResumo({required this.id, required this.nome, required this.criadaEm, required this.totalItens});
  final int id;
  final String nome;
  final DateTime criadaEm;
  final int totalItens;
  factory ListaResumo.fromJson(Map<String, dynamic> j) =>
      ListaResumo(id: j['id'], nome: j['nome'], criadaEm: _dt(j['criada_em']), totalItens: j['total_itens']);
}

class ItemLista {
  ItemLista({
    required this.id,
    required this.produtoId,
    required this.quantidade,
    required this.comprado,
    required this.produtoNome,
    this.produtoMarca,
    required this.unidadeMedida,
  });
  final int id;
  final int produtoId;
  final double quantidade;
  final bool comprado;
  final String produtoNome;
  final String? produtoMarca;
  final String unidadeMedida;
  factory ItemLista.fromJson(Map<String, dynamic> j) => ItemLista(
        id: j['id'],
        produtoId: j['produto_id'],
        quantidade: _d(j['quantidade']),
        comprado: j['comprado'],
        produtoNome: j['produto_nome'],
        produtoMarca: j['produto_marca'],
        unidadeMedida: j['unidade_medida'],
      );
}

class Lista {
  Lista({required this.id, required this.nome, required this.criadaEm, required this.itens});
  final int id;
  final String nome;
  final DateTime criadaEm;
  final List<ItemLista> itens;
  factory Lista.fromJson(Map<String, dynamic> j) => Lista(
        id: j['id'],
        nome: j['nome'],
        criadaEm: _dt(j['criada_em']),
        itens: (j['itens'] as List).map((e) => ItemLista.fromJson(e)).toList(),
      );
}

class MercadoTotal {
  MercadoTotal({
    required this.supermercadoId,
    required this.supermercadoNome,
    required this.total,
    required this.itensEncontrados,
    required this.itensFaltando,
    required this.completo,
  });
  final int supermercadoId;
  final String supermercadoNome;
  final double total;
  final int itensEncontrados;
  final int itensFaltando;
  final bool completo;
  factory MercadoTotal.fromJson(Map<String, dynamic> j) => MercadoTotal(
        supermercadoId: j['supermercado_id'],
        supermercadoNome: j['supermercado_nome'],
        total: _d(j['total']),
        itensEncontrados: j['itens_encontrados'],
        itensFaltando: j['itens_faltando'],
        completo: j['completo'],
      );
}

class ComparacaoLista {
  ComparacaoLista({
    required this.totalItens,
    required this.referencia,
    this.melhorOpcao,
    required this.economia,
    required this.economiaPercentual,
    required this.supermercados,
  });
  final int totalItens;
  final String referencia;
  final MercadoTotal? melhorOpcao;
  final double economia;
  final double economiaPercentual;
  final List<MercadoTotal> supermercados;
  factory ComparacaoLista.fromJson(Map<String, dynamic> j) => ComparacaoLista(
        totalItens: j['total_itens'],
        referencia: j['referencia'],
        melhorOpcao: j['melhor_opcao'] == null ? null : MercadoTotal.fromJson(j['melhor_opcao']),
        economia: _d(j['economia']),
        economiaPercentual: _d(j['economia_percentual']),
        supermercados: (j['supermercados'] as List).map((e) => MercadoTotal.fromJson(e)).toList(),
      );
}
