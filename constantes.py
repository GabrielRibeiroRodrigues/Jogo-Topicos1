# ── Tela ─────────────────────────────────────────────────────────────────────
LARGURA = 800
ALTURA  = 600
FPS     = 60
TITULO_JOGO = 'Jogo do Gabriel – Stealth Game'

# ── Cores ─────────────────────────────────────────────────────────────────────
PRETO        = (0,   0,   0)
BRANCO       = (255, 255, 255)
CINZA        = (140, 140, 140)
CINZA_ESCURO = (55,  55,  55)
VERDE        = (0,   200, 50)
AMARELO      = (255, 210, 0)
VERMELHO     = (210, 0,   0)
AZUL         = (40,  100, 220)
MARROM       = (120, 80,  40)
BEGE         = (210, 170, 110)
VERDE_ESCURO = (20,  120, 40)
COR_CHAO     = (30,  30,  40)

# ── Tile ──────────────────────────────────────────────────────────────────────
TAM_TILE = 40

# ── Jogador ───────────────────────────────────────────────────────────────────
VEL_JOGADOR  = 3
VEL_AGACHADO = 1

# ── Guarda / FSM ──────────────────────────────────────────────────────────────
VEL_PATRULHA        = 1.5
VEL_ALERTA          = 2.2
VEL_PERSEGUICAO     = 3.5
RAIO_VISAO          = 160   # pixels
ANGULO_CONE         = 45    # graus para cada lado
TIMER_ALERTA        = 3000  # ms – tempo investigando antes de voltar a patrulha
TEMPO_PERDA_JOGADOR = 2000  # ms – tempo sem ver o jogador antes de ir a ALERTA

# ── Som (pedra / distração) ───────────────────────────────────────────────────
RAIO_SOM_MAX     = 150   # pixels
VEL_EXPANSAO_SOM = 6     # pixels por frame

# ── Fonte ─────────────────────────────────────────────────────────────────────
FONTE = 'arial'
