"""
Assets do jogo:
- dungeon.png / top_down_character_v4.png  — CC0 (OpenGameArt)
- CyberTileA4.png  — CC-BY 4.0 (cyberpunk bricks + floor)
"""
import os
import pygame

_DIR      = os.path.join(os.path.dirname(__file__), "assets", "pack_extracted")
_DIR_SCIFI = os.path.join(os.path.dirname(__file__), "assets", "scifi")
_TILE  = 16
_CFW   = 16
_CFH   = 32

_tileset   = None
_charsheet = None
_cybertile = None   # CyberTileA4.png
_cache     = {}


def _load():
    global _tileset, _charsheet
    if _tileset is None:
        _tileset   = pygame.image.load(os.path.join(_DIR, "dungeon.png")).convert_alpha()
        _charsheet = pygame.image.load(os.path.join(_DIR, "top_down_character_v4.png")).convert_alpha()


def _load_cyber():
    global _cybertile
    if _cybertile is None:
        _cybertile = pygame.image.load(
            os.path.join(_DIR_SCIFI, "CyberTileA4.png")
        ).convert_alpha()


def _get_cyber_region(rx: int, ry: int, rw: int, rh: int, size: int,
                      darken=None, brighten=None) -> pygame.Surface:
    """darken = BLEND_MULT tuple,  brighten = BLEND_ADD tuple"""
    key = ("cyber", rx, ry, rw, rh, size, darken, brighten)
    if key not in _cache:
        _load_cyber()
        src  = _cybertile.subsurface((rx, ry, rw, rh))
        surf = pygame.transform.scale(src, (size, size))
        surf = surf.copy()
        if darken:
            surf.fill(darken,  special_flags=pygame.BLEND_MULT)
        if brighten:
            surf.fill(brighten, special_flags=pygame.BLEND_ADD)
        _cache[key] = surf
    return _cache[key]


# ── tiles cyberpunk (CyberTileA4.png) ─────────────────────────────────────────
# Chão: painéis de concreto industrial  — região (40,400,80,80)  avg≈104 gray
# Parede: tijolos dark cyberpunk        — região (220,260,80,80) avg≈56  gray

def tile_chao(size=40):
    # BLEND_ADD +50 para clarear: avg ~154 (60% brightness), leve tint azul
    return _get_cyber_region(40, 400, 80, 80, size, brighten=(40, 42, 55))

def tile_chao_alt(size=40):
    return _get_cyber_region(0, 400, 80, 80, size, brighten=(38, 40, 53))

def tile_chao_b(size=40):
    return _get_cyber_region(40, 440, 80, 80, size, brighten=(45, 47, 58))

def tile_parede(size=40):
    key = ("cyber_wall_neon", size)
    if key not in _cache:
        # Escurece muito + borda neon ciano
        base = _get_cyber_region(220, 260, 80, 80, size, darken=(100, 100, 115))
        surf = base.copy()
        pygame.draw.rect(surf, (0, 140, 200), (0, 0, size, size), 1)
        _cache[key] = surf
    return _cache[key]

def tile_parede_dark(size=40):
    return _get_cyber_region(220, 300, 80, 80, size, darken=(80, 80, 95))

# ── tiles do dungeon original (mantidos para caixa/saida) ─────────────────────
def _get_dungeon_tile(col: int, row: int, size: int = 40) -> pygame.Surface:
    key = ("tile", col, row, size)
    if key not in _cache:
        _load()
        src = _tileset.subsurface((col * _TILE, row * _TILE, _TILE, _TILE))
        _cache[key] = pygame.transform.scale(src, (size, size))
    return _cache[key]

def tile_caixa(size=40):  return _get_dungeon_tile(6,  10, size)
def tile_saida(size=40):  return _get_dungeon_tile(4,  10, size)


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
