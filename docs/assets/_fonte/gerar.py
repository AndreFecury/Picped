"""Gera os SVGs em pixel art de docs/assets/ (rode: python docs/assets/_fonte/gerar.py)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pix import Canvas, P, documento, largura_texto, moldura, sprite, texto  # noqa: E402

DESTINO = Path(__file__).resolve().parent.parent
P.update({"z": "#20223F", "Z": "#2E3160", "x": "#7B83C4"})

CEU = ["#1B1B3A", "#2A2350", "#3F2A63", "#5E3068", "#8A3A6A", "#B84D63", "#DD6B57", "#F09A5A"]


def sym(metade: list[str]) -> list[str]:
    """Espelha a metade esquerda (ícones simétricos)."""
    return [m + m[::-1] for m in metade]


def salvar(nome: str, conteudo: str) -> None:
    (DESTINO / nome).write_text(conteudo, encoding="utf-8")
    print(f"{nome:28s} {len(conteudo) / 1024:6.1f} KB")


def grupo(cv: Canvas, classe: str = "", extra: str = "") -> str:
    attrs = f' class="{classe}"' if classe else ""
    return f"<g{attrs}{extra}>{cv.svg()}</g>"


# ====================================================================== sprites
CLIENTE = [
    "...uuuu...",
    "..uuuuuu..",
    "..uppppu..",
    "..pkppkp..",
    "..pppppp..",
    "...pPPp...",
    "..tttttt..",
    ".tttttttt.",
    ".ttttttppp",
    ".tttttt...",
    "..tttttt..",
    "..bbbbbb..",
]
PERNAS_A = ["..bb..bb..", "..bb..bb..", "..kk..kk..", ".kkk..kkk."]
PERNAS_B = ["...bbbb...", "...bbbb...", "...kkkk...", "..kkkkkk.."]
CARRINHO = [
    "....yy.rr.gg..",
    "k...yy.rr.ggc.",
    "kkkkkkkkkkkkkk",
    ".kswswswswswk.",
    ".kswswswswswk.",
    "..kswswswswk..",
    "..kkkkkkkkkk..",
    "..k........k..",
    ".kkk......kkk.",
    ".kSk......kSk.",
]
PINO = sym([
    "..kkk",
    ".krrr",
    "krrrr",
    "krrww",
    "krrww",
    "krrrr",
    ".krrr",
    "..krr",
    "...kr",
    "....k",
])
ETIQUETA_FURO = ["kk", "kk"]


# ====================================================================== hero
def hero() -> str:
    W, H = 1200, 440
    estilo = (
        ".tw{animation:tw 2.4s steps(1) infinite}.tw2{animation:tw 3.1s steps(1) .8s infinite}"
        "@keyframes tw{50%{opacity:.15}}"
        ".bl{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}"
        ".bob{animation:bo 1.6s steps(1) infinite}.bob2{animation:bo 1.6s steps(1) .8s infinite}"
        "@keyframes bo{50%{transform:translateY(-6px)}}"
        ".anda{animation:an 14s steps(70) infinite}@keyframes an{from{transform:translateX(-260px)}"
        "to{transform:translateX(560px)}}"
        ".pa{animation:pa .4s steps(1) infinite}.pb{opacity:0;animation:pb .4s steps(1) infinite}"
        "@keyframes pa{50%{opacity:0}}@keyframes pb{50%{opacity:1}}"
    )
    fundo = Canvas()
    fundo.rect(0, 0, W, H, "k")
    for i, cor in enumerate(CEU):
        fundo.rect(0, i * 36, W, 36, cor)
    # sol se pondo atrás da cidade
    for j, (larg, cor) in enumerate([(84, "#F7C873"), (120, "#F7C873"), (144, "#F5B861"), (156, "#F5B861")]):
        fundo.rect(900 - larg / 2 + 150, 222 + j * 6, larg, 6, cor)
    # silhueta da cidade (prédios) ao fundo
    predios = [(600, 210, 48), (654, 186, 36), (696, 234, 60), (1100, 198, 42), (1146, 222, 54), (560, 240, 36)]
    for x, y, w in predios:
        fundo.rect(x, y, w, 300 - y, "#3A2A5C")
        for jy in range(y + 12, 290, 18):
            for jx in range(x + 6, x + w - 6, 12):
                if (jx + jy) % 3:
                    fundo.rect(jx, jy, 6, 6, "#F7C873" if (jx * jy) % 7 < 3 else "#5E3068")
    # mata (floresta) no horizonte
    for x in range(0, W, 6):
        alt = 6 * (2 + ((x * 7) % 5 + (x // 18) % 3) % 4)
        fundo.rect(x, 300 - alt, 6, alt, "#1E3A2F")
    fundo.rect(0, 294, W, 42, "#1E3A2F")
    for x in range(0, W, 30):  # grama
        fundo.rect(x + (x // 30 % 3) * 6, 318, 6, 6, "#2F5A40")

    estrelas_a, estrelas_b = Canvas(), Canvas()
    for i, (x, y) in enumerate([(24, 18), (138, 42), (300, 12), (474, 30), (560, 66), (648, 24), (780, 54),
                                (846, 12), (960, 36), (1062, 18), (1164, 48), (408, 84), (1020, 90), (702, 96)]):
        (estrelas_a if i % 2 else estrelas_b).rect(x, y, 6, 6, "w")

    # ---------------- supermercado (lado direito)
    loja = Canvas()
    x0, x1, topo = 730, 1158, 150
    loja.rect(x0 - 6, topo - 6, x1 - x0 + 12, 336 - topo + 6, "k")
    loja.rect(x0, topo, x1 - x0, 336 - topo, "w")
    loja.rect(x0, topo, x1 - x0, 12, "s")
    # letreiro
    moldura(loja, x0 + 48, topo - 54, x1 - x0 - 96, 60, 6, fundo="G", borda="g")
    texto(loja, "SUPERMERCADO", (x0 + x1) / 2, topo - 33, 3, "w", sombra="k", alinhar="centro")
    # toldo listrado
    for i, x in enumerate(range(x0, x1, 24)):
        cor = "g" if i % 2 == 0 else "W"
        loja.rect(x, topo + 12, 24, 30, cor)
        loja.rect(x + 6, topo + 42, 12, 6, cor)
    loja.rect(x0, topo + 12, x1 - x0, 6, "k")
    # vitrines com prateleiras
    for vx in (x0 + 24, x1 - 168):
        loja.rect(vx - 6, topo + 66, 150, 108, "k")
        loja.rect(vx, topo + 72, 138, 96, "#BFE3F0")
        for k, py in enumerate((topo + 96, topo + 126, topo + 156)):
            loja.rect(vx, py, 138, 6, "H")
            for j in range(8):
                cor = ["r", "y", "g", "c", "o", "b", "r", "y"][(j + k * 3) % 8]
                loja.rect(vx + 6 + j * 16, py - 18, 10, 18, cor)
                loja.rect(vx + 6 + j * 16, py - 18, 10, 4, "k")
    # porta
    px = (x0 + x1) / 2 - 42
    loja.rect(px - 6, topo + 60, 96, 126, "k")
    loja.rect(px, topo + 66, 84, 120, "t")
    loja.rect(px + 39, topo + 66, 6, 120, "k")
    loja.rect(px + 6, topo + 72, 30, 60, "#BFE3F0")
    loja.rect(px + 48, topo + 72, 30, 60, "#BFE3F0")

    # ---------------- chão: calçada + rua
    chao = Canvas()
    chao.rect(0, 336, W, 30, "s")
    for x in range(0, W, 48):
        chao.rect(x, 336, 6, 30, "S")
    chao.rect(0, 336, W, 6, "x")
    chao.rect(0, 366, W, H - 366, "d")
    for x in range(18, W, 96):
        chao.rect(x, 400, 48, 6, "y")
    chao.rect(0, 366, W, 6, "k")

    # ---------------- título e textos
    tit = Canvas()
    texto(tit, "PICPED", 60, 36, 13, "w", sombra="k")
    texto(tit, "COMPARADOR DE PREÇOS", 62, 150, 4, "y", sombra="k")
    texto(tit, "API FASTAPI · POSTGRESQL 16", 62, 192, 3, "w", sombra="k")
    texto(tit, "APP ANDROID EM FLUTTER · MANAUS", 62, 220, 3, "w", sombra="k")
    piscar = Canvas()
    texto(piscar, "> PRESS START", 62, 250, 3, "l", sombra="k")

    # ---------------- etiquetas de preço e pino de GPS sobre a loja
    def etiqueta(cv: Canvas, x: int, y: int, valor: str, cor: str) -> None:
        w = largura_texto(valor, 3) + 30
        moldura(cv, x, y, w, 36, 3, fundo=cor, borda="w", fina=True)
        cv.rect(x + 9, y + 15, 6, 6, "k")
        texto(cv, valor, x + 21, y + 12, 3, "k")

    et1, et2 = Canvas(), Canvas()
    etiqueta(et1, 700, 36, "R$ 28,50", "l")
    etiqueta(et2, 1010, 48, "-13,4%", "y")
    pino = Canvas()
    sprite(pino, PINO, (x0 + x1) / 2 - 30, 18, 6)

    # ---------------- cliente empurrando o carrinho (anda pela calçada)
    pessoa = Canvas()
    sprite(pessoa, CLIENTE, 0, 0, 6)
    sprite(pessoa, CARRINHO, 60, 30, 6)
    pa, pb = Canvas(), Canvas()
    sprite(pa, PERNAS_A, 0, 72, 6)
    sprite(pb, PERNAS_B, 0, 72, 6)

    corpo = (
        fundo.svg()
        + grupo(estrelas_a, "tw") + grupo(estrelas_b, "tw2")
        + loja.svg() + chao.svg() + tit.svg() + grupo(piscar, "bl")
        + grupo(et1, "bob") + grupo(et2, "bob2") + grupo(pino, "bob")
        + '<g transform="translate(120 274)"><g class="anda">'
        + pessoa.svg() + grupo(pa, "pa") + grupo(pb, "pb") + "</g></g>"
    )
    return documento(W, H, corpo, "Picped: comparador de preços de supermercado. Cena pixelada ao pôr do sol em "
                     "Manaus com um supermercado, etiquetas de preço e um cliente empurrando o carrinho.", estilo)


# ====================================================================== ícones de seção (16x16, pixel 3)
ICONES: dict[str, tuple[str, list[str], str]] = {
    "ic-sobre": ("Sobre o projeto", [
        "................",
        "kkk.............",
        ".kk.............",
        "..kkkkkkkkkkkkkk",
        "..kgggggggggggk.",
        "..kgwgwgwgwgwgk.",
        "..kgggggggggggk.",
        "...kgwgwgwgwgk..",
        "...kgggggggggk..",
        "...kkkkkkkkkkk..",
        "....k.......k...",
        "...kkkkkkkkkkk..",
        "................",
        "....kk.....kk...",
        "...kssk...kssk..",
        "....kk.....kk...",
    ], "bob"),
    "ic-telas": ("Telas do app", sym([
        "...kkkkk",
        "..kddddd",
        "..kdkkkk",
        "..kdkggg",
        "..kdkgww",
        "..kdkggg",
        "..kdkgyy",
        "..kdkggg",
        "..kdkgww",
        "..kdkggg",
        "..kdkggg",
        "..kdkkkk",
        "..kddddd",
        "..kdddds",
        "...kkkkk",
        "........",
    ]), "bob"),
    "ic-arquitetura": ("Arquitetura", [
        "................",
        ".kkkkkkkkkkkkkk.",
        ".kgggggggggggggk"[:16],
        ".kgGGGGGGGGGGgk.",
        ".kkkkkkkkkkkkkk.",
        "........k.......",
        ".kkkkkkkkkkkkkk.",
        ".kyyyyyyyyyyyyk.",
        ".kyooooooooooyk.",
        ".kkkkkkkkkkkkkk.",
        "........k.......",
        ".kkkkkkkkkkkkkk.",
        ".kcccccccccccck.",
        ".kcbbbbbbbbbbck.",
        ".kkkkkkkkkkkkkk.",
        "................",
    ], ""),
    "ic-banco": ("Banco de dados", sym([
        "....kkkk",
        "..kkcccc",
        ".kcccccc",
        ".kkccccc",
        ".kbkkkkk",
        ".kbbbbbb",
        ".kbbbbbb",
        ".kkbbbbb",
        ".kbkkkkk",
        ".kbbbbbb",
        ".kbbbbbb",
        ".kkbbbbb",
        ".kbkkkkk",
        "..kkbbbb",
        "....kkkk",
        "........",
    ]), ""),
    "ic-api": ("API", [
        "................",
        "kkkkkkkkkkkkkkkk",
        "kgggggggggrryykk"[:15] + "k",
        "kkkkkkkkkkkkkkkk",
        "knnnnnnnnnnnnnnk",
        "knlnnnnnnnnnnnnk",
        "knnlnnnnnnnnnnnk",
        "knnnlnnnnnnnnnnk",
        "knnlnnnnnnnnnnnk",
        "knlnnnllllnnnnnk",
        "knnnnnnnnnnnnnnk",
        "knnnnnnnnnnnnnnk",
        "kkkkkkkkkkkkkkkk",
        "................",
        "................",
        "................",
    ], ""),
    "ic-regras": ("Regras de negócio", sym([
        ".kkkkkkk",
        ".kgggggg",
        ".kgggggg",
        ".kgggggg",
        ".kgggggg",
        ".kgggggg",
        ".kgggggg",
        ".kgggggg",
        "..kggggg",
        "..kggggg",
        "...kgggg",
        "....kggg",
        ".....kgg",
        "......kk",
        "........",
        "........",
    ]), ""),
    "ic-geo": ("Geolocalização", sym([
        "....kkkk",
        "...krrrr",
        "..krrrrr",
        ".krrrrww",
        ".krrrwww",
        ".krrrwww",
        ".krrrrww",
        "..krrrrr",
        "...krrrr",
        "....krrr",
        ".....krr",
        "......kr",
        ".......k",
        "....dddd",
        "...ddddd",
        "........",
    ]), "bob"),
    "ic-endpoints": ("Endpoints", [
        ".......kk.......",
        ".....kkkkkkkkk..",
        ".....kyyyyyyyyk.",
        ".....kykkykkyyyk",
        ".....kyyyyyyyyk.",
        ".....kkkkkkkkk..",
        "..kkkkkkkk......",
        ".kgggggggk......",
        "kggkkgkkgk......",
        ".kgggggggk......",
        "..kkkkkkkk......",
        ".......kk.......",
        ".......kk.......",
        ".......kk.......",
        ".....dddddd.....",
        "................",
    ], ""),
    "ic-erros": ("Erros", sym([
        ".......k",
        "......ky",
        "......ky",
        ".....kyy",
        ".....kyk",
        "....kyyk",
        "....kyyk",
        "...kyyyk",
        "...kyyyk",
        "..kyyyyy",
        "..kyyyyk",
        ".kyyyyyy",
        ".kkkkkkk",
        "........",
        "........",
        "........",
    ]), "pis"),
    "ic-seguranca": ("Segurança", sym([
        ".....kkk",
        "....kssk",
        "....ks..",
        "....ks..",
        "....ks..",
        "..kkkkkk",
        "..kyyyyy",
        "..kyyyyy",
        "..kyyyyk",
        "..kyyyyk",
        "..kyyyyy",
        "..kooooo",
        "..kkkkkk",
        "........",
        "........",
        "........",
    ]), ""),
    "ic-testes": ("Testes", [
        "......kkkk......",
        "..kkkkkssskkkk..",
        "..kHHkkkkkkHHk..",
        "..kHwwwwwwwwHk..",
        "..kHwgwwkkkwHk..",
        "..kHgwwwwwwwHk..",
        "..kHwwwwwwwwHk..",
        "..kHwgwwkkkwHk..",
        "..kHgwwwwwwwHk..",
        "..kHwwwwwwwwHk..",
        "..kHwgwwkkkwHk..",
        "..kHgwwwwwwwHk..",
        "..kHwwwwwwwwHk..",
        "..kHHHHHHHHHHk..",
        "..kkkkkkkkkkkk..",
        "................",
    ], ""),
    "ic-docker": ("Docker", [
        "................",
        "................",
        "....kkkkkkkk....",
        "....kook..kk....",
        "kkkkkkkkkkkkkkkk",
        "kooooooooooooook"[:15] + "k",
        "kokokokokokokokk"[:15] + "k",
        "kokokokokokokokk"[:15] + "k",
        "kokokokokokokokk"[:15] + "k",
        "kooooooooooooook"[:15] + "k",
        "kkkkkkkkkkkkkkkk",
        "cccccccccccccccc",
        "cbcccbcccbcccbcc",
        "bbbbbbbbbbbbbbbb",
        "................",
        "................",
    ], ""),
    "ic-ci": ("CI/CD", sym([
        ".......k",
        "...kk.ks",
        "...ksksk"[:8],
        "....ksss",
        "..kkssss",
        ".kssskkk",
        ".ksssknn",
        "..kssknn",
        "..kssknn",
        ".ksssknn",
        ".kssskkk",
        "..kkssss",
        "....ksss",
        "...ksksk",
        "...kk.ks",
        ".......k",
    ]), "gira"),
    "ic-rodar": ("Como rodar", [
        "................",
        "................",
        "..kkkkkkkkkkkk..",
        ".kddddddddddddk.",
        "kddkdddddddrddk."[:15] + "k",
        "kdkkkddddddddydk"[:16],
        "kddkddddddrddddk",
        "kddddddddddddydk",
        "kddddsdssddddddk",
        "kdddddddddddddk.",
        ".kddddkkkkddddk.",
        "..kkkk....kkkk..",
        "................",
        "................",
        "................",
        "................",
    ], "bob"),
    "ic-estrutura": ("Estrutura", [
        "................",
        "................",
        ".kkkkk..........",
        "kyyyyyk.........",
        "kyyyyyykkkkkkkk.",
        "kyyyyyyyyyyyyyyk",
        "kokkkkkkkkkkkkkk",
        "koyyyyyyyyyyyyyk",
        "koyyyyyyyyyyyyyk",
        "koyyyyyyyyyyyyyk",
        "koyyyyyyyyyyyyyk",
        "koyyyyyyyyyyyyyk",
        "kkkkkkkkkkkkkkkk",
        "................",
        "................",
        "................",
    ], ""),
    "ic-dados": ("Dados", [
        "................",
        "............kk..",
        "...........kllk.",
        "............kk..",
        "..........kkkk..",
        "..........kggk..",
        "......kkkkkggk..",
        "......kyykkggk..",
        "..kkkkkyykkggk..",
        "..kcckkyykkggk..",
        "..kcckkyykkggk..",
        "..kcckkyykkggk..",
        "kkkkkkkkkkkkkkkk",
        "................",
        "................",
        "................",
    ], ""),
    "ic-equipe": ("Equipe", [
        "................",
        "..kkkk....kkkk..",
        ".kuuuuk..kkkkkk.",
        ".kppppk..kppppk.",
        ".kpkpkk..kkpkpk."[:16],
        ".kppppk..kppppk.",
        "..kppk....kppk..",
        ".kttttk..kggggk.",
        "kttttttkkggggggk",
        "kttttttkkggggggk",
        "kptttpkk.kpggpk."[:16],
        ".kttttk..kggggk.",
        ".kbkkbk..kbkkbk.",
        ".kk..kk..kk..kk.",
        "................",
        "................",
    ], ""),
    "ic-roadmap": ("Próximos passos", [
        "................",
        "..kkkkkkkkkk....",
        "..klrrrrrrrrk...",
        "..klrrrrrrrrrk..",
        "..klrrwwrrrrrk..",
        "..klrrrrrrrrk...",
        "..klkkkkkkkk....",
        "..kl............",
        "..kl............",
        "..kl............",
        "..kl............",
        "..kl............",
        ".kkkk...........",
        "kddddk..........",
        "................",
        "................",
    ], ""),
}

ESTILO_ICONE = (
    ".bob{animation:bo 1.4s steps(1) infinite}@keyframes bo{50%{transform:translateY(-3px)}}"
    ".pis{animation:pi 1.2s steps(1) infinite}@keyframes pi{50%{opacity:.55}}"
)


def icone(nome: str) -> str:
    rotulo, grade, anim = ICONES[nome]
    for linha in grade:
        assert len(linha) == 16, (nome, linha, len(linha))
    assert len(grade) == 16, nome
    cv = Canvas()
    sprite(cv, grade, 3, 3, 3)
    extra = Canvas()
    if nome == "ic-regras":  # check em cima do escudo
        sprite(extra, ["......w", ".....ww", "w...ww.", "ww.ww..", ".www...", "..w...."], 4 * 3 + 3, 4 * 3 + 3, 3)
    if nome == "ic-erros":
        sprite(extra, ["k", "k", "k", "k", ".", "k"], 7 * 3 + 3 + 1.5, 4 * 3 + 3, 3)
    corpo = grupo(cv, anim if anim in ("bob", "pis") else "") + extra.svg()
    return documento(54, 54, corpo, rotulo, ESTILO_ICONE)


LOGO = [
    "..GGGGGGGGGGGG..",
    ".GGGGGGGGGGGGGG.",
    "GGGGGGGGGGGGGGGG",
    "GGGWWWWWWGGGGGGG",
    "GGGWWWWWWWWGGGGG",
    "GGGWWGGGGWWWGGGG",
    "GGGWWGGGGGWWGGGG",
    "GGGWWGGGGWWWGGGG",
    "GGGWWWWWWWWGGGGG",
    "GGGWWWWWWWGGGGGG",
    "GGGWWGGGGGGGGGGG",
    "GGGWWGGGGGGGGGGG",
    "GGGWWGGGGGGggGGG",
    "GGGWWGGGGGGggGGG",
    ".GGGGGGGGGGGGGG.",
    "..GGGGGGGGGGGG..",
]


# ====================================================================== ficha técnica
def ficha(endpoints: int, testes: int) -> str:
    W, H = 1200, 572
    estilo = (
        ".hb{animation:hb 1.2s steps(2) infinite}@keyframes hb{50%{opacity:.2}}"
        ".f1,.f2{animation:fl 2.4s steps(24) backwards}.f2{animation-delay:.6s}"
        "@keyframes fl{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}"
    )
    cv = Canvas()
    moldura(cv, 0, 0, W, H, 6, fundo="z", borda="z")
    # retrato com o logo do app
    moldura(cv, 24, 24, 300, 300, 6, fundo="Z", borda="y")
    sprite(cv, LOGO, 78, 78, 12)
    texto(cv, "PICPED API", 174, 348, 4, "y", alinhar="centro")
    on = Canvas()
    texto(on, "ONLINE", 174, 384, 3, "l", alinhar="centro")
    texto(cv, "V0.3.0", 174, 414, 2, "x", alinhar="centro")

    linhas = [
        ("CLASSE", "API REST + APP ANDROID"),
        ("LINGUAGENS", "PYTHON 3.12 · DART 3.14"),
        ("BANCO", "POSTGRESQL 16 · ATÉ A 3FN"),
        ("INFRA", "DOCKER COMPOSE · GITLAB CI"),
        ("GUILDA", "PSICODE · UNIP MANAUS"),
    ]
    y = 36
    for rot, val in linhas:
        texto(cv, rot, 360, y, 3, "x")
        texto(cv, val, 360, y + 27, 4, "w")
        y += 72

    # barras de progresso (preenchem ao abrir)
    def barra(y: int, rotulo: str, direita: str) -> None:
        texto(cv, rotulo, 360, y, 3, "x")
        texto(cv, direita, W - 30, y, 3, "x", alinhar="dir")
        moldura(cv, 360, y + 27, W - 390, 30, 3, fundo="n", borda="x", fina=True)

    barra(404, "TESTES AUTOMATIZADOS", f"{testes} / {testes} PASSANDO")
    barra(480, "ETAPAS DA DISCIPLINA", "7 / 7 ENTREGUES")
    b1, b2 = Canvas(), Canvas()
    b1.rect(369, 440, W - 408, 12, "g")
    b2.rect(369, 516, W - 408, 12, "y")

    # contadores no rodapé
    cont = Canvas()
    for i, (num, rot) in enumerate([(str(endpoints), "ENDPOINTS"), ("7", "TABELAS")]):
        centro = (102, 252)[i]
        texto(cont, num, centro, 470, 5, "y", alinhar="centro")
        texto(cont, rot, centro, 512, 2, "w", alinhar="centro")
    moldura(cv, 24, 450, 300, 96, 3, fundo="Z", borda="x", fina=True)

    corpo = (cv.svg() + grupo(on, "hb") + grupo(b1, "f1") + grupo(b2, "f2") + cont.svg())
    # recorta a altura útil
    return documento(W, H, corpo, f"Ficha técnica: API REST em Python 3.12 com FastAPI e PostgreSQL 16, app Android "
                     f"em Flutter, {endpoints} endpoints, {testes} testes passando, 7 tabelas.", estilo)


# ====================================================================== arquitetura
def arquitetura() -> str:
    W, H = 1200, 620
    estilo = (
        ".ida{animation:ida 3.2s steps(32) infinite}@keyframes ida{from{transform:translateX(0)}"
        "to{transform:translateX(936px)}}"
        ".volta{animation:volta 3.2s steps(32) 1.6s infinite}@keyframes volta{from{transform:translateX(936px)}"
        "to{transform:translateX(0)}}"
        ".hb{animation:hb 1.2s steps(2) infinite}@keyframes hb{50%{opacity:.25}}"
    )
    cv = Canvas()
    moldura(cv, 0, 0, W, H, 6, fundo="z", borda="z")
    texto(cv, "ARQUITETURA EM CAMADAS", W / 2, 30, 4, "y", sombra="k", alinhar="centro")
    texto(cv, "CADA CAMADA SÓ CONHECE A DE BAIXO", W / 2, 76, 2, "x", alinhar="centro")

    caixas = [
        ("CLIENTES", "c", ["APP FLUTTER", "SWAGGER /DOCS", "WEB /APP"]),
        ("ROUTERS", "g", ["FASTAPI", "PYDANTIC V2", "401 403 422"]),
        ("SERVICES", "y", ["REGRAS DE", "NEGÓCIO", "GPS E PREÇOS"]),
        ("DAO / SQL", "o", ["REPOSITORIES", "SQL PARAMETR.", "POOL CONEXÕES"]),
        ("POSTGRES", "b", ["7 TABELAS", "FUNÇÃO GEO", "ÍNDICES · 3FN"]),
    ]
    larg, gap, x0, topo, alt = 196, 44, 20, 150, 236
    for i, (tit, cor, linhas) in enumerate(caixas):
        x = x0 + i * (larg + gap)
        moldura(cv, x, topo, larg, alt, 6, fundo="Z", borda=cor)
        cv.rect(x + 12, topo + 12, larg - 24, 42, cor)
        texto(cv, tit, x + larg / 2, topo + 24, 3, "k", alinhar="centro")
        for j, ln in enumerate(linhas):
            texto(cv, ln, x + larg / 2, topo + 84 + j * 42, 2, "w", alinhar="centro")
        if i < len(caixas) - 1:  # setas (ida em cima, volta embaixo)
            ax = x + larg
            for k in range(0, gap - 6, 9):
                cv.rect(ax + 3 + k, topo + 96, 6, 6, "x")
                cv.rect(ax + 3 + k, topo + 156, 6, 6, "x")
            cv.rect(ax + gap - 12, topo + 90, 6, 18, "x")
            cv.rect(ax + 6, topo + 150, 6, 18, "x")
    ida, volta = Canvas(), Canvas()
    ida.rect(x0 + larg - 3, topo + 93, 12, 12, "l")
    volta.rect(x0 + larg - 3, topo + 153, 12, 12, "y")
    # legenda
    cv.rect(W / 2 - 300, 110, 12, 12, "l")
    texto(cv, "REQUISIÇÃO", W / 2 - 276, 109, 2, "w")
    cv.rect(W / 2 + 30, 110, 12, 12, "y")
    texto(cv, "RESPOSTA JSON / ERRO", W / 2 + 54, 109, 2, "w")

    # base: core + domain
    by = 446
    moldura(cv, 20, by, 712, 150, 6, fundo="Z", borda="x")
    texto(cv, "CORE", 48, by + 24, 3, "x")
    for j, ln in enumerate(["CONFIG VIA .ENV · POOL SQLALCHEMY", "ERROS PADRONIZADOS · TOKEN HMAC-SHA256",
                            "HASH PBKDF2 · CORS · HEALTHCHECK"]):
        texto(cv, ln, 48, by + 58 + j * 24, 2, "w")
    moldura(cv, 756, by, 424, 150, 6, fundo="Z", borda="x")
    texto(cv, "DOMAIN", 780, by + 24, 3, "x")
    for j, ln in enumerate(["ENTIDADES PURAS (DATACLASSES)", "SEM FRAMEWORK E SEM SQL"]):
        texto(cv, ln, 780, by + 58 + j * 24, 2, "w")
    # ligações pontilhadas da base até as caixas
    for xi in (1, 2, 3):
        cx = x0 + xi * (larg + gap) + larg / 2 - 3
        for yy in range(topo + alt + 6, by - 6, 12):
            if not (xi == 2 and topo + alt + 6 <= yy <= topo + alt + 36):
                cv.rect(cx, yy, 6, 6, "S")
    corpo = cv.svg() + grupo(ida, "ida") + grupo(volta, "volta")
    return documento(W, H, corpo, "Arquitetura em camadas: clientes (app Flutter, Swagger, web) chamam os routers "
                     "FastAPI com schemas Pydantic, que chamam os services com as regras de negócio, que usam os "
                     "repositories com SQL parametrizado sobre o PostgreSQL. Core e Domain dão suporte.", estilo)


# ====================================================================== regra de GPS
def geo() -> str:
    W, H = 1200, 460
    estilo = (
        ".hb{animation:hb 1.2s steps(2) infinite}@keyframes hb{50%{opacity:.25}}"
        ".bob{animation:bo 1.4s steps(1) infinite}.bob2{animation:bo 1.4s steps(1) .7s infinite}"
        "@keyframes bo{50%{transform:translateY(-6px)}}"
    )
    cv = Canvas()
    moldura(cv, 0, 0, W, H, 6, fundo="z", borda="z")
    # mapa
    mx, my, mw, mh = 24, 24, 552, 412
    moldura(cv, mx, my, mw, mh, 6, fundo="#2D5A3D", borda="y")
    for x in range(mx + 66, mx + mw - 12, 120):
        cv.rect(x, my + 12, 24, mh - 24, "S")
    for y in range(my + 54, my + mh - 12, 110):
        cv.rect(mx + 12, y, mw - 24, 24, "S")
    for x in range(mx + 18, mx + mw - 24, 30):
        for y in range(my + 18, my + mh - 24, 30):
            if (x * 3 + y) % 7 == 0:
                cv.rect(x, y, 6, 6, "#3E7A50")
    cx, cy = mx + 278, my + 214
    # anel do raio (pixels sobre a circunferência)
    anel = Canvas()
    r = 108
    pts = set()
    for k in range(0, 360, 3):
        px = round((cx + r * math.cos(math.radians(k))) / 6) * 6
        py = round((cy + r * math.sin(math.radians(k))) / 6) * 6
        pts.add((px, py))
    for px, py in sorted(pts):
        if (px + py) // 6 % 2 == 0:
            anel.rect(px - 3, py - 3, 6, 6, "l")
    # mercado no centro
    loja = [
        "kkkkkkkkkkkk",
        "kgWgWgWgWgWk",
        "kkkkkkkkkkkk",
        "kwwwwwwwwwwk",
        "kwcckwwkccwk",
        "kwcckwwkccwk",
        "kwwwkttkwwwk",
        "kkkkkkkkkkkk",
    ]
    sprite(cv, loja, cx - 36, cy - 24, 6)
    texto(cv, "RAIO 80 M", cx, cy + 34, 2, "w", sombra="k", alinhar="centro")
    pa, pb = Canvas(), Canvas()
    pino_g = [linha.replace("r", "g") for linha in PINO]
    sprite(pa, pino_g, cx - 72, cy - 84, 4)
    moldura(pa, cx - 142, cy - 130, 180, 36, 3, fundo="g", borda="w", fina=True)
    texto(pa, "20 M → 201", cx - 52, cy - 118, 2, "k", alinhar="centro")
    sprite(pb, PINO, cx + 140, cy - 150, 4)
    moldura(pb, cx + 70, cy - 196, 180, 36, 3, fundo="r", borda="w", fina=True)
    texto(pb, "120 M → 422", cx + 160, cy - 184, 2, "w", alinhar="centro")

    # explicação
    tx = 612
    texto(cv, "VALIDAÇÃO POR GPS", tx, 40, 4, "y", sombra="k")
    passos = [
        ("1", "APP LÊ O GPS DO CELULAR"),
        ("2", "/SUPERMERCADOS/PROXIMOS"),
        ("", "HAVERSINE DENTRO DO BANCO"),
        ("3", "POST /PRECOS COM DISTÂNCIA"),
        ("4", "SERVICE COMPARA COM O RAIO"),
    ]
    y = 104
    for n, t in passos:
        if n:
            moldura(cv, tx, y - 6, 30, 30, 3, fundo="y", borda="y", fina=True)
            texto(cv, n, tx + 15, y + 2, 2, "k", alinhar="centro")
        texto(cv, t, tx + 48, y + 2, 2, "w")
        y += 42
    moldura(cv, tx, 330, 270, 102, 6, fundo="G", borda="g")
    texto(cv, "DENTRO DO RAIO", tx + 135, 352, 2, "w", alinhar="centro")
    texto(cv, "201", tx + 135, 384, 4, "l", alinhar="centro")
    moldura(cv, tx + 294, 330, 270, 102, 6, fundo="#4A1C24", borda="r")
    texto(cv, "FORA DO RAIO", tx + 429, 352, 2, "w", alinhar="centro")
    texto(cv, "422", tx + 429, 384, 4, "r", alinhar="centro")
    corpo = cv.svg() + grupo(anel, "hb") + grupo(pa, "bob") + grupo(pb, "bob2")
    return documento(W, H, corpo, "Validação por GPS: o preço só é aceito se o usuário estiver dentro do raio do "
                     "supermercado (a 20 m, dentro do raio de 80 m retorna 201; 120 m retorna 422).", estilo)


# ====================================================================== ranking da lista
def ranking() -> str:
    W, H = 1200, 430
    estilo = (
        ".f1,.f2,.f3,.f4{animation:fl 1.6s steps(16) backwards}"
        ".f2{animation-delay:.3s}.f3{animation-delay:.6s}.f4{animation-delay:.9s}"
        "@keyframes fl{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}"
        ".bob{animation:bo 1.4s steps(1) infinite}@keyframes bo{50%{transform:translateY(-4px)}}"
    )
    cv = Canvas()
    moldura(cv, 0, 0, W, H, 6, fundo="z", borda="z")
    texto(cv, "ONDE A LISTA SAI MAIS BARATA", 30, 30, 4, "y", sombra="k")
    texto(cv, "LISTA: COMPRAS DO MÊS · 4 ITENS · DADOS DEMONSTRATIVOS", 30, 76, 2, "x")
    linhas = [
        ("ATACADÃO", "R$ 161,15", "4/4", 161.15, "g", True),
        ("CARVALHO", "R$ 178,53", "4/4", 178.53, "y", True),
        ("SUPER MAIS", "R$ 89,38", "2/4", 89.38, "S", False),
        ("DB", "R$ 136,48", "2/4", 136.48, "S", False),
    ]
    barras = [Canvas() for _ in linhas]
    y = 120
    bx, bw = 300, 500
    for i, (nome, valor, itens, v, cor, completo) in enumerate(linhas):
        texto(cv, nome, 66, y + 12, 3, "w")
        moldura(cv, bx, y, bw, 42, 3, fundo="n", borda="d", fina=True)
        barras[i].rect(bx + 6, y + 6, (bw - 12) * v / 180, 30, cor)
        texto(cv, valor, bx + bw + 24, y + 12, 3, "w" if completo else "s")
        texto(cv, itens if completo else itens + " PARCIAL", W - 30, y + 14, 2, "l" if completo else "o",
              alinhar="dir")
        y += 66
    coroa = Canvas()
    sprite(coroa, ["y.y.y", "yyyyy", "yyyyy"], 30, 130, 4)
    moldura(cv, 30, 386 - 18, W - 60, 48, 3, fundo="G", borda="g", fina=True)
    texto(cv, "ECONOMIA POTENCIAL: R$ 17,38 (9,7%) · PARCIAIS NÃO ENTRAM NA CONTA", W / 2, 382, 2, "w",
          alinhar="centro")
    corpo = cv.svg() + "".join(grupo(b, f"f{i + 1}") for i, b in enumerate(barras)) + grupo(coroa, "bob")
    return documento(W, H, corpo, "Ranking da lista Compras do mês: Atacadão R$ 161,15 com todos os itens é a melhor "
                     "opção; Carvalho R$ 178,53; Super Mais (R$ 89,38) e DB (R$ 136,48) têm só 2 de 4 itens "
                     "e ficam como parciais. "
                     "Economia potencial de R$ 17,38 (9,7%).", estilo)


# ====================================================================== botões da equipe
def botao(nome: str, sub: str, cor: str, cor_sub: str = "k") -> str:
    W, H = 380, 112
    estilo = ".cur{animation:sp 1s steps(2) infinite}@keyframes sp{50%{opacity:0}}"
    cv = Canvas()
    cv.rect(6, 12, W - 6, H - 12, "k")
    moldura(cv, 0, 0, W - 6, H - 12, 6, fundo=cor, borda=cor)
    texto(cv, nome, 54, 24, 3, "w", sombra="k")
    texto(cv, sub, 54, 62, 2, cor_sub)
    cur = Canvas()
    texto(cur, ">", 24, 24, 3, "l", sombra="k")
    return documento(W, H, cv.svg() + grupo(cur, "cur"), f"{nome}: {sub}", estilo)


if __name__ == "__main__":
    salvar("hero.svg", hero())
    for nome in ICONES:
        salvar(f"{nome}.svg", icone(nome))
    salvar("ficha.svg", ficha(endpoints=int(sys.argv[1]) if len(sys.argv) > 1 else 46,
                              testes=int(sys.argv[2]) if len(sys.argv) > 2 else 135))
    salvar("arquitetura.svg", arquitetura())
    salvar("geo.svg", geo())
    salvar("ranking.svg", ranking())
    salvar("btn-andre.svg", botao("ANDRÉ FECURY", "GITHUB @ANDREFECURY", "t"))
    salvar("btn-san.svg", botao("LUÍS SAN MARTIN", "GITHUB @OSAN-MARTIN", "G", "l"))
    salvar("btn-luiz.svg", botao("LUIZ FECURY", "EQUIPE PSICODE", "m", "s"))
