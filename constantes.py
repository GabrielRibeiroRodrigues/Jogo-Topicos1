# ── Tela ─────────────────────────────────────────────────────────────────────
LARGURA = 1024
ALTURA  = 640
FPS     = 60
TITULO_JOGO = 'STEALTH OPS — SOMBRA DIGITAL'

# ── Paleta Cyberpunk Dark ─────────────────────────────────────────────────────
PRETO        = (0,    0,    0)
BRANCO       = (210,  220,  240)
CINZA        = (100,  112,  145)
CINZA_ESCURO = (28,   32,   50)
VERDE        = (57,   255,  20)
AMARELO      = (255,  210,  0)
VERMELHO     = (255,  50,   60)
AZUL         = (0,    160,  255)
CIANO        = (0,    220,  255)
MAGENTA      = (255,  0,    180)
LARANJA      = (255,  130,  0)
COR_CHAO     = (10,   12,   22)
COR_GRADE    = (18,   22,   38)

# ── Tile ──────────────────────────────────────────────────────────────────────
TAM_TILE = 40

# ── Jogador ───────────────────────────────────────────────────────────────────
VEL_JOGADOR        = 4.4
VEL_AGACHADO       = 1.6
LIVES_INICIAIS     = 3
INVENCIBILIDADE_MS = 1800

# ── Guarda / FSM ──────────────────────────────────────────────────────────────
VEL_PATRULHA        = 1.5
VEL_ALERTA          = 2.2
VEL_PERSEGUICAO     = 3.5
RAIO_VISAO          = 160
ANGULO_CONE         = 45
TIMER_ALERTA        = 3000
TEMPO_PERDA_JOGADOR = 2000
RAIO_PERSEGUICAO_IMEDIATA = 120

# ── EMP (habilidade 2) ────────────────────────────────────────────────────────
EMP_RAIO                 = 200
EMP_COOLDOWN_MS          = 12000
EMP_DURACAO_ATORDOADO_MS = 3200

# ── Fumaca (habilidade 1, substitui pedra) ────────────────────────────────────
RAIO_SOM_MAX       = 150
VEL_EXPANSAO_SOM   = 6
FUMACA_RAIO_MAX    = 90
FUMACA_DURACAO_MS  = 4500
FUMACA_EXPANSAO_MS = 900
COOLDOWN_FUMACA_MS = 3500
COOLDOWN_PEDRA_MS  = COOLDOWN_FUMACA_MS   # alias retrocompat

# ── Score / Ranking ───────────────────────────────────────────────────────────
SCORE_BASE_FASE           = 2000
SCORE_PENALIDADE_TEMPO    = 4
SCORE_PENALIDADE_DETECCAO = 180
SCORE_PENALIDADE_HEAT     = 6

# ── Heat / pressão global ─────────────────────────────────────────────────────
HEAT_MAX                      = 100.0
HEAT_DECAY_POR_SEG            = 6.5
HEAT_GAIN_ALERTA_POR_SEG      = 10.0
HEAT_GAIN_PERSEGUICAO_POR_SEG = 22.0
HEAT_FATOR_MAX                = 1.35

# ── IA Avançada ───────────────────────────────────────────────────────────────
PERCEPCAO_MAX                    = 100.0
GANHO_PERCEPCAO_POR_SEG          = 92.0
PERDA_PERCEPCAO_POR_SEG          = 64.0
RAIO_COMUNICACAO_GUARDA          = 230
COOLDOWN_ALERTA_COMPARTILHADO_MS = 1100

# ── Progressão ────────────────────────────────────────────────────────────────
DISTANCIA_POR_NIVEL = 600
NIVEL_ALVO          = 10
TEMPO_ALVO_SEG      = 600

# ── Limites de escala tática ──────────────────────────────────────────────────
VEL_PATRULHA_MAX        = 3.0
VEL_ALERTA_MAX          = 4.0
VEL_PERSEGUICAO_MAX     = 6.0
RAIO_VISAO_MAX          = 260
ANGULO_CONE_MAX         = 70
TIMER_ALERTA_MIN        = 1200
TEMPO_PERDA_JOGADOR_MIN = 700
FATOR_AUDICAO_MAX       = 1.6

# ── Intel ─────────────────────────────────────────────────────────────────────
INTEL_PONTOS_PADRAO = 1

# ── Fonte ─────────────────────────────────────────────────────────────────────
FONTE = 'arial'
