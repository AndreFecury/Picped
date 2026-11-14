"""Monta docs/assets/telas.png e docs/assets/swagger.png a partir de capturas reais (PNG).

Uso: python docs/assets/_fonte/galeria.py <pasta-com-capturas>
Capturas esperadas: inicio.png, produto.png, produto2.png, lista.png (390x844 @2x) e swagger.png (1280x900).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pix import ALT, LARG, P, _glifo  # noqa: E402

DESTINO = Path(__file__).resolve().parent.parent
FUNDO, PAINEL, CONTORNO, CORPO, DOURADO, CREME, LILAS = "#20223F", "#2E3160", P["k"], P["d"], P["y"], P["w"], "#7B83C4"


def texto(d: ImageDraw.ImageDraw, txt: str, x: int, y: int, s: int, cor: str, centro: bool = False) -> None:
    txt = txt.upper()
    if centro:
        x -= (len(txt) * (LARG + 1) * s - s) // 2
    for i, ch in enumerate(txt):
        grade, acima, abaixo = _glifo(ch)
        gx = x + i * (LARG + 1) * s
        for marca, oy in ((grade, 0), (acima, -3), (abaixo, ALT)):
            if not marca:
                continue
            for j, linha in enumerate(marca):
                for k, c in enumerate(linha):
                    if c == "#":
                        d.rectangle([gx + k * s, y + (j + oy) * s, gx + (k + 1) * s - 1, y + (j + oy + 1) * s - 1],
                                    fill=cor)


def caixa(d, x, y, w, h, s, fundo, borda):
    """Retângulo com cantos chanfrados (pixel)."""
    d.rectangle([x + s, y, x + w - s - 1, y + h - 1], fill=CONTORNO)
    d.rectangle([x, y + s, x + w - 1, y + h - s - 1], fill=CONTORNO)
    d.rectangle([x + 2 * s, y + s, x + w - 2 * s - 1, y + h - s - 1], fill=borda)
    d.rectangle([x + s, y + 2 * s, x + w - s - 1, y + h - 2 * s - 1], fill=borda)
    d.rectangle([x + 2 * s, y + 2 * s, x + w - 2 * s - 1, y + h - 2 * s - 1], fill=fundo)


def telas(pasta: Path) -> None:
    itens = [("inicio.png", "INÍCIO", "MERCADOS POR DISTÂNCIA"), ("produto.png", "PRODUTO", "ONDE ESTÁ MAIS BARATO"),
             ("produto2.png", "HISTÓRICO", "MÍN · MÉDIA · MÁX"), ("lista.png", "LISTA", "ONDE A LISTA SAI MAIS BARATA")]
    tw, th = 330, 714  # tela (390x844 reduzida)
    borda, gap, mx = 21, 48, 48
    fw, fh = tw + 2 * borda, th + 2 * borda + 42
    W = mx * 2 + 4 * fw + 3 * gap
    H = 48 + fh + 120
    im = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(im)
    for i, (arq, titulo, sub) in enumerate(itens):
        x = mx + i * (fw + gap)
        y = 48
        caixa(d, x, y, fw, fh, 6, CORPO, CORPO)
        d.rectangle([x + fw // 2 - 36, y + 15, x + fw // 2 + 35, y + 20], fill=CONTORNO)  # alto-falante
        tela = Image.open(pasta / arq).convert("RGB").resize((tw, th), Image.LANCZOS)
        d.rectangle([x + borda - 3, y + 36 - 3, x + borda + tw + 2, y + 36 + th + 2], fill=CONTORNO)
        im.paste(tela, (x + borda, y + 36))
        d.rectangle([x + fw // 2 - 18, y + fh - 15, x + fw // 2 + 17, y + fh - 10], fill=CONTORNO)  # botão
        texto(d, titulo, x + fw // 2, y + fh + 24, 4, DOURADO, centro=True)
        texto(d, sub, x + fw // 2, y + fh + 70, 2, LILAS, centro=True)
    im.save(DESTINO / "telas.png", optimize=True)
    print("telas.png", im.size)


def swagger(pasta: Path) -> None:
    shot = Image.open(pasta / "swagger.png").convert("RGB").crop((0, 110, 1280, 610))
    pad = 30
    W, H = shot.width + 2 * pad, shot.height + 2 * pad + 66
    im = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(im)
    caixa(d, 0, 0, W, H, 6, PAINEL, LILAS)
    for i, cor in enumerate((P["r"], P["y"], P["g"])):
        d.rectangle([pad + i * 30, 30, pad + i * 30 + 17, 47], fill=cor)
    texto(d, "LOCALHOST:8000/DOCS", W // 2, 30, 3, CREME, centro=True)
    d.rectangle([pad - 3, 66 + pad - 3 - 6, pad + shot.width + 2, 66 + pad + shot.height + 2 - 6], fill=CONTORNO)
    im.paste(shot, (pad, 66 + pad - 6))
    im.save(DESTINO / "swagger.png", optimize=True)
    print("swagger.png", im.size)


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    telas(pasta)
    swagger(pasta)
