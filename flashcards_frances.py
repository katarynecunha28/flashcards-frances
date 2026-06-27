"""
╔══════════════════════════════════════════════════════════════════════╗
║              GERADOR DE FLASHCARDS DE FRANCÊS EM PDF                 ║
║                                                                      ║
║  Dependências:  pip install reportlab qrcode[pil] Pillow cairosvg    ║
║                                                                      ║
║  Como usar:                                                          ║
║    1. Edite a lista WORDS com suas palavras e imagens                ║
║    2. Coloque as imagens na pasta indicada em IMG_DIR                ║
║    3. Execute:  python flashcards_frances.py                         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import io
import math
import qrcode

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage


# ══════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÕES GERAIS — mexa aqui para mudar aparência e layout
# ══════════════════════════════════════════════════════════════════════

# Pasta onde estão as imagens dos cards (use "/" no final)
IMG_DIR = "C:/caminho/da/pasta/imagens"

# Arquivo de saída
OUTPUT_PDF = "flashcards_frances.pdf"

# Número de colunas e linhas por página
COLS = 3
ROWS = 3  # COLS × ROWS = cards por página (aqui: 9)

# Margens da página e espaço entre cards (em milímetros)
MARGIN_X = 10 * mm   # margem esquerda e direita
MARGIN_Y = 12 * mm   # margem superior e inferior
GAP_X    =  5 * mm   # espaço horizontal entre cards
GAP_Y    =  5 * mm   # espaço vertical entre cards
HEADER_H =  7 * mm   # altura reservada para o cabeçalho da página

# Tamanho de cada card (calculado automaticamente a partir das margens)
PAGE_W, PAGE_H = A4
CARD_W = (PAGE_W - 2 * MARGIN_X - (COLS - 1) * GAP_X) / COLS
CARD_H = (PAGE_H - 2 * MARGIN_Y - HEADER_H - (ROWS - 1) * GAP_Y) / ROWS


# ══════════════════════════════════════════════════════════════════════
#  PALETAS DE CORES
#  Cada paleta tem três cores em formato RGB de 0.0 a 1.0:
#    "bg"  → cor de fundo do card
#    "top" → cor da barra superior e detalhes
#    "txt" → cor do texto principal (palavra em francês)
# ══════════════════════════════════════════════════════════════════════

PALETTES = [
    {"bg": (1.00, 0.94, 0.85), "top": (0.85, 0.28, 0.08), "txt": (0.60, 0.14, 0.02)},  # 0: laranja (Animais)
    {"bg": (0.88, 0.96, 0.88), "top": (0.15, 0.55, 0.25), "txt": (0.05, 0.35, 0.10)},  # 1: verde (Comidas)
    {"bg": (0.87, 0.93, 1.00), "top": (0.12, 0.38, 0.80), "txt": (0.05, 0.18, 0.60)},  # 2: azul (Lugares)
    {"bg": (0.99, 0.88, 0.93), "top": (0.75, 0.12, 0.42), "txt": (0.52, 0.03, 0.25)},  # 3: rosa (Cores)
    {"bg": (0.94, 0.88, 1.00), "top": (0.46, 0.15, 0.72), "txt": (0.30, 0.03, 0.52)},  # 4: roxo (Números)
    {"bg": (0.84, 0.96, 0.97), "top": (0.02, 0.52, 0.60), "txt": (0.01, 0.32, 0.42)},  # 5: ciano
    {"bg": (0.98, 0.95, 0.82), "top": (0.62, 0.42, 0.10), "txt": (0.42, 0.25, 0.02)},  # 6: dourado
    {"bg": (0.97, 0.88, 0.97), "top": (0.60, 0.08, 0.60), "txt": (0.42, 0.02, 0.42)},  # 7: magenta
    {"bg": (0.88, 0.97, 0.93), "top": (0.05, 0.50, 0.35), "txt": (0.02, 0.32, 0.22)},  # 8: esmeralda
]


# ══════════════════════════════════════════════════════════════════════
#  LISTA DE PALAVRAS (VOCABULÁRIO)
# ══════════════════════════════════════════════════════════════════════

I = IMG_DIR  # atalho para não repetir o caminho toda vez

WORDS = [
    # ── Animais (Índices gerais: 0 até 5) ────────────────────────────
    (I + "img_chat.png",      "le chat",     "o gato",       "luh sha"),
    (I + "img_chien.png",    "le chien",    "o cachorro",   "luh shyeh"),
    (I + "img_oiseau.png",   "l'oiseau",    "o passaro",    "lwah-ZO"),
    (I + "img_poisson.png",  "le poisson",  "o peixe",      "luh pwah-SO"),
    (I + "img_elephant.png", "l'elephant",  "o elefante",   "lay-lay-FA"),
    (I + "img_lapin.png",    "le lapin",    "o coelho",     "luh lah-PEH"),

    # ── Comidas (Índices gerais: 6 até 11) ───────────────────────────
    (I + "img_pomme.png",    "la pomme",    "a maca",       "lah pom"),
    (I + "img_baguette.png", "la baguette", "a baguete",    "lah bah-GET"),
    (I + "img_fromage.png",  "le fromage",  "o queijo",     "luh froh-MAHJ"),
    (I + "img_cafe.png",     "le cafe",     "o cafe",       "luh kah-FAY"),
    (I + "img_vin.png",      "le vin",      "o vinho",      "luh veh"),
    (I + "img_soupe.png",    "la soupe",    "a sopa",       "lah soop"),

    # ── Lugares (Índices gerais: 12 até 17) ──────────────────────────
    (I + "img_maison.png",   "la maison",   "a casa",       "lah meh-ZO"),
    (I + "img_ecole.png",    "l'ecole",     "a escola",     "lay-KOL"),
    (I + "img_hopital.png",  "l'hopital",   "o hospital",   "loh-pee-TAL"),
    (I + "img_marche.png",   "le marche",   "o mercado",    "luh mar-SHAY"),
    (I + "img_plage.png",    "la plage",    "a praia",      "lah plahj"),
    (I + "img_gare.png",     "la gare",     "a estacao",    "lah gar"),

    # ── Cores (Índices gerais: 18 até 23) ────────────────────────────
    (I + "img_rouge.png",    "rouge",       "vermelho",     "rooj"),
    (I + "img_bleu.png",     "bleu",        "azul",         "bluh"),
    (I + "img_jaune.png",    "jaune",       "amarelo",      "zhon"),
    (I + "img_vert.png",     "vert",        "verde",        "vehr"),
    (I + "img_noir.png",     "noir",        "preto",        "nwar"),
    (I + "img_blanc.png",    "blanc",       "branco",       "bla"),

    # ── Números (Índices gerais: 24 em diante) ───────────────────────
    (I + "img_num0.png",     "zéro",        "zero",         "zeh-ro"),
    (I + "img_num1.png",     "un / une",    "um / uma",     "eh / yn"),
    (I + "img_num2.png",     "deux",        "dois",         "duh"),
    (I + "img_num3.png",     "trois",       "tres",         "trwah"),
    (I + "img_num4.png",     "quatre",      "quatro",       "katr"),
    (I + "img_num5.png",     "cinq",        "cinco",        "sehnk"),
    (I + "img_num6.png",     "six",         "seis",         "sees"),
    (I + "img_num7.png",     "sept",        "sete",         "seht"),
    (I + "img_num8.png",     "huit",        "oito",         "weet"),
    (I + "img_num9.png",     "neuf",        "nove",         "nuhf"),
]


# ══════════════════════════════════════════════════════════════════════
#  FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════

def forvo_url(word: str) -> str:
    slug = (word.lower()
                .replace(" ", "_")
                .replace("'", "")
                .replace("/", "_"))
    return f"https://forvo.com/search/{slug}/fr/"


def make_qr(url: str) -> ImageReader:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=3,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#111122", back_color="white")
    img = img.resize((100, 100), PILImage.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf)


def img_reader(path: str) -> ImageReader:
    buf = io.BytesIO()
    PILImage.open(path).save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf)


# ══════════════════════════════════════════════════════════════════════
#  DESENHO DE UM CARD
# ══════════════════════════════════════════════════════════════════════

def draw_card(cv: canvas.Canvas, cx: float, cy: float,
              data: tuple, pal: dict) -> None:
    img_path, word_fr, transl, phonetic = data
    bg = pal["bg"]
    top = pal["top"]
    txt = pal["txt"]

    # ── Sombra sólida leve (sem Alpha transparente para evitar conflitos) ──
    cv.setFillColorRGB(0.88, 0.88, 0.88)
    cv.roundRect(cx + 1.2*mm, cy - 1.2*mm, CARD_W, CARD_H, 5*mm, fill=1, stroke=0)

    # ── Fundo do card ─────────────────────────────────────────────────
    cv.setFillColorRGB(*bg)
    cv.setStrokeColorRGB(*[x * 0.65 for x in top])
    cv.setLineWidth(1.5)
    cv.roundRect(cx, cy, CARD_W, CARD_H, 5*mm, fill=1, stroke=1)

    # ── Barra colorida no topo (corrigida sem vazamentos) ─────────────
    BAR = CARD_H * 0.13
    cv.setFillColorRGB(*top)
    cv.roundRect(cx, cy + CARD_H - BAR, CARD_W, BAR, 5*mm, fill=1, stroke=0)

    # ── Zona da ilustração (ajustada para não vazar no texto) ─────────
    illus_bot = cy + CARD_H - BAR - 1*mm
    text_top  = cy + CARD_H * 0.42
    
    # Subindo levemente o centro para dar espaço embaixo
    illus_cy  = ((text_top + illus_bot) / 2) + 2.5 * mm
    illus_cx  = cx + CARD_W / 2

    # Tamanho reduzido para 68% da altura útil para não sobrepor o texto
    SZ = min((illus_bot - text_top) * 0.68, CARD_W * 0.75)

    if img_path:
        cv.drawImage(
            img_reader(img_path),
            illus_cx - SZ / 2,
            illus_cy - SZ / 2,
            width=SZ,
            height=SZ,
            mask="auto",
        )
    else:
        R = CARD_H * 0.18
        cv.setFillColorRGB(*[min(1, x + 0.22) for x in top])
        cv.circle(illus_cx, illus_cy, R, fill=1, stroke=0)
        cv.setFillColorRGB(*top)
        cv.setFont("Helvetica-Bold", R * 1.1)
        cv.drawCentredString(illus_cx, illus_cy - R * 0.36, word_fr[0].upper())

    # ── Palavra em francês ────────────────────────────────────────────
    word_y = cy + CARD_H * 0.385
    cv.setFont("Helvetica-Bold", CARD_H * 0.077)
    cv.setFillColorRGB(*txt)
    cv.drawCentredString(cx + CARD_W / 2, word_y, word_fr)

    # ── Linha divisória ───────────────────────────────────────────────
    cv.setStrokeColorRGB(*[x * 0.5 for x in top])
    cv.setLineWidth(0.6)
    cv.line(cx + 5*mm, word_y - 1.8*mm, cx + CARD_W - 5*mm, word_y - 1.8*mm)

    # ── Tradução em português ─────────────────────────────────────────
    cv.setFont("Helvetica", CARD_H * 0.060)
    cv.setFillColorRGB(0.18, 0.18, 0.18)
    cv.drawCentredString(cx + CARD_W / 2, word_y - CARD_H * 0.075, transl)

    # ── Fonética ──────────────────────────────────────────────────────
    cv.setFont("Helvetica-Oblique", CARD_H * 0.050)
    cv.setFillColorRGB(0.45, 0.45, 0.45)
    cv.drawCentredString(cx + CARD_W / 2, word_y - CARD_H * 0.135, f"[ {phonetic} ]")

    # ── QR Code ───────────────────────────────────────────────────────
    QR = CARD_H * 0.175
    qr_x = cx + (CARD_W - QR) / 2
    qr_y = cy + CARD_H * 0.022
    cv.drawImage(
        make_qr(forvo_url(word_fr)),
        qr_x, qr_y,
        width=QR, height=QR,
        mask="auto",
    )


# ══════════════════════════════════════════════════════════════════════
#  GERAÇÃO DO PDF COMPLETO
# ══════════════════════════════════════════════════════════════════════

def generate_pdf(output_path: str) -> None:
    cv = canvas.Canvas(output_path, pagesize=A4)
    cv.setTitle("Flashcards de Frances")
    cv.setAuthor("Gerado com Python + ReportLab")

    cards_por_pagina = COLS * ROWS
    total_paginas    = math.ceil(len(WORDS) / cards_por_pagina)

    for page in range(total_paginas):

        # ── Cabeçalho da página ───────────────────────────────────────
        cv.setFont("Helvetica-Bold", 9)
        cv.setFillColorRGB(0.2, 0.2, 0.4)
        cv.drawString(MARGIN_X, PAGE_H - 5*mm, "Flashcards de Frances")

        cv.setFont("Helvetica", 7.5)
        cv.setFillColorRGB(0.5, 0.5, 0.5)
        cv.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 5*mm,
                           f"pag. {page + 1}/{total_paginas}")

        # ── Cards da página atual ─────────────────────────────────────
        batch = WORDS[page * cards_por_pagina : (page + 1) * cards_por_pagina]

        for i, data in enumerate(batch):
            col = i % COLS
            row = i // COLS

            cx = MARGIN_X + col * (CARD_W + GAP_X)
            cy = PAGE_H - MARGIN_Y - HEADER_H - (row + 1) * CARD_H - row * GAP_Y

            # Descobre a posição real e absoluta da palavra na lista
            idx_geral = page * cards_por_pagina + i

            # Lógica inteligente: Define a cor do card com base na categoria
            if idx_geral <= 5:
                palette_index = 0  # Laranja para Animais
            elif idx_geral <= 11:
                palette_index = 1  # Verde para Comidas
            elif idx_geral <= 17:
                palette_index = 2  # Azul para Lugares
            elif idx_geral <= 23:
                palette_index = 3  # Rosa para Cores
            else:
                palette_index = 4  # Roxo para Números

            draw_card(cv, cx, cy, data, PALETTES[palette_index])

        cv.showPage()

    cv.save()
    print(f"PDF gerado: {output_path}")
    print(f"  {total_paginas} paginas | {len(WORDS)} cards | {COLS}x{ROWS} por pagina")


if __name__ == "__main__":
    generate_pdf(OUTPUT_PDF)
