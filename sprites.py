import pygame
import math
import constantes


# ─────────────────────────────────────────────────────────────────────────────
#  PAREDE
# ─────────────────────────────────────────────────────────────────────────────
class Parede(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.obstaculos)
        self.image = pygame.Surface((constantes.TAM_TILE, constantes.TAM_TILE))
        self.image.fill(constantes.CINZA_ESCURO)
        pygame.draw.rect(self.image, (25, 25, 35), self.image.get_rect(), 1)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# ─────────────────────────────────────────────────────────────────────────────
#  CAIXA  (obstáculo + esconderijo)
# ─────────────────────────────────────────────────────────────────────────────
class Caixa(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.obstaculos, game.caixas)
        self.image = pygame.Surface((constantes.TAM_TILE, constantes.TAM_TILE))
        self.image.fill(constantes.MARROM)
        pygame.draw.rect(self.image, constantes.BEGE, (5, 5, 30, 30), 3)
        pygame.draw.line(self.image, constantes.BEGE, (20, 5),  (20, 35), 1)
        pygame.draw.line(self.image, constantes.BEGE, (5, 20),  (35, 20), 1)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# ─────────────────────────────────────────────────────────────────────────────
#  SAÍDA  (objetivo do jogador)
# ─────────────────────────────────────────────────────────────────────────────
class Saida(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()                   # não pertence a nenhum grupo
        self.image = pygame.Surface((constantes.TAM_TILE, constantes.TAM_TILE))
        self.image.fill(constantes.VERDE_ESCURO)
        pygame.draw.rect(self.image, constantes.VERDE, (5, 5, 30, 30))
        # seta apontando para cima = "saída"
        seta = [(20, 8), (30, 20), (24, 20), (24, 32), (16, 32), (16, 20), (10, 20)]
        pygame.draw.polygon(self.image, constantes.BRANCO, seta)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# ─────────────────────────────────────────────────────────────────────────────
#  JOGADOR
# ─────────────────────────────────────────────────────────────────────────────
class Jogador(pygame.sprite.Sprite):
    TAMANHO = 22

    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites)
        self.game = game
        self.image = pygame.Surface((self.TAMANHO, self.TAMANHO), pygame.SRCALPHA)
        self.rect  = self.image.get_rect()
        # Centralizar dentro do tile
        self.rect.x = x + (constantes.TAM_TILE - self.TAMANHO) // 2
        self.rect.y = y + (constantes.TAM_TILE - self.TAMANHO) // 2
        # Posição float para movimento suave
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.is_hidden = False
        self._redesenhar()

    # ── visual ────────────────────────────────────────────────────────────────
    def _redesenhar(self):
        self.image.fill((0, 0, 0, 0))
        r   = self.TAMANHO // 2
        cor = constantes.CINZA if self.is_hidden else constantes.AZUL
        pygame.draw.circle(self.image, cor, (r, r), r)
        pygame.draw.circle(self.image, constantes.BRANCO, (r, r), r, 2)
        if self.is_hidden:
            # marcação visual de "agachado"
            pygame.draw.line(self.image, constantes.AMARELO, (r-5, r-5), (r+5, r+5), 2)
            pygame.draw.line(self.image, constantes.AMARELO, (r+5, r-5), (r-5, r+5), 2)

    # ── loop ──────────────────────────────────────────────────────────────────
    def update(self):
        self._mover()
        self._verificar_esconderijo()
        self._redesenhar()

    # ── movimento com resolução de colisão ────────────────────────────────────
    def _mover(self):
        teclas = pygame.key.get_pressed()
        vel    = constantes.VEL_AGACHADO if self.is_hidden else constantes.VEL_JOGADOR
        dx, dy = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:    dy = -vel
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:  dy =  vel
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:  dx = -vel
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx =  vel

        # eixo X
        self.pos.x += dx
        self.rect.x = int(self.pos.x)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if dx > 0:
                self.rect.right = hit.rect.left
            elif dx < 0:
                self.rect.left = hit.rect.right
            self.pos.x = float(self.rect.x)

        # eixo Y
        self.pos.y += dy
        self.rect.y = int(self.pos.y)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if dy > 0:
                self.rect.bottom = hit.rect.top
            elif dy < 0:
                self.rect.top = hit.rect.bottom
            self.pos.y = float(self.rect.y)

    # ── mecânica de esconderijo ───────────────────────────────────────────────
    def _verificar_esconderijo(self):
        teclas = pygame.key.get_pressed()
        ctrl   = teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]
        # jogador precisa estar adjacente a uma caixa E segurar CTRL
        expandido       = self.rect.inflate(8, 8)
        perto_de_caixa  = any(expandido.colliderect(c.rect) for c in self.game.caixas)
        self.is_hidden  = ctrl and perto_de_caixa


# ─────────────────────────────────────────────────────────────────────────────
#  SOM  (pedra / distração)
# ─────────────────────────────────────────────────────────────────────────────
class Som(pygame.sprite.Sprite):
    """Onda sonora circular que se expande e alerta guardas próximos."""

    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.sons)
        self.game = game
        self.pos  = pygame.math.Vector2(x, y)
        self.raio = 5
        # imagem mínima (colisão feita via raio, não rect)
        self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        self.raio += constantes.VEL_EXPANSAO_SOM
        if self.raio >= constantes.RAIO_SOM_MAX:
            self.kill()

    def desenhar(self, superficie):
        """Desenha anel sonoro na superficie SRCALPHA fornecida pelo Game."""
        alpha = max(0, int(180 * (1 - self.raio / constantes.RAIO_SOM_MAX)))
        cor   = (*constantes.AMARELO, alpha)
        pygame.draw.circle(superficie, cor,
                           (int(self.pos.x), int(self.pos.y)),
                           int(self.raio), 2)


# ─────────────────────────────────────────────────────────────────────────────
#  GUARDA  (FSM: PATRULHA → ALERTA → PERSEGUIÇÃO)
# ─────────────────────────────────────────────────────────────────────────────
class Guarda(pygame.sprite.Sprite):
    TAMANHO = 22
    COR_ESTADOS = {
        "PATRULHA":    constantes.VERDE,
        "ALERTA":      constantes.AMARELO,
        "PERSEGUICAO": constantes.VERMELHO,
    }

    def __init__(self, game, cx, cy, waypoints):
        super().__init__(game.todas_as_sprites, game.guardas)
        self.game = game
        self.image = pygame.Surface((self.TAMANHO, self.TAMANHO), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(cx, cy))
        self.pos   = pygame.math.Vector2(cx, cy)

        # waypoints de patrulha
        self.waypoints     = [pygame.math.Vector2(wp) for wp in waypoints]
        self.waypoint_atual = 0

        # ── FSM ───────────────────────────────────────────────────────────────
        self.estado = "PATRULHA"

        # direção inicial: aponta para o segundo waypoint
        if len(self.waypoints) > 1:
            d = self.waypoints[1] - self.waypoints[0]
            self.direcao = d.normalize() if d.length() > 0 else pygame.math.Vector2(1, 0)
        else:
            self.direcao = pygame.math.Vector2(1, 0)

        # variáveis do estado ALERTA
        self.alvo_investigar = None
        self.chegou_ao_alvo  = False
        self.tempo_chegada   = 0

        # variáveis do estado PERSEGUIÇÃO
        self.ultimo_avistamento = None
        self.tempo_inicio_perda = None

        self._redesenhar()

    # ── visual ────────────────────────────────────────────────────────────────
    def _redesenhar(self):
        self.image.fill((0, 0, 0, 0))
        r   = self.TAMANHO // 2
        cor = self.COR_ESTADOS[self.estado]
        pygame.draw.circle(self.image, cor, (r, r), r)
        pygame.draw.circle(self.image, constantes.BRANCO, (r, r), r, 2)
        # seta indicando direção de visão
        if self.direcao.length() > 0:
            d     = self.direcao.normalize()
            ponta = (int(r + d.x * (r - 3)), int(r + d.y * (r - 3)))
            pygame.draw.line(self.image, constantes.BRANCO, (r, r), ponta, 2)

    # ── loop principal da FSM ─────────────────────────────────────────────────
    def update(self):
        if self.estado == "PATRULHA":
            self._patrulhar()
            if self._pode_ver_jogador():
                self._mudar_estado("PERSEGUICAO")
            elif self._pode_ouvir():
                self._mudar_estado("ALERTA")

        elif self.estado == "ALERTA":
            self._investigar()
            if self._pode_ver_jogador():
                self._mudar_estado("PERSEGUICAO")

        elif self.estado == "PERSEGUICAO":
            self._perseguir()

        self._redesenhar()

    # ── transição de estado ───────────────────────────────────────────────────
    def _mudar_estado(self, novo_estado):
        self.estado = novo_estado
        if novo_estado == "ALERTA":
            self.chegou_ao_alvo  = False
        elif novo_estado == "PERSEGUICAO":
            self.ultimo_avistamento = pygame.math.Vector2(self.game.jogador.rect.center)
            self.tempo_inicio_perda = None

    # ── movimentação com colisão ──────────────────────────────────────────────
    def _mover_para(self, alvo_vec, velocidade):
        direcao = alvo_vec - self.pos
        if direcao.length() < 1:
            return
        self.direcao = direcao.normalize()
        mov = self.direcao * velocidade

        # eixo X
        self.pos.x += mov.x
        self.rect.centerx = int(self.pos.x)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if mov.x > 0:
                self.rect.right = hit.rect.left
            elif mov.x < 0:
                self.rect.left = hit.rect.right
            self.pos.x = float(self.rect.centerx)

        # eixo Y
        self.pos.y += mov.y
        self.rect.centery = int(self.pos.y)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if mov.y > 0:
                self.rect.bottom = hit.rect.top
            elif mov.y < 0:
                self.rect.top = hit.rect.bottom
            self.pos.y = float(self.rect.centery)

    # ── estados da FSM ────────────────────────────────────────────────────────
    def _patrulhar(self):
        if not self.waypoints:
            return
        alvo = self.waypoints[self.waypoint_atual]
        if (alvo - self.pos).length() < 5:
            # chegou ao waypoint: avançar para o próximo
            self.waypoint_atual = (self.waypoint_atual + 1) % len(self.waypoints)
        else:
            self._mover_para(alvo, constantes.VEL_PATRULHA)

    def _investigar(self):
        if self.alvo_investigar is None:
            self._mudar_estado("PATRULHA")
            return

        dist = (self.alvo_investigar - self.pos).length()
        if dist > 6:
            self._mover_para(self.alvo_investigar, constantes.VEL_ALERTA)
            self.chegou_ao_alvo = False
        else:
            # chegou ao ponto investigado: iniciar temporizador
            if not self.chegou_ao_alvo:
                self.chegou_ao_alvo = True
                self.tempo_chegada  = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.tempo_chegada >= constantes.TIMER_ALERTA:
                # nada encontrado → voltar a patrulha
                self._mudar_estado("PATRULHA")

    def _perseguir(self):
        if self._pode_ver_jogador():
            # vê o jogador: perseguir e atualizar último avistamento
            self.ultimo_avistamento = pygame.math.Vector2(self.game.jogador.rect.center)
            self.tempo_inicio_perda = None
            self._mover_para(self.ultimo_avistamento, constantes.VEL_PERSEGUICAO)
        else:
            # perdeu o jogador de vista: ir ao último avistamento
            if self.tempo_inicio_perda is None:
                self.tempo_inicio_perda = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.tempo_inicio_perda >= constantes.TEMPO_PERDA_JOGADOR:
                # tempo esgotado → investigar o último local visto
                if self.ultimo_avistamento:
                    self.alvo_investigar = self.ultimo_avistamento.copy()
                self._mudar_estado("ALERTA")
                return

            if self.ultimo_avistamento:
                self._mover_para(self.ultimo_avistamento, constantes.VEL_PERSEGUICAO)

    # ── detecção de visão (distância + ângulo do cone) ────────────────────────
    def _pode_ver_jogador(self):
        jogador = self.game.jogador
        if jogador.is_hidden:
            return False                                   # escondido = invisível

        vetor     = pygame.math.Vector2(jogador.rect.center) - self.pos
        distancia = vetor.length()

        if distancia > constantes.RAIO_VISAO:              # condição A: distância
            return False
        if distancia < 1 or self.direcao.length() == 0:
            return True

        # condição B: ângulo via produto escalar
        dot    = vetor.normalize().dot(self.direcao.normalize())
        dot    = max(-1.0, min(1.0, dot))                  # clamp evita NaN
        angulo = math.degrees(math.acos(dot))
        return angulo <= constantes.ANGULO_CONE

    # ── detecção de som ───────────────────────────────────────────────────────
    def _pode_ouvir(self):
        """Retorna True se a onda sonora de alguma pedra já chegou até o guarda."""
        for som in self.game.sons:
            if (self.pos - som.pos).length() <= som.raio:
                self.alvo_investigar = pygame.math.Vector2(som.pos)
                return True
        return False

    # ── desenho do cone (chamado pelo Game com a surface de overlay) ───────────
    def desenhar_cone(self, superficie):
        """Desenha o cone de visão translúcido na superficie SRCALPHA passada."""
        if self.direcao.length() == 0:
            return

        alpha_tabela = {"PATRULHA": 60, "ALERTA": 70, "PERSEGUICAO": 85}
        cor = (*self.COR_ESTADOS[self.estado], alpha_tabela[self.estado])

        centro    = (int(self.pos.x), int(self.pos.y))
        dir_norm  = self.direcao.normalize()
        meio_cone = math.radians(constantes.ANGULO_CONE)
        raio      = constantes.RAIO_VISAO

        # polígono em leque
        pontos = [centro]
        N = 20
        for i in range(N + 1):
            t      = i / N
            angulo = -meio_cone + 2 * meio_cone * t
            cos_a  = math.cos(angulo)
            sin_a  = math.sin(angulo)
            # rotacionar o vetor direção pelo ângulo
            dx = dir_norm.x * cos_a - dir_norm.y * sin_a
            dy = dir_norm.x * sin_a + dir_norm.y * cos_a
            pontos.append((centro[0] + dx * raio, centro[1] + dy * raio))

        pygame.draw.polygon(superficie, cor, pontos)
