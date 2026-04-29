import pygame
import math
import random
import constantes
import assets_loader


# ─────────────────────────────────────────────────────────────────────────────
#  PAREDE
# ─────────────────────────────────────────────────────────────────────────────
class Parede(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.obstaculos)
        T = constantes.TAM_TILE
        self.image = assets_loader.tile_parede(T)
        self.rect  = self.image.get_rect(topleft=(x, y))


# ─────────────────────────────────────────────────────────────────────────────
#  CAIXA
# ─────────────────────────────────────────────────────────────────────────────
class Caixa(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.obstaculos, game.caixas)
        T = constantes.TAM_TILE
        self.image = assets_loader.tile_caixa(T)
        self.rect  = self.image.get_rect(topleft=(x, y))


# ─────────────────────────────────────────────────────────────────────────────
#  SAIDA  (animada)
# ─────────────────────────────────────────────────────────────────────────────
class Saida(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites)
        self.game = game
        self._t = 0.0
        T = constantes.TAM_TILE
        self.image = pygame.Surface((T, T), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self._redesenhar()

    def update(self):
        self._t += 0.08
        self._redesenhar()

    def _redesenhar(self):
        T = constantes.TAM_TILE
        self.image.fill((0, 0, 0, 0))
        pulse = 0.6 + 0.4 * math.sin(self._t)
        glow_a = int(50 + 40 * pulse)
        pygame.draw.rect(self.image, (0, 200, 80, glow_a), (0, 0, T, T), border_radius=6)
        pygame.draw.rect(self.image, (0, 120, 45, 200), (3, 3, T - 6, T - 6), border_radius=5)
        arrow_g = int(180 + 75 * pulse)
        arrow_col = (20, arrow_g, 60)
        seta = [
            (T // 2, 8), (T - 10, 20), (T // 2 + 6, 20),
            (T // 2 + 6, T - 8), (T // 2 - 6, T - 8),
            (T // 2 - 6, 20), (10, 20),
        ]
        pygame.draw.polygon(self.image, arrow_col, seta)
        border_g = int(160 + 95 * pulse)
        pygame.draw.rect(self.image, (0, border_g, 60), (0, 0, T, T), 2, border_radius=6)


# ─────────────────────────────────────────────────────────────────────────────
#  INTEL  (animada)
# ─────────────────────────────────────────────────────────────────────────────
class Intel(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.intels)
        self._t = random.uniform(0, math.pi * 2)
        T = constantes.TAM_TILE
        self.image = pygame.Surface((T, T), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self._redesenhar()

    def update(self):
        self._t += 0.07
        self._redesenhar()

    def _redesenhar(self):
        T = constantes.TAM_TILE
        self.image.fill((0, 0, 0, 0))
        pulse = 0.7 + 0.3 * math.sin(self._t)
        pygame.draw.rect(self.image, (18, 26, 50, 170), (2, 2, T - 4, T - 4), border_radius=4)
        pygame.draw.rect(self.image, (36, 58, 118), (8, 7, T - 16, T - 14), border_radius=3)
        pygame.draw.rect(self.image, (18, 32, 78), (11, 10, T - 22, T - 20), border_radius=2)
        for i in range(3):
            yy = 13 + i * 5
            pygame.draw.line(self.image, (55, 95, 200, 140), (13, yy), (T - 13, yy), 1)
        r = max(2, int(5 * pulse))
        pygame.draw.circle(self.image, (int(160 * pulse), int(200 * pulse), 255), (T // 2, T // 2), r)
        ba = int(160 + 95 * pulse)
        pygame.draw.rect(self.image, (80, 130, ba), (2, 2, T - 4, T - 4), 1, border_radius=4)


# ─────────────────────────────────────────────────────────────────────────────
#  JOGADOR
# ─────────────────────────────────────────────────────────────────────────────
class Jogador(pygame.sprite.Sprite):
    TAMANHO = assets_loader.PLAYER_W

    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites)
        self.game = game
        W, H = assets_loader.PLAYER_W, assets_loader.PLAYER_H
        self.image = pygame.Surface((W, H), pygame.SRCALPHA)
        self.rect  = self.image.get_rect()
        self.rect.x = x + (constantes.TAM_TILE - W) // 2
        self.rect.y = y + (constantes.TAM_TILE - H) // 2
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.velocidade = pygame.math.Vector2(0, 0)
        self.is_hidden = False
        self.virado_direita = True
        self.movendo = False
        self._contador_anim = 0
        self._invencivel_ate = 0
        self._frames = self._criar_frames_personagem()
        self._redesenhar()

    @property
    def is_invencivel(self):
        return pygame.time.get_ticks() < self._invencivel_ate

    def ativar_invencibilidade(self):
        self._invencivel_ate = pygame.time.get_ticks() + constantes.INVENCIBILIDADE_MS

    def _criar_frames_personagem(self):
        return {
            "andar_dir": assets_loader.player_walk_right(4),
            "andar_esq": assets_loader.player_walk_left(4),
            "idle":      assets_loader.player_idle(),
            "agachado":  assets_loader.player_hidden(),
        }

    def _redesenhar(self):
        if self.is_hidden:
            frame = self._frames["agachado"]
        else:
            if self.movendo:
                self._contador_anim = (self._contador_anim + 1) % (4 * 6)
                idx = (self._contador_anim // 6) % 4
                if self.virado_direita:
                    frame = self._frames["andar_dir"][idx]
                else:
                    frame = self._frames["andar_esq"][idx]
            else:
                self._contador_anim = 0
                frame = self._frames["idle"]

        # Pisca quando invencível
        if self.is_invencivel and (pygame.time.get_ticks() // 80) % 2 == 0:
            temp = frame.copy()
            temp.set_alpha(90)
            self.image = temp
        else:
            self.image = frame

    def update(self):
        self._mover()
        self._verificar_esconderijo()
        self._redesenhar()

    def _mover(self):
        teclas = pygame.key.get_pressed()
        vel_max = constantes.VEL_AGACHADO if self.is_hidden else constantes.VEL_JOGADOR
        ix, iy = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:    iy -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:  iy += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:  ix -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: ix += 1

        alvo = pygame.math.Vector2(ix, iy)
        if alvo.length_squared() > 0:
            alvo = alvo.normalize() * vel_max

        fa = 0.26 if self.is_hidden else 0.20
        fd = 0.55 if self.is_hidden else 0.72
        if alvo.length_squared() > 0:
            self.velocidade.x += (alvo.x - self.velocidade.x) * fa
            self.velocidade.y += (alvo.y - self.velocidade.y) * fa
        else:
            self.velocidade.x *= fd
            self.velocidade.y *= fd

        if abs(self.velocidade.x) < 0.03: self.velocidade.x = 0
        if abs(self.velocidade.y) < 0.03: self.velocidade.y = 0

        dx, dy = self.velocidade.x, self.velocidade.y
        self.movendo = abs(dx) > 0.06 or abs(dy) > 0.06
        if   dx >  0.05: self.virado_direita = True
        elif dx < -0.05: self.virado_direita = False

        self.pos.x += dx
        self.rect.x = int(self.pos.x)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if dx > 0: self.rect.right = hit.rect.left
            else:      self.rect.left  = hit.rect.right
            self.velocidade.x = 0
            self.pos.x = float(self.rect.x)

        self.pos.y += dy
        self.rect.y = int(self.pos.y)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if dy > 0: self.rect.bottom = hit.rect.top
            else:      self.rect.top    = hit.rect.bottom
            self.velocidade.y = 0
            self.pos.y = float(self.rect.y)

    def _verificar_esconderijo(self):
        teclas   = pygame.key.get_pressed()
        ctrl     = teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]
        expandido = self.rect.inflate(8, 8)
        perto    = any(expandido.colliderect(c.rect) for c in self.game.caixas)
        self.is_hidden = ctrl and perto


# ─────────────────────────────────────────────────────────────────────────────
#  FUMACA  (distração sonora + nuvem de fumaça que bloqueia visão)
# ─────────────────────────────────────────────────────────────────────────────
class FumacaCloud(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.todas_as_sprites, game.sons, game.fumacas)
        self.game = game
        self.pos  = pygame.math.Vector2(x, y)
        self.raio = 5              # sound radius (usado pela IA dos guardas)
        self.raio_fumaca = 5.0     # visual smoke radius
        self._nascimento = pygame.time.get_ticks()
        self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        agora      = pygame.time.get_ticks()
        tempo_vida = agora - self._nascimento

        if self.raio < constantes.RAIO_SOM_MAX:
            self.raio += constantes.VEL_EXPANSAO_SOM

        prog_exp = min(1.0, tempo_vida / constantes.FUMACA_EXPANSAO_MS)
        self.raio_fumaca = constantes.FUMACA_RAIO_MAX * prog_exp

        if tempo_vida >= constantes.FUMACA_DURACAO_MS:
            self.kill()

    def bloqueia_linha(self, x1, y1, x2, y2):
        if self.raio_fumaca < 15:
            return False
        cx, cy = self.pos.x, self.pos.y
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(cx - x1, cy - y1) <= self.raio_fumaca
        t  = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)))
        px = x1 + t * dx
        py = y1 + t * dy
        return math.hypot(cx - px, cy - py) <= self.raio_fumaca * 0.8

    def desenhar(self, superficie, camera_x=0, camera_y=0):
        agora      = pygame.time.get_ticks()
        tempo_vida = agora - self._nascimento
        cx = int(self.pos.x - camera_x)
        cy = int(self.pos.y - camera_y)

        # Sound ring
        if self.raio < constantes.RAIO_SOM_MAX:
            alpha = max(0, int(200 * (1 - self.raio / constantes.RAIO_SOM_MAX)))
            pygame.draw.circle(superficie, (255, 200, 0, alpha), (cx, cy), int(self.raio), 2)
            pygame.draw.circle(superficie, (255, 235, 100, max(0, alpha - 50)),
                               (cx, cy), max(2, int(self.raio * 0.55)), 1)

        # Smoke cloud
        if self.raio_fumaca > 5:
            restante = constantes.FUMACA_DURACAO_MS - tempo_vida
            fade = min(1.0, restante / (constantes.FUMACA_DURACAO_MS * 0.25))
            fade = max(0.0, fade)
            a1 = int(90 * fade)
            a2 = int(55 * fade)
            pygame.draw.circle(superficie, (120, 150, 130, a1), (cx, cy), int(self.raio_fumaca))
            pygame.draw.circle(superficie, (80,  110,  90, a2), (cx, cy), int(self.raio_fumaca * 0.65))
            pygame.draw.circle(superficie, (50,   80,  60, 70), (cx, cy), int(self.raio_fumaca), 3)


# ─────────────────────────────────────────────────────────────────────────────
#  SOM  (alias para backward compat com guardas)
# ─────────────────────────────────────────────────────────────────────────────
Som = FumacaCloud


# ─────────────────────────────────────────────────────────────────────────────
#  EMP RING  (efeito visual apenas)
# ─────────────────────────────────────────────────────────────────────────────
class EMPRing(pygame.sprite.Sprite):
    def __init__(self, game, x, y, raio_max):
        super().__init__(game.todas_as_sprites, game.efeitos)
        self.game = game
        self.pos  = pygame.math.Vector2(x, y)
        self.raio = 5
        self.raio_max = raio_max
        self._alpha = 255
        self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        self.raio += 10
        self._alpha = max(0, int(255 * (1 - self.raio / self.raio_max)))
        if self.raio >= self.raio_max:
            self.kill()

    def desenhar(self, superficie, camera_x=0, camera_y=0):
        if self.raio <= 0:
            return
        cx = int(self.pos.x - camera_x)
        cy = int(self.pos.y - camera_y)
        for offset in (0, 10, 20):
            r = max(1, int(self.raio) - offset)
            a = max(0, self._alpha - offset * 6)
            pygame.draw.circle(superficie, (0, 220, 255, a), (cx, cy), r, 2)
        # Inner fill glow
        glow_r = max(1, int(self.raio * 0.4))
        pygame.draw.circle(superficie, (0, 180, 255, max(0, int(self._alpha * 0.15))),
                           (cx, cy), glow_r)


# ─────────────────────────────────────────────────────────────────────────────
#  PARTICULA
# ─────────────────────────────────────────────────────────────────────────────
class Particula(pygame.sprite.Sprite):
    def __init__(self, game, x, y, cor, vel_x=None, vel_y=None, vida_ms=450):
        super().__init__(game.todas_as_sprites, game.particulas)
        self.game = game
        self.pos  = pygame.math.Vector2(x, y)
        self.vel  = pygame.math.Vector2(
            vel_x if vel_x is not None else random.uniform(-2.5, 2.5),
            vel_y if vel_y is not None else random.uniform(-3.5, -0.5),
        )
        self.cor      = cor
        self.vida_ms  = vida_ms
        self._nasc    = pygame.time.get_ticks()
        self.tamanho  = random.randint(2, 4)
        self.image = pygame.Surface((self.tamanho * 2 + 2, self.tamanho * 2 + 2), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        agora    = pygame.time.get_ticks()
        prog     = (agora - self._nasc) / self.vida_ms
        if prog >= 1.0:
            self.kill()
            return
        self.vel.y += 0.15
        self.pos   += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        alpha = int(255 * (1 - prog))
        self.image.fill((0, 0, 0, 0))
        r = max(1, int(self.tamanho * (1 - prog * 0.5)))
        cx = self.image.get_width() // 2
        cy = self.image.get_height() // 2
        pygame.draw.circle(self.image, (*self.cor, alpha), (cx, cy), r)


# ─────────────────────────────────────────────────────────────────────────────
#  GUARDA  (FSM: PATRULHA → ALERTA → PERSEGUIÇÃO → ATORDOADO)
# ─────────────────────────────────────────────────────────────────────────────
class Guarda(pygame.sprite.Sprite):
    TAMANHO = assets_loader.GUARD_W
    COR_ESTADOS = {
        "PATRULHA":    constantes.VERDE,
        "ALERTA":      constantes.AMARELO,
        "PERSEGUICAO": constantes.VERMELHO,
        "ATORDOADO":   constantes.CIANO,
    }

    def __init__(self, game, cx, cy, waypoints, papel="patrulheiro"):
        super().__init__(game.todas_as_sprites, game.guardas)
        self.game  = game
        self.papel = papel
        self.perfil = self._perfil_por_papel(papel)
        W, H = assets_loader.GUARD_W, assets_loader.GUARD_H
        self.image = pygame.Surface((W, H), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(cx, cy))
        self.pos   = pygame.math.Vector2(cx, cy)

        self.waypoints      = [pygame.math.Vector2(wp) for wp in waypoints]
        self.waypoint_atual = 0

        self.estado = "PATRULHA"

        if len(self.waypoints) > 1:
            d = self.waypoints[1] - self.waypoints[0]
            self.direcao = d.normalize() if d.length() > 0 else pygame.math.Vector2(1, 0)
        else:
            self.direcao = pygame.math.Vector2(1, 0)

        self.alvo_investigar = None
        self.chegou_ao_alvo  = False
        self.tempo_chegada   = 0
        self.pontos_busca    = []
        self.indice_busca    = 0

        self.ultimo_avistamento = None
        self.tempo_inicio_perda = None

        agora = pygame.time.get_ticks()
        self.percepcao = 0.0
        self._ultimo_tick_percepcao    = agora
        self._ultimo_alerta_compartilhado = 0
        self._tempo_atordoado_fim      = 0

        self._ultima_pos_registro  = self.pos.copy()
        self._tempo_ultimo_progresso = agora
        self._contador_travado     = 0
        self._espera_patrulha_ate  = 0
        self._desvio_patrulha      = pygame.math.Vector2(0, 0)
        self._sentinela_tempo_giro = 0

        self._anim_counter  = 0
        self._frames_dir    = assets_loader.guard_walk_frames(papel, n=4)
        self._frames_esq    = assets_loader.guard_walk_frames_left(papel, n=4)
        self._frame_idle    = assets_loader.guard_idle(papel)

        self._redesenhar()

    def _perfil_por_papel(self, papel):
        perfis = {
            "patrulheiro": {"fator_vel": 1.00, "fator_percepcao": 1.00,
                            "fator_visao": 1.00, "fator_audicao": 1.00},
            "sentinela":   {"fator_vel": 0.80, "fator_percepcao": 1.08,
                            "fator_visao": 1.20, "fator_audicao": 0.95},
            "cacador":     {"fator_vel": 1.18, "fator_percepcao": 1.20,
                            "fator_visao": 1.05, "fator_audicao": 1.15},
        }
        return perfis.get(papel, perfis["patrulheiro"])

    def ativar_atordoamento(self, duracao_ms):
        self._tempo_atordoado_fim = pygame.time.get_ticks() + duracao_ms
        self.estado    = "ATORDOADO"
        self.percepcao = 0.0
        self._contador_travado = 0
        # Gera partículas elétricas
        for _ in range(6):
            Particula(self.game, self.pos.x, self.pos.y,
                      constantes.CIANO,
                      vel_x=random.uniform(-3, 3),
                      vel_y=random.uniform(-3, 0),
                      vida_ms=300)

    def _redesenhar(self):
        self._anim_counter = (self._anim_counter + 1) % (4 * 8)
        idx = (self._anim_counter // 8) % 4

        if self.direcao.x >= 0:
            frame = self._frames_dir[idx]
        else:
            frame = self._frames_esq[idx]

        if self.estado == "ATORDOADO":
            frame = frame.copy()
            W = frame.get_width()
            # Estrelinhas de atordoamento acima da cabeça
            for ox, oy_off, r in ((W // 2, 1, 3), (W // 2 - 5, 4, 2), (W // 2 + 5, 4, 2)):
                pygame.draw.circle(frame, (0, 220, 255), (ox, oy_off), r)

        self.image = frame

    def update(self):
        if self.estado == "ATORDOADO":
            if pygame.time.get_ticks() >= self._tempo_atordoado_fim:
                self._mudar_estado("PATRULHA")
            else:
                self.direcao = self.direcao.rotate(3)
                if self.direcao.length_squared() == 0:
                    self.direcao = pygame.math.Vector2(1, 0)
            self._redesenhar()
            return

        detectou = self._atualizar_percepcao()

        if self.estado == "PATRULHA":
            self._patrulhar()
            if detectou:
                self._mudar_estado("PERSEGUICAO")
            elif self._pode_ouvir():
                self._mudar_estado("ALERTA")

        elif self.estado == "ALERTA":
            self._investigar()
            if detectou:
                self._mudar_estado("PERSEGUICAO")

        elif self.estado == "PERSEGUICAO":
            self._perseguir()

        self._monitorar_travamento()
        self._redesenhar()

    def _mudar_estado(self, novo):
        self.estado = novo
        if novo == "ALERTA":
            self.chegou_ao_alvo = False
            self._preparar_busca_alerta()
            self.percepcao = max(self.percepcao, 35.0)
        elif novo == "PERSEGUICAO":
            self.ultimo_avistamento = pygame.math.Vector2(self.game.jogador.rect.center)
            self.tempo_inicio_perda = None
            self.pontos_busca  = []
            self.indice_busca  = 0
            self.percepcao     = constantes.PERCEPCAO_MAX
            self._compartilhar_alerta()
        elif novo == "PATRULHA":
            self._espera_patrulha_ate = pygame.time.get_ticks() + random.randint(120, 300)
            self._desvio_patrulha    = pygame.math.Vector2(0, 0)
            self.percepcao = min(self.percepcao, 24.0)
        self._contador_travado       = 0
        self._tempo_ultimo_progresso = pygame.time.get_ticks()
        self._ultima_pos_registro    = self.pos.copy()

    def _atualizar_percepcao(self):
        agora = pygame.time.get_ticks()
        dt    = max(0.0, (agora - self._ultimo_tick_percepcao) / 1000.0)
        self._ultimo_tick_percepcao = agora

        jogador   = self.game.jogador
        dist      = (pygame.math.Vector2(jogador.rect.center) - self.pos).length()
        raio_imediato = constantes.RAIO_PERSEGUICAO_IMEDIATA + self.TAMANHO * 0.5

        if not jogador.is_hidden and dist <= raio_imediato:
            self.percepcao = constantes.PERCEPCAO_MAX
            return True

        visivel = self._pode_ver_jogador()
        if visivel:
            bonus = 1.35 if dist <= max(55, self.game.raio_visao * 0.35) else 1.0
            self.percepcao += (constantes.GANHO_PERCEPCAO_POR_SEG * dt
                               * self.game.dificuldade_escala
                               * bonus
                               * self.perfil["fator_percepcao"])
        else:
            self.percepcao -= (constantes.PERDA_PERCEPCAO_POR_SEG * 0.82) * dt

        self.percepcao = max(0.0, min(constantes.PERCEPCAO_MAX, self.percepcao))
        return self.percepcao >= constantes.PERCEPCAO_MAX * 0.72

    def _compartilhar_alerta(self):
        agora = pygame.time.get_ticks()
        if agora - self._ultimo_alerta_compartilhado < constantes.COOLDOWN_ALERTA_COMPARTILHADO_MS:
            return
        self._ultimo_alerta_compartilhado = agora
        for outro in self.game.guardas:
            if outro is self: continue
            if (outro.pos - self.pos).length() > constantes.RAIO_COMUNICACAO_GUARDA: continue
            outro.alvo_investigar = pygame.math.Vector2(self.ultimo_avistamento)
            if outro.estado == "PATRULHA":
                outro._mudar_estado("ALERTA")
            elif outro.estado == "ALERTA":
                outro.percepcao = max(outro.percepcao, 45.0)

    def _ponto_livre(self, centro):
        if not (8 <= centro.x <= self.game.mundo_largura - 8 and
                8 <= centro.y <= self.game.mundo_altura - 8):
            return False
        teste = pygame.Rect(0, 0, self.TAMANHO, self.TAMANHO)
        teste.center = (int(centro.x), int(centro.y))
        for ob in self.game.obstaculos:
            if teste.colliderect(ob.rect):
                return False
        return True

    def _distancia_livre_na_direcao(self, direcao, max_dist=100):
        if direcao.length_squared() == 0: return 0
        d = direcao.normalize()
        for dist in range(8, max_dist + 1, 8):
            if not self._ponto_livre(self.pos + d * dist):
                return dist - 8
        return max_dist

    def _ajustar_direcao_livre(self):
        candidatos = [
            self.direcao, self.direcao.rotate(45), self.direcao.rotate(-45),
            self.direcao.rotate(90), self.direcao.rotate(-90),
            self.direcao.rotate(135), self.direcao.rotate(-135),
            -self.direcao,
            pygame.math.Vector2(1, 0), pygame.math.Vector2(-1, 0),
            pygame.math.Vector2(0, 1), pygame.math.Vector2(0, -1),
        ]
        melhor_dir, melhor_dist = self.direcao, -1
        for c in candidatos:
            if c.length_squared() == 0: continue
            livre = self._distancia_livre_na_direcao(c, 96)
            if livre > melhor_dist:
                melhor_dist, melhor_dir = livre, c.normalize()
        if melhor_dist >= 16:
            self.direcao = melhor_dir

    def _preparar_busca_alerta(self):
        if self.alvo_investigar is None:
            self.pontos_busca = []
            self.indice_busca = 0
            return
        base = pygame.math.Vector2(self.alvo_investigar)
        T    = constantes.TAM_TILE
        offsets = [(0,0),(T,0),(-T,0),(0,T),(0,-T),(T,T),(-T,T),(T,-T),(-T,-T)]
        random.shuffle(offsets)
        pontos = []
        for dx, dy in offsets:
            x = max(16, min(self.game.mundo_largura  - 16, int(base.x + dx)))
            y = max(16, min(self.game.mundo_altura - 16, int(base.y + dy)))
            c = pygame.math.Vector2(x, y)
            if self._ponto_livre(c):
                pontos.append(c)
        self.pontos_busca = pontos if pontos else [base]
        self.indice_busca = 0
        self.alvo_investigar = self.pontos_busca[0]

    def _mover_para(self, alvo_vec, velocidade):
        direcao = alvo_vec - self.pos
        if direcao.length() < 1: return
        self.direcao = direcao.normalize()
        mov = self.direcao * velocidade

        self.pos.x += mov.x
        self.rect.centerx = int(self.pos.x)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if mov.x > 0: self.rect.right = hit.rect.left
            else:         self.rect.left  = hit.rect.right
            self.pos.x = float(self.rect.centerx)

        self.pos.y += mov.y
        self.rect.centery = int(self.pos.y)
        for hit in pygame.sprite.spritecollide(self, self.game.obstaculos, False):
            if mov.y > 0: self.rect.bottom = hit.rect.top
            else:         self.rect.top    = hit.rect.bottom
            self.pos.y = float(self.rect.centery)

    def _patrulhar(self):
        if not self.waypoints: return
        if self.papel == "sentinela":
            self._patrulhar_sentinela()
            return
        agora = pygame.time.get_ticks()
        if agora < self._espera_patrulha_ate: return
        alvo = self.waypoints[self.waypoint_atual] + self._desvio_patrulha
        if (alvo - self.pos).length() < 5:
            if len(self.waypoints) > 2 and random.random() < 0.38:
                candidatos = [i for i in range(len(self.waypoints)) if i != self.waypoint_atual]
                self.waypoint_atual = random.choice(candidatos)
            else:
                self.waypoint_atual = (self.waypoint_atual + 1) % len(self.waypoints)
            self._espera_patrulha_ate = agora + random.randint(140, 420)
            self._desvio_patrulha    = pygame.math.Vector2(random.randint(-9, 9), random.randint(-9, 9))
        else:
            self._mover_para(alvo, self.game.vel_patrulha * self.perfil["fator_vel"])

    def _patrulhar_sentinela(self):
        agora = pygame.time.get_ticks()
        if agora >= self._sentinela_tempo_giro:
            ang = random.uniform(-0.75, 0.75)
            self.direcao = self.direcao.rotate_rad(ang)
            if self.direcao.length_squared() == 0:
                self.direcao = pygame.math.Vector2(1, 0)
            self._ajustar_direcao_livre()
            self._sentinela_tempo_giro = agora + random.randint(500, 1200)
        base = self.waypoints[0]
        if (base - self.pos).length() > 22:
            self._mover_para(base, self.game.vel_patrulha * 0.7)

    def _investigar(self):
        if self.alvo_investigar is None:
            if self.pontos_busca and self.indice_busca < len(self.pontos_busca):
                self.alvo_investigar = self.pontos_busca[self.indice_busca]
            else:
                self._mudar_estado("PATRULHA")
            return
        dist = (self.alvo_investigar - self.pos).length()
        if dist > 6:
            self._mover_para(self.alvo_investigar, self.game.vel_alerta * self.perfil["fator_vel"])
            self.chegou_ao_alvo = False
        else:
            if not self.chegou_ao_alvo:
                self.chegou_ao_alvo = True
                self.tempo_chegada  = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.tempo_chegada >= max(300, self.game.timer_alerta // 3):
                self.indice_busca += 1
                if self.indice_busca < len(self.pontos_busca):
                    self.alvo_investigar = self.pontos_busca[self.indice_busca]
                    self.chegou_ao_alvo  = False
                else:
                    self.alvo_investigar = None
                    self.pontos_busca    = []
                    self._mudar_estado("PATRULHA")

    def _perseguir(self):
        if self._pode_ver_jogador():
            self.ultimo_avistamento = pygame.math.Vector2(self.game.jogador.rect.center)
            self.tempo_inicio_perda = None
            self._mover_para(self.ultimo_avistamento, self.game.vel_perseguicao * self.perfil["fator_vel"])
            self._compartilhar_alerta()
        else:
            if self.tempo_inicio_perda is None:
                self.tempo_inicio_perda = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.tempo_inicio_perda >= self.game.tempo_perda_jogador:
                if self.ultimo_avistamento:
                    self.alvo_investigar = self.ultimo_avistamento.copy()
                self._mudar_estado("ALERTA")
                return
            if self.ultimo_avistamento:
                self._mover_para(self.ultimo_avistamento, self.game.vel_perseguicao * self.perfil["fator_vel"])

    def _monitorar_travamento(self):
        if self.estado not in ("PATRULHA", "ALERTA", "PERSEGUICAO"): return
        agora = pygame.time.get_ticks()
        if agora - self._tempo_ultimo_progresso < 240: return
        if (self.pos - self._ultima_pos_registro).length() < 1.2:
            self._contador_travado += 1
            if self._contador_travado >= 4:
                self._destravar()
                self._contador_travado = 0
        else:
            self._contador_travado = 0
        self._ultima_pos_registro    = self.pos.copy()
        self._tempo_ultimo_progresso = agora

    def _destravar(self):
        self._tentar_deslocar_local()
        self._ajustar_direcao_livre()
        if self.estado == "PATRULHA":
            if len(self.waypoints) > 1:
                candidatos = [i for i in range(len(self.waypoints)) if i != self.waypoint_atual]
                self.waypoint_atual = random.choice(candidatos)
            self._desvio_patrulha    = pygame.math.Vector2(random.randint(-12, 12), random.randint(-12, 12))
            self._espera_patrulha_ate = pygame.time.get_ticks() + random.randint(80, 260)
        elif self.estado == "ALERTA":
            if self.indice_busca + 1 < len(self.pontos_busca):
                self.indice_busca += 1
                self.alvo_investigar = self.pontos_busca[self.indice_busca]
            else:
                centro = pygame.math.Vector2(
                    random.randint(20, self.game.mundo_largura - 20),
                    random.randint(20, self.game.mundo_altura - 20),
                )
                self.alvo_investigar = centro
                self._preparar_busca_alerta()
            self.chegou_ao_alvo = False
        elif self.estado == "PERSEGUICAO" and self.ultimo_avistamento is not None:
            ajuste = pygame.math.Vector2(random.randint(-24, 24), random.randint(-24, 24))
            novo = self.ultimo_avistamento + ajuste
            novo.x = max(16, min(self.game.mundo_largura - 16, novo.x))
            novo.y = max(16, min(self.game.mundo_altura - 16, novo.y))
            self.ultimo_avistamento = novo
        self._tempo_ultimo_progresso = pygame.time.get_ticks()
        self._ultima_pos_registro    = self.pos.copy()

    def _tentar_deslocar_local(self):
        direcoes = [
            pygame.math.Vector2(1,0), pygame.math.Vector2(-1,0),
            pygame.math.Vector2(0,1), pygame.math.Vector2(0,-1),
            pygame.math.Vector2(1,1), pygame.math.Vector2(-1,1),
            pygame.math.Vector2(1,-1), pygame.math.Vector2(-1,-1),
        ]
        random.shuffle(direcoes)
        for d in direcoes:
            c = self.pos + d.normalize() * 8
            if self._ponto_livre(c):
                self.pos = c
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                self.direcao = d.normalize()
                self._ajustar_direcao_livre()
                return

    def _pode_ver_jogador(self):
        if self.estado == "ATORDOADO": return False
        jogador = self.game.jogador
        if jogador.is_hidden: return False
        vetor    = pygame.math.Vector2(jogador.rect.center) - self.pos
        distancia = vetor.length()
        raio_local = self.game.raio_visao * self.perfil["fator_visao"]
        if distancia > raio_local: return False
        if distancia < 1 or self.direcao.length() == 0: return True
        dot    = vetor.normalize().dot(self.direcao.normalize())
        dot    = max(-1.0, min(1.0, dot))
        angulo = math.degrees(math.acos(dot))
        if angulo > self.game.angulo_cone: return False
        return self._tem_linha_de_visao(pygame.math.Vector2(jogador.rect.center))

    def _tem_linha_de_visao(self, alvo):
        x1, y1 = int(self.pos.x), int(self.pos.y)
        x2, y2 = int(alvo.x), int(alvo.y)
        for ob in self.game.obstaculos:
            hitbox = ob.rect.inflate(-4, -4)
            if hitbox.width <= 0 or hitbox.height <= 0: hitbox = ob.rect
            if hitbox.clipline((x1, y1), (x2, y2)): return False
        for fumaca in self.game.fumacas:
            if fumaca.bloqueia_linha(x1, y1, x2, y2): return False
        return True

    def _pode_ouvir(self):
        for som in self.game.sons:
            if (self.pos - som.pos).length() <= som.raio * self.game.fator_audicao_guarda * self.perfil["fator_audicao"]:
                self.alvo_investigar = pygame.math.Vector2(som.pos)
                return True
        return False

    def desenhar_cone(self, superficie, camera_x=0, camera_y=0):
        if self.estado == "ATORDOADO" or self.direcao.length() == 0:
            return
        alpha_tabela = {"PATRULHA": 55, "ALERTA": 75, "PERSEGUICAO": 95}
        cor   = (*self.COR_ESTADOS[self.estado], alpha_tabela.get(self.estado, 55))
        centro = (int(self.pos.x - camera_x), int(self.pos.y - camera_y))
        d_norm  = self.direcao.normalize()
        meio    = math.radians(self.game.angulo_cone)
        raio    = self.game.raio_visao

        pontos = [centro]
        N = 22
        for i in range(N + 1):
            t   = i / N
            ang = -meio + 2 * meio * t
            ca, sa = math.cos(ang), math.sin(ang)
            dx = d_norm.x * ca - d_norm.y * sa
            dy = d_norm.x * sa + d_norm.y * ca
            pontos.append((centro[0] + dx * raio, centro[1] + dy * raio))
        pygame.draw.polygon(superficie, cor, pontos)
