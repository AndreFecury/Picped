"""
Motor das artes em pixel art do README (SVG puro, sem dependências).

- fonte bitmap 5x7 própria (com acentos do português);
- sprites desenhados como grades de caracteres -> retângulos agrupados por cor;
- tudo com shape-rendering="crispEdges" para manter os pixels nítidos em qualquer escala.

Uso: python docs/assets/_fonte/gerar.py  (regenera todos os SVGs de docs/assets/)
"""
from __future__ import annotations

import unicodedata

# ---------------------------------------------------------------- paleta
# Mesma base do perfil (tons Sweetie-16) + os verdes da identidade visual do app Picped.
P = {
    "k": "#1A1C2C",  # contorno / quase preto
    "n": "#14152B",  # fundo de tela
    "m": "#29366F",  # azul-noite
    "b": "#3B5DC9",  # azul
    "c": "#41A6F6",  # azul-claro
    "t": "#1D6F86",  # petróleo
    "g": "#16A34A",  # verde Picped
    "G": "#0B3B2E",  # verde-escuro Picped
    "l": "#C9FF7A",  # verde-limão (leds)
    "y": "#F7C873",  # dourado
    "o": "#EF7D57",  # laranja
    "r": "#E5484D",  # vermelho
    "w": "#FFF6D5",  # creme (texto)
    "W": "#FFFFFF",
    "s": "#94B0C2",  # cinza-claro
    "S": "#566C86",  # cinza
    "d": "#333C57",  # cinza-escuro
    "h": "#4A2E16",  # madeira escura
    "H": "#C98E4E",  # madeira clara
    "p": "#F3CDAE",  # pele
    "P": "#DFA986",  # pele sombra
    "u": "#9A7440",  # cabelo
}

# ---------------------------------------------------------------- fonte 5x7
_F = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "|": ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "*": [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."],
    "[": [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."],
    "]": [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."],
    "{": ["...##", "..#..", "..#..", ".#...", "..#..", "..#..", "...##"],
    "}": ["##...", "..#..", "..#..", "...#.", "..#..", "..#..", "##..."],
    "@": [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    "×": [".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."],
    "→": [".....", "..#..", "...#.", "#####", "...#.", "..#..", "....."],
    "✓": [".....", "....#", "...#.", "#.#..", ".#...", ".....", "....."],
}
# marcas de acento (2 linhas acima da letra) e cedilha (1 linha abaixo)
_ACENTO = {
    "́": ["...#.", "..#.."],  # agudo
    "̀": [".#...", "..#.."],  # grave
    "̂": ["..#..", ".#.#."],  # circunflexo
    "̃": [".#.#.", "#.#.."],  # til
}
_CEDILHA = ["..#..", ".#..."]

LARG = 5  # largura da letra em pixels
ALT = 7   # altura da letra em pixels (sem acentos)


def _glifo(ch: str) -> tuple[list[str], list[str] | None, list[str] | None]:
    base = unicodedata.normalize("NFD", ch)
    letra, marcas = base[0], base[1:]
    grade = _F.get(letra.upper(), _F["?"])
    acima = abaixo = None
    for mk in marcas:
        if mk in _ACENTO:
            acima = _ACENTO[mk]
        elif mk == "̧":
            abaixo = _CEDILHA
    return grade, acima, abaixo


class Canvas:
    """Acumula retângulos por cor e devolve <path>s compactos."""

    def __init__(self) -> None:
        # lista de (cor, retângulos): a ordem de desenho é preservada (o que vem depois fica por cima)
        self.camadas: list[tuple[str, list[str]]] = []

    def rect(self, x: float, y: float, w: float, h: float, cor: str) -> None:
        cor = P.get(cor, cor)
        if not self.camadas or self.camadas[-1][0] != cor:
            self.camadas.append((cor, []))
        self.camadas[-1][1].append(f"M{_n(x)} {_n(y)}h{_n(w)}v{_n(h)}h{_n(-w)}z")

    def svg(self, attrs: str = "") -> str:
        return "".join(f'<path {attrs}fill="{c}" d="{"".join(r)}"/>' for c, r in self.camadas)


def _n(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}".rstrip("0")


def largura_texto(texto: str, s: float) -> float:
    return len(texto) * (LARG + 1) * s - s if texto else 0


def texto(cv: Canvas, txt: str, x: float, y: float, s: float, cor: str, sombra: str | None = None,
          alinhar: str = "esq") -> float:
    """Desenha o texto (sempre em maiúsculas) com o topo da letra em y. Devolve a largura."""
    txt = txt.upper()
    w = largura_texto(txt, s)
    if alinhar == "centro":
        x -= w / 2
    elif alinhar == "dir":
        x -= w
    if sombra:
        texto(cv, txt, x + s, y + s, s, sombra)
    for i, ch in enumerate(txt):
        gx = x + i * (LARG + 1) * s
        grade, acima, abaixo = _glifo(ch)
        if acima:
            grade = [linha for linha in grade]
            _pintar(cv, acima, gx, y - 3 * s, s, cor)
            # letras com acento ficam "achatadas" no topo para caber a marca
        _pintar(cv, grade, gx, y, s, cor)
        if abaixo:
            _pintar(cv, abaixo, gx, y + ALT * s, s, cor)
    return w


def _pintar(cv: Canvas, grade: list[str], x: float, y: float, s: float, cor: str) -> None:
    for j, linha in enumerate(grade):
        i = 0
        while i < len(linha):
            if linha[i] == "#":
                k = i
                while k < len(linha) and linha[k] == "#":
                    k += 1
                cv.rect(x + i * s, y + j * s, (k - i) * s, s, cor)
                i = k
            else:
                i += 1


def sprite(cv: Canvas, grade: list[str], x: float, y: float, s: float, mapa: dict[str, str] | None = None) -> None:
    """Grade de caracteres -> pixels. '.' e ' ' são transparentes; cada letra é uma cor da paleta."""
    mapa = mapa or {}
    for j, linha in enumerate(grade):
        i = 0
        while i < len(linha):
            ch = linha[i]
            if ch in ". ":
                i += 1
                continue
            k = i
            while k < len(linha) and linha[k] == ch:
                k += 1
            cv.rect(x + i * s, y + j * s, (k - i) * s, s, mapa.get(ch, ch))
            i = k


def moldura(cv: Canvas, x: float, y: float, w: float, h: float, s: float, fundo: str = "n",
            borda: str = "H", contorno: str = "k", fina: bool = False) -> None:
    """Caixa com cantos chanfrados em pixel (estilo janela de RPG)."""
    e = s * (1 if fina else 2)
    cv.rect(x + s, y, w - 2 * s, h, contorno)
    cv.rect(x, y + s, w, h - 2 * s, contorno)
    cv.rect(x + s + e - s, y + e, w - 2 * e, h - 2 * e, borda)
    cv.rect(x + e, y + s + e - s, w - 2 * e, h - 2 * e, borda)
    cv.rect(x + e + s, y + e + s, w - 2 * e - 2 * s, h - 2 * e - 2 * s, fundo)


ESTILO_BASE = (
    "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
)


def documento(w: int, h: int, corpo: str, rotulo: str, estilo: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{rotulo}">'
        f"<style>{estilo}{ESTILO_BASE}</style>{corpo}</svg>"
    )
