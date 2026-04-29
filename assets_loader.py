"""
Carrega e fornece sprites prontos do tileset e character sheet baixados do OpenGameArt.
Tileset: dungeon.png  (16x16 tiles, 26 colunas x 17 linhas)
Char:    top_down_character_v4.png  (frames 16x32, 8 colunas x 9 linhas)
Licença: CC0 (domínio público)
"""
import os
import pygame

_DIR   = os.path.join(os.path.dirname(__file__), "assets", "pack_extracted")
_TILE  = 16          # tamanho original do tile
_CFW   = 16          # largura do frame do personagem
_CFH   = 32          # altura do frame do personagem

_tileset   = None
_charsheet = None
_cache     = {}


def _load():
    global _tileset, _charsheet
    if _tileset is None:
        _tileset   = pygame.image.load(os.path.join(_DIR, "dungeon.png")).convert_alpha()
        _charsheet = pygame.image.load(os.path.join(_DIR, "top_down_character_v4.png")).convert_alpha()


# ── tiles ─────────────────────────────────────────────────────────────────────
def get_tile(col: int, row: int, size: int = 40) -> pygame.Surface:
    key = ("tile", col, row, size)
    if key not in _cache:
        _load()
        src = _tileset.subsurface((col * _TILE, row * _TILE, _TILE, _TILE))
        _cache[key] = pygame.transform.scale(src, (size, size))
    return _cache[key]


# Tiles pré-definidos (coordenadas identificadas visualmente no tileset)
def tile_chao(size=40):       return get_tile(11, 8, size)   # salmon/pink dungeon floor
def tile_chao_alt(size=40):   return get_tile(10, 7, size)   # variante com ponto
def tile_parede(size=40):     return get_tile(10, 0, size)   # gray stone – parede
def tile_parede_dark(size=40):return get_tile(12, 2, size)   # stone block escuro
def tile_caixa(size=40):      return get_tile(6,  10, size)  # arco de masmorra – caixa
def tile_saida(size=40):      return get_tile(4,  10, size)  # grade/portão – saída


# ── frames do personagem ──────────────────────────────────────────────────────
def get_char_frame(col: int, row: int, w: int, h: int,
                   flip_x=False, tint=None) -> pygame.Surface:
    key = ("char", col, row, w, h, flip_x, tint)
    if key not in _cache:
        _load()
        src  = _charsheet.subsurface((col * _CFW, row * _CFH, _CFW, _CFH))
        surf = pygame.transform.scale(src, (w, h))
        if flip_x:
            surf = pygame.transform.flip(surf, True, False)
        if tint:
            tinted = surf.copy()
            tinted.fill(tint, special_flags=pygame.BLEND_MULT)
            surf = tinted
        _cache[key] = surf
    return _cache[key]


def get_walk_frames(row: int, num: int, w: int, h: int,
                    flip_x=False, tint=None):
    """Retorna lista de frames de caminhada de uma linha da spritesheet."""
    return [get_char_frame(c, row, w, h, flip_x, tint) for c in range(num)]


# ── conjuntos prontos ─────────────────────────────────────────────────────────
PLAYER_W = 24
PLAYER_H = 32

# Row 1 = walk cycle com 4 frames (frente/virado para câmera)
# Row 0 = 2 frames idle
# Row 2 = 1 frame (pose agachada)

def player_walk_right(n=4):
    return get_walk_frames(1, n, PLAYER_W, PLAYER_H)

def player_walk_left(n=4):
    return get_walk_frames(1, n, PLAYER_W, PLAYER_H, flip_x=True)

def player_idle():
    return get_char_frame(0, 0, PLAYER_W, PLAYER_H)

def player_hidden():
    return get_char_frame(0, 2, PLAYER_W, PLAYER_H)


GUARD_W = 22
GUARD_H = 28

# Guardas usam row 3 (walk cycle) com tint por papel
_TINT_PATRULHEIRO = (255, 160, 160)   # vermelho suave
_TINT_SENTINELA   = (160, 180, 255)   # azul
_TINT_CACADOR     = (255, 120, 80)    # laranja quente

def _tint_por_papel(papel):
    return {
        "patrulheiro": _TINT_PATRULHEIRO,
        "sentinela":   _TINT_SENTINELA,
        "cacador":     _TINT_CACADOR,
    }.get(papel, _TINT_PATRULHEIRO)

def guard_walk_frames(papel="patrulheiro", n=4):
    tint = _tint_por_papel(papel)
    return get_walk_frames(3, n, GUARD_W, GUARD_H, tint=tint)

def guard_walk_frames_left(papel="patrulheiro", n=4):
    tint = _tint_por_papel(papel)
    return get_walk_frames(3, n, GUARD_W, GUARD_H, flip_x=True, tint=tint)

def guard_idle(papel="patrulheiro"):
    tint = _tint_por_papel(papel)
    return get_char_frame(0, 2, GUARD_W, GUARD_H, tint=tint)
