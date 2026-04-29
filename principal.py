import pygame
import random
import math
import struct
import constantes
import sprites
import mapa
import assets_loader


# ─────────────────────────────────────────────────────────────────────────────
#  GAME
# ─────────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.tela    = pygame.display.set_mode((constantes.LARGURA, constantes.ALTURA))
        pygame.display.set_caption(constantes.TITULO_JOGO)
        self.relogio = pygame.time.Clock()
        self.fonte   = pygame.font.match_font(constantes.FONTE)
        self.esta_rodando = True

        self.overlay   = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        self._bg_cache = None

        self._shake_duracao   = 0
        self._shake_inicio    = 0
        self._shake_intensidade = 0
        self._shake_offset    = (0, 0)

        self.opcoes_dificuldade = [
            ("FACIL", 0.88),
            ("MEDIO", 1.00),
            ("DIFICIL", 1.18),
        ]

        self._sons = self._init_sons()
        self._menu_particulas = []
        self._menu_timer = pygame.time.get_ticks()
        self._scanlines  = self._gerar_scanlines()
        self._vignette   = self._gerar_vignette()

    # ─────────────────────────────────────────────────────────────────────────
    #  SONS SINTETIZADOS
    # ─────────────────────────────────────────────────────────────────────────
    def _init_sons(self):
        tabela = {
            "alerta":    (780,  90,  0.28, True),
            "capturado": (200, 380,  0.35, True),
            "intel":     (1100, 110, 0.22, True),
            "emp":       (440,  260, 0.30, True),
            "fumaca":    (560,   80, 0.20, True),
            "vitoria":   (660,  220, 0.28, True),
            "vida":      (880,  120, 0.25, True),
            "bloqueado": (300,   60, 0.20, True),
        }
        sons = {}
        for nome, (freq, dur, vol, fade) in tabela.items():
            sons[nome] = self._beep(freq, dur, vol, fade)
        return sons

    def _beep(self, freq, dur_ms, volume=0.3, fade=True):
        rate = 22050
        n    = int(rate * dur_ms / 1000)
        buf  = bytearray(n * 4)
        for i in range(n):
            t  = i / rate
            f  = (1.0 - i / n) if fade else 1.0
            val = int(volume * f * 32767 * math.sin(2 * math.pi * freq * t))
            val = max(-32768, min(32767, val))
            packed = struct.pack('<h', val)
            buf[i * 4:i * 4 + 2] = packed
            buf[i * 4 + 2:i * 4 + 4] = packed
        try:
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception:
            return None

    def _tocar(self, nome):
        s = self._sons.get(nome)
        if s:
            try:
                s.play()
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    #  EFEITOS DE TELA
    # ─────────────────────────────────────────────────────────────────────────
    def _gerar_scanlines(self):
        surf = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        for y in range(0, constantes.ALTURA, 3):
            pygame.draw.line(surf, (0, 0, 0, 22), (0, y), (constantes.LARGURA, y), 1)
        return surf

    def _gerar_vignette(self):
        surf = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, 120), (0, 0, constantes.LARGURA, constantes.ALTURA), 50)
        return surf

    # ─────────────────────────────────────────────────────────────────────────
    #  INICIALIZAR PARTIDA
    # ─────────────────────────────────────────────────────────────────────────
    def novo_jogo(self):
        self.estado_tela = "MENU"
        self.indice_dificuldade = 1
        self.dificuldade_nome, self.dificuldade_escala = self.opcoes_dificuldade[1]

        self.total_fases    = len(mapa.FASES)
        self.fase_atual_idx = 0
        self.nome_fase_atual = ""
        self.em_transicao_fase   = False
        self.proxima_fase_idx    = None
        self.mensagem_transicao  = ""
        self.tempo_inicio_transicao = 0
        self.duracao_transicao_ms   = 1400

        self.nivel            = 1
        self.distancia_frente = 0.0
        self.tempo_inicio_partida = 0
        self._acumulado_pausa_ms  = 0
        self._inicio_pausa_ms     = 0
        self.heat                 = 0.0
        self._ultimo_tick_heat    = pygame.time.get_ticks()
        self.ultimo_tempo_fumaca  = -constantes.COOLDOWN_FUMACA_MS
        self._saida_bloqueada_feedback_ate = 0
        self.resultados_fase     = []
        self.score_total_campanha = 0

        # Vidas
        self.lives = constantes.LIVES_INICIAIS

        # EMP
        self._emp_ultimo_uso = -constantes.EMP_COOLDOWN_MS

        self.vel_patrulha    = constantes.VEL_PATRULHA
        self.vel_alerta      = constantes.VEL_ALERTA
        self.vel_perseguicao = constantes.VEL_PERSEGUICAO
        self.raio_visao      = constantes.RAIO_VISAO
        self.angulo_cone     = constantes.ANGULO_CONE
        self.timer_alerta    = constantes.TIMER_ALERTA
        self.tempo_perda_jogador     = constantes.TEMPO_PERDA_JOGADOR
        self.fator_audicao_guarda    = 1.0

        self._carregar_fase(self.fase_atual_idx)
        self._atualizar_parametros_dificuldade()

        self.jogando   = True
        self.game_over = False
        self.vitoria   = False
        self._rodar()

    def _iniciar_missao(self):
        self.estado_tela    = "JOGANDO"
        self.game_over      = False
        self.vitoria        = False
        self.em_transicao_fase = False
        self.proxima_fase_idx  = None
        self.mensagem_transicao = ""
        self._acumulado_pausa_ms = 0
        self._inicio_pausa_ms    = 0
        self.tempo_inicio_partida = pygame.time.get_ticks()
        self._shake_offset       = (0, 0)
        self.heat                = 0.0
        self._ultimo_tick_heat   = pygame.time.get_ticks()
        self.ultimo_tempo_fumaca = -constantes.COOLDOWN_FUMACA_MS
        self._saida_bloqueada_feedback_ate = 0
        self._emp_ultimo_uso     = -constantes.EMP_COOLDOWN_MS
        self._atualizar_camera()
        self._atualizar_parametros_dificuldade()

    def _ativar_shake(self, intensidade=5, duracao_ms=160):
        self._shake_intensidade = max(self._shake_intensidade, intensidade)
        self._shake_duracao     = max(self._shake_duracao, duracao_ms)
        self._shake_inicio      = pygame.time.get_ticks()

    def _atualizar_shake(self):
        if self._shake_duracao <= 0:
            self._shake_offset = (0, 0)
            return
        elapsed = pygame.time.get_ticks() - self._shake_inicio
        if elapsed >= self._shake_duracao:
            self._shake_duracao    = 0
            self._shake_intensidade = 0
            self._shake_offset     = (0, 0)
            return
        t = 1 - (elapsed / self._shake_duracao)
        m = max(1, int(self._shake_intensidade * t))
        self._shake_offset = (random.randint(-m, m), random.randint(-m, m))

    def _carregar_fase(self, fase_idx):
        self.fase_atual_idx = fase_idx
        fase = mapa.FASES[fase_idx]
        self.nome_fase_atual  = fase["nome"]
        self.mundo_largura    = len(fase["layout"][0]) * constantes.TAM_TILE
        self.mundo_altura     = len(fase["layout"]) * constantes.TAM_TILE
        self.camera_x = 0
        self.camera_y = 0

        self.todas_as_sprites = pygame.sprite.Group()
        self.obstaculos       = pygame.sprite.Group()
        self.caixas           = pygame.sprite.Group()
        self.guardas          = pygame.sprite.Group()
        self.sons             = pygame.sprite.Group()
        self.fumacas          = pygame.sprite.Group()
        self.intels           = pygame.sprite.Group()
        self.efeitos          = pygame.sprite.Group()
        self.particulas       = pygame.sprite.Group()

        self._saida = None
        for li, linha in enumerate(fase["layout"]):
            for ci, tile in enumerate(linha):
                x = ci * constantes.TAM_TILE
                y = li * constantes.TAM_TILE
                if   tile == '#': sprites.Parede(self, x, y)
                elif tile == 'B': sprites.Caixa(self, x, y)
                elif tile == 'E': self._saida = sprites.Saida(self, x, y)
                elif tile == 'I': sprites.Intel(self, x, y)

        ic, il = fase["inicio"]
        self.jogador = sprites.Jogador(
            self,
            ic * constantes.TAM_TILE,
            il * constantes.TAM_TILE,
        )

        for idx, dados in enumerate(fase["guardas"]):
            papel = self._papel_guarda_por_indice(idx)
            rota  = dados
            if isinstance(dados, dict):
                rota  = dados.get("rota", [])
                papel = dados.get("papel", papel)
            wps = [self._tile_para_centro(tx, ty) for tx, ty in rota]
            cx, cy = wps[0]
            sprites.Guarda(self, cx, cy, wps, papel=papel)

        self.intel_total_fase    = len(self.intels)
        self.intel_coletada_fase = 0

        self.tempo_inicio_fase      = pygame.time.get_ticks()
        self._amostras_heat_fase    = 0
        self._acumulado_heat_fase   = 0.0
        self.detectacoes_fase       = 0
        self._guardas_perseguindo_prev = set()
        self._fase_resultado_registrado = False
        self._ultimo_x_jogador      = float(self.jogador.rect.centerx)
        self._bg_cache              = None
        self._atualizar_camera()

    def _atualizar_camera(self):
        ax = self.jogador.rect.centerx - constantes.LARGURA  // 2
        ay = self.jogador.rect.centery - constantes.ALTURA // 2
        self.camera_x = max(0, min(ax, max(0, self.mundo_largura  - constantes.LARGURA)))
        self.camera_y = max(0, min(ay, max(0, self.mundo_altura - constantes.ALTURA)))

    def _papel_guarda_por_indice(self, idx):
        padrao = ["patrulheiro", "sentinela", "cacador", "patrulheiro"]
        return padrao[idx % len(padrao)]

    def _tile_para_centro(self, tx, ty):
        T = constantes.TAM_TILE
        return (tx * T + T // 2, ty * T + T // 2)

    # ─────────────────────────────────────────────────────────────────────────
    #  LOOP
    # ─────────────────────────────────────────────────────────────────────────
    def _rodar(self):
        while self.jogando:
            self.relogio.tick(constantes.FPS)
            self._eventos()
            self._atualizar_shake()
            if self.estado_tela == "JOGANDO":
                self._atualizar()
            self._desenhar()

    # ─────────────────────────────────────────────────────────────────────────
    #  EVENTOS
    # ─────────────────────────────────────────────────────────────────────────
    def _eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.jogando      = False
                self.esta_rodando = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.estado_tela == "JOGANDO" and not self.em_transicao_fase:
                    agora = pygame.time.get_ticks()
                    if agora - self.ultimo_tempo_fumaca >= constantes.COOLDOWN_FUMACA_MS:
                        mx, my = event.pos
                        sprites.FumacaCloud(self, mx + self.camera_x, my + self.camera_y)
                        self.ultimo_tempo_fumaca = agora
                        self._tocar("fumaca")
                    else:
                        self._ativar_shake(2, 80)
                        self._tocar("bloqueado")

            if event.type == pygame.KEYDOWN:
                if self.estado_tela == "MENU":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.indice_dificuldade = (self.indice_dificuldade - 1) % len(self.opcoes_dificuldade)
                        self.dificuldade_nome, self.dificuldade_escala = self.opcoes_dificuldade[self.indice_dificuldade]
                        self._atualizar_parametros_dificuldade()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.indice_dificuldade = (self.indice_dificuldade + 1) % len(self.opcoes_dificuldade)
                        self.dificuldade_nome, self.dificuldade_escala = self.opcoes_dificuldade[self.indice_dificuldade]
                        self._atualizar_parametros_dificuldade()
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._iniciar_missao()
                    elif event.key == pygame.K_ESCAPE:
                        self.jogando = False
                        self.esta_rodando = False

                elif self.estado_tela == "JOGANDO":
                    if event.key == pygame.K_ESCAPE and not self.em_transicao_fase:
                        self.estado_tela    = "PAUSADO"
                        self._inicio_pausa_ms = pygame.time.get_ticks()
                    elif event.key == pygame.K_e and not self.em_transicao_fase:
                        self._usar_emp()

                elif self.estado_tela == "PAUSADO":
                    if event.key == pygame.K_ESCAPE:
                        self.estado_tela = "JOGANDO"
                        if self._inicio_pausa_ms > 0:
                            self._acumulado_pausa_ms += pygame.time.get_ticks() - self._inicio_pausa_ms
                        self._inicio_pausa_ms = 0
                    elif event.key == pygame.K_m:
                        self.jogando = False

                elif self.estado_tela == "FIM":
                    if event.key == pygame.K_r:
                        self.jogando = False
                    elif event.key == pygame.K_m:
                        self.jogando = False

                if event.key == pygame.K_F5:
                    self.jogando = False

    # ─────────────────────────────────────────────────────────────────────────
    #  EMP
    # ─────────────────────────────────────────────────────────────────────────
    def _usar_emp(self):
        agora = pygame.time.get_ticks()
        if agora - self._emp_ultimo_uso < constantes.EMP_COOLDOWN_MS:
            self._tocar("bloqueado")
            return
        self._emp_ultimo_uso = agora
        px = self.jogador.rect.centerx
        py = self.jogador.rect.centery
        sprites.EMPRing(self, px, py, constantes.EMP_RAIO)
        player_pos = pygame.math.Vector2(px, py)
        count = 0
        for guarda in self.guardas:
            if (guarda.pos - player_pos).length() <= constantes.EMP_RAIO:
                guarda.ativar_atordoamento(constantes.EMP_DURACAO_ATORDOADO_MS)
                count += 1
        if count > 0:
            self._ativar_shake(4, 120)
            self._tocar("emp")
        else:
            self._tocar("emp")
        # Partículas EMP
        for _ in range(12):
            ang = random.uniform(0, math.pi * 2)
            r   = random.uniform(20, 80)
            sprites.Particula(self, px + math.cos(ang) * r, py + math.sin(ang) * r,
                               constantes.CIANO, vida_ms=500)

    # ─────────────────────────────────────────────────────────────────────────
    #  ATUALIZAR
    # ─────────────────────────────────────────────────────────────────────────
    def _atualizar(self):
        if self.em_transicao_fase:
            if pygame.time.get_ticks() - self.tempo_inicio_transicao >= self.duracao_transicao_ms:
                self.em_transicao_fase = False
                if self.proxima_fase_idx is not None:
                    self._carregar_fase(self.proxima_fase_idx)
                    self.proxima_fase_idx = None
            return

        self.todas_as_sprites.update()
        self._atualizar_progressao()
        self._atualizar_heat()
        self._atualizar_metricas_fase()
        self._atualizar_camera()

        # Coleta de intel
        coletados = pygame.sprite.spritecollide(self.jogador, self.intels, dokill=True)
        if coletados:
            self.intel_coletada_fase += len(coletados)
            self.heat = min(constantes.HEAT_MAX, self.heat + 8 * len(coletados))
            self._ativar_shake(3, 120)
            self._tocar("intel")
            for _ in range(8):
                sprites.Particula(self,
                                   self.jogador.rect.centerx + random.randint(-10, 10),
                                   self.jogador.rect.centery + random.randint(-10, 10),
                                   constantes.CIANO, vida_ms=400)

        # Game over / vidas
        if not self.jogador.is_invencivel:
            for guarda in self.guardas:
                if (guarda.estado == "PERSEGUICAO"
                        and guarda.rect.colliderect(self.jogador.rect)):
                    self.lives -= 1
                    self._ativar_shake(10, 280)
                    self._tocar("capturado")
                    for _ in range(16):
                        sprites.Particula(self,
                                           self.jogador.rect.centerx,
                                           self.jogador.rect.centery,
                                           constantes.VERMELHO,
                                           vel_x=random.uniform(-4, 4),
                                           vel_y=random.uniform(-4, 1),
                                           vida_ms=500)
                    if self.lives <= 0:
                        self.game_over = True
                        self.estado_tela = "FIM"
                        self._registrar_resultado_fase(concluida=False)
                    else:
                        self.jogador.ativar_invencibilidade()
                    break

        # Vitória
        if self._saida and self.jogador.rect.colliderect(self._saida.rect):
            if self.intel_coletada_fase >= self.intel_total_fase:
                self._avancar_fase_ou_vencer()
            else:
                self._saida_bloqueada_feedback_ate = pygame.time.get_ticks() + 900
                self._ativar_shake(3, 100)
                self._tocar("bloqueado")

    def _avancar_fase_ou_vencer(self):
        proxima = self.fase_atual_idx + 1
        if proxima >= self.total_fases:
            self._registrar_resultado_fase(concluida=True)
            self.vitoria     = True
            self.estado_tela = "FIM"
            self._tocar("vitoria")
            return
        self._registrar_resultado_fase(concluida=True)
        self.em_transicao_fase    = True
        self.proxima_fase_idx     = proxima
        self.tempo_inicio_transicao = pygame.time.get_ticks()
        self.mensagem_transicao   = f"SETOR {proxima + 1}: {mapa.FASES[proxima]['nome']}"
        self._ativar_shake(4, 160)
        self._tocar("vitoria")

    def _atualizar_metricas_fase(self):
        self._acumulado_heat_fase += self.heat
        self._amostras_heat_fase  += 1
        perseguindo = {id(g) for g in self.guardas if g.estado == "PERSEGUICAO"}
        novos = perseguindo - self._guardas_perseguindo_prev
        if novos:
            self.detectacoes_fase += len(novos)
            self._tocar("alerta")
            for g in self.guardas:
                if id(g) in novos:
                    for _ in range(5):
                        sprites.Particula(self, g.rect.centerx, g.rect.top,
                                           constantes.AMARELO,
                                           vel_x=random.uniform(-2, 2),
                                           vel_y=random.uniform(-3, -0.5),
                                           vida_ms=350)
        self._guardas_perseguindo_prev = perseguindo

    def _calcular_score_fase(self, concluida):
        tempo_seg  = max(0, (pygame.time.get_ticks() - self.tempo_inicio_fase) // 1000)
        heat_medio = (self._acumulado_heat_fase / self._amostras_heat_fase) if self._amostras_heat_fase else 0.0
        if concluida:
            base = constantes.SCORE_BASE_FASE
        else:
            fracao = self.intel_coletada_fase / max(1, self.intel_total_fase)
            base   = int(constantes.SCORE_BASE_FASE * 0.35 * fracao)
        score = int(
            base
            - tempo_seg    * constantes.SCORE_PENALIDADE_TEMPO
            - self.detectacoes_fase * constantes.SCORE_PENALIDADE_DETECCAO
            - heat_medio   * constantes.SCORE_PENALIDADE_HEAT
        )
        return max(0, score), tempo_seg, heat_medio

    def _rank_por_score(self, score):
        if score >= 1700: return "S"
        if score >= 1350: return "A"
        if score >= 1000: return "B"
        if score >= 700:  return "C"
        return "D"

    def _registrar_resultado_fase(self, concluida):
        if self._fase_resultado_registrado: return
        score, tempo, heat = self._calcular_score_fase(concluida)
        resultado = {
            "fase":      self.fase_atual_idx + 1,
            "nome":      self.nome_fase_atual,
            "concluida": concluida,
            "tempo_seg": tempo,
            "detec":     self.detectacoes_fase,
            "heat_medio": heat,
            "score":     score,
            "rank":      self._rank_por_score(score),
        }
        self.resultados_fase.append(resultado)
        self.score_total_campanha += score
        self._fase_resultado_registrado = True

    def _score_preview_atual(self):
        score, _, _ = self._calcular_score_fase(concluida=True)
        return score, self._rank_por_score(score)

    def _atualizar_progressao(self):
        x_atual = float(self.jogador.rect.centerx)
        delta   = x_atual - self._ultimo_x_jogador
        if delta > 0:
            self.distancia_frente += delta
        self._ultimo_x_jogador = x_atual
        novo_nivel = 1 + int(self.distancia_frente // constantes.DISTANCIA_POR_NIVEL)
        if novo_nivel != self.nivel:
            self.nivel = novo_nivel
            self._atualizar_parametros_dificuldade()

    def _atualizar_heat(self):
        agora = pygame.time.get_ticks()
        dt    = max(0.0, (agora - self._ultimo_tick_heat) / 1000.0)
        self._ultimo_tick_heat = agora
        qa = sum(1 for g in self.guardas if g.estado == "ALERTA")
        qp = sum(1 for g in self.guardas if g.estado == "PERSEGUICAO")
        ganho = (qa * constantes.HEAT_GAIN_ALERTA_POR_SEG + qp * constantes.HEAT_GAIN_PERSEGUICAO_POR_SEG) * dt
        perda = constantes.HEAT_DECAY_POR_SEG * dt
        self.heat = min(constantes.HEAT_MAX, max(0.0, self.heat + ganho - perda))
        self._atualizar_parametros_dificuldade()

    def _atualizar_parametros_dificuldade(self):
        esc = max(0, self.nivel - 1)
        fd  = self.dificuldade_escala
        fh  = 1.0 + (self.heat / constantes.HEAT_MAX) * (constantes.HEAT_FATOR_MAX - 1.0)
        ft  = fd * fh
        self.vel_patrulha    = min(constantes.VEL_PATRULHA_MAX,    constantes.VEL_PATRULHA    * (1 + 0.05 * esc) * ft)
        self.vel_alerta      = min(constantes.VEL_ALERTA_MAX,      constantes.VEL_ALERTA      * (1 + 0.06 * esc) * ft)
        self.vel_perseguicao = min(constantes.VEL_PERSEGUICAO_MAX, constantes.VEL_PERSEGUICAO * (1 + 0.07 * esc) * ft)
        self.raio_visao      = min(constantes.RAIO_VISAO_MAX,      int((constantes.RAIO_VISAO + 6 * esc) * ft))
        self.angulo_cone     = min(constantes.ANGULO_CONE_MAX,     int((constantes.ANGULO_CONE + 1.5 * esc) * ft))
        self.timer_alerta    = max(constantes.TIMER_ALERTA_MIN,    int((constantes.TIMER_ALERTA - 120 * esc) / ft))
        self.tempo_perda_jogador = max(constantes.TEMPO_PERDA_JOGADOR_MIN, int((constantes.TEMPO_PERDA_JOGADOR - 90 * esc) / ft))
        self.fator_audicao_guarda = min(constantes.FATOR_AUDICAO_MAX, (1.0 + 0.04 * esc) * ft)

    # ─────────────────────────────────────────────────────────────────────────
    #  DESENHAR
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar(self):
        ox, oy   = self._shake_offset
        camx, camy = self.camera_x, self.camera_y

        self._desenhar_fundo((camx, camy), (ox, oy))

        for sprite in self.obstaculos:
            self.tela.blit(sprite.image, sprite.rect.move(-camx + ox, -camy + oy))

        if self._saida:
            self.tela.blit(self._saida.image, self._saida.rect.move(-camx + ox, -camy + oy))
            if self.intel_coletada_fase < self.intel_total_fase:
                self._desenhar_cadeado(self._saida.rect, camx, camy, ox, oy)

        for intel in self.intels:
            self.tela.blit(intel.image, intel.rect.move(-camx + ox, -camy + oy))

        # Overlay: cones + efeitos + fumaça
        self.overlay.fill((0, 0, 0, 0))
        for guarda in self.guardas:
            guarda.desenhar_cone(self.overlay, camx, camy)
        for som in self.sons:
            som.desenhar(self.overlay, camx, camy)
        for efeito in self.efeitos:
            efeito.desenhar(self.overlay, camx, camy)
        self.tela.blit(self.overlay, (ox, oy))

        # Partículas
        for p in self.particulas:
            self.tela.blit(p.image, p.rect.move(-camx + ox, -camy + oy))

        # Jogador
        self.tela.blit(self.jogador.image, self.jogador.rect.move(-camx + ox, -camy + oy))

        # Guardas
        for guarda in self.guardas:
            self.tela.blit(guarda.image, guarda.rect.move(-camx + ox, -camy + oy))

        # Barras de detecção e indicadores
        for guarda in self.guardas:
            self._desenhar_barra_deteccao(guarda, camx, camy, ox, oy)
            self._desenhar_indicador_guarda(guarda, camx, camy, ox, oy)

        # HUD
        if self.estado_tela != "MENU":
            self._desenhar_hud()

        # Scanlines + vignette
        self.tela.blit(self._scanlines, (0, 0))
        self.tela.blit(self._vignette, (0, 0))

        # Telas sobrepostas
        if self.estado_tela == "FIM" and self.game_over:
            self._tela_final("CAPTURADO!", constantes.VERMELHO)
        elif self.estado_tela == "FIM" and self.vitoria:
            self._tela_final("MISSAO CONCLUIDA!", constantes.VERDE)

        if self.em_transicao_fase:
            self._desenhar_transicao_fase()

        if self.estado_tela == "MENU":
            self._desenhar_menu()
        elif self.estado_tela == "PAUSADO":
            self._desenhar_pausa()

        pygame.display.flip()

    def _desenhar_cadeado(self, saida_rect, camx, camy, ox, oy):
        T = constantes.TAM_TILE
        cx = saida_rect.x - camx + 12 + ox
        cy = saida_rect.y - camy + 10 + oy
        cad = pygame.Rect(cx, cy, 16, 18)
        pygame.draw.rect(self.tela, (20, 20, 28), cad, border_radius=3)
        pygame.draw.rect(self.tela, (255, 180, 0), cad, 2, border_radius=3)
        pygame.draw.arc(self.tela, (255, 180, 0), (cx + 2, cy - 8, 12, 12), math.pi, 0, 2)

    def _desenhar_barra_deteccao(self, guarda, camx, camy, ox, oy):
        if guarda.estado == "ATORDOADO":
            # Ícone atordoado
            gx = guarda.rect.centerx - camx + ox
            gy = guarda.rect.top - camy + oy - 10
            pygame.draw.circle(self.tela, constantes.CIANO, (int(gx), int(gy)), 5, 2)
            pygame.draw.line(self.tela, constantes.CIANO, (int(gx) - 3, int(gy)), (int(gx) + 3, int(gy)), 2)
            return
        pct = guarda.percepcao / constantes.PERCEPCAO_MAX
        if pct < 0.05: return
        bw = 24
        bh = 4
        gx = guarda.rect.centerx - camx + ox
        gy = guarda.rect.top - camy + oy - 8
        pygame.draw.rect(self.tela, (15, 15, 25), (gx - bw // 2, gy, bw, bh))
        if pct < 0.4:      cor_bar = constantes.VERDE
        elif pct < 0.72:   cor_bar = constantes.AMARELO
        else:              cor_bar = constantes.VERMELHO
        fill = int(bw * pct)
        if fill > 0:
            pygame.draw.rect(self.tela, cor_bar, (gx - bw // 2, gy, fill, bh))
        pygame.draw.rect(self.tela, (70, 80, 110), (gx - bw // 2, gy, bw, bh), 1)

    def _desenhar_indicador_guarda(self, guarda, camx, camy, ox, oy):
        gx = guarda.rect.centerx - camx + ox
        gy = guarda.rect.top - camy + oy - 20
        if guarda.estado == "PERSEGUICAO":
            self._texto("!", 18, constantes.VERMELHO, gx, gy)
        elif guarda.estado == "ALERTA":
            self._texto("?", 16, constantes.AMARELO, gx, gy)

    # ─────────────────────────────────────────────────────────────────────────
    #  HUD
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar_hud(self):
        L = constantes.LARGURA
        A = constantes.ALTURA

        # ── Painel esquerdo: guardas ──────────────────────────────────────────
        num_guardas = len(list(self.guardas))
        painel_h = 44 + num_guardas * 20 + 24
        self._desenhar_painel(6, 6, 240, painel_h)
        self._texto_neon("GUARDAS", 11, constantes.CIANO, 14, 10, ancora="topleft")
        y = 26
        for i, g in enumerate(self.guardas, 1):
            cor   = sprites.Guarda.COR_ESTADOS[g.estado]
            papel = g.papel[:3].upper()
            self._texto(f"G{i}", 12, cor, 14, y, ancora="topleft")
            self._texto(f"{papel}", 11, constantes.CINZA, 32, y, ancora="topleft")
            self._texto(g.estado, 12, cor, 80, y, ancora="topleft")
            pct = g.percepcao / constantes.PERCEPCAO_MAX
            bw = 60
            pygame.draw.rect(self.tela, (15, 15, 25), (166, y + 1, bw, 10))
            if pct > 0.05:
                fc = constantes.VERDE if pct < 0.4 else (constantes.AMARELO if pct < 0.72 else constantes.VERMELHO)
                pygame.draw.rect(self.tela, fc, (166, y + 1, int(bw * pct), 10))
            pygame.draw.rect(self.tela, (60, 70, 100), (166, y + 1, bw, 10), 1)
            y += 20

        score_p, rank_p = self._score_preview_atual()
        self._texto(f"Det: {self.detectacoes_fase}", 11, constantes.CINZA, 14, y + 2, ancora="topleft")
        self._texto(f"Score: {score_p} [{rank_p}]", 11, constantes.BRANCO, 14, y + 16, ancora="topleft")

        # ── Vidas ─────────────────────────────────────────────────────────────
        lv_y = painel_h + 14
        self._desenhar_painel(6, lv_y, 240, 30)
        self._texto_neon("VIDAS", 11, constantes.CIANO, 14, lv_y + 4, ancora="topleft")
        for i in range(constantes.LIVES_INICIAIS):
            cor_v = constantes.VERMELHO if i < self.lives else (30, 20, 20)
            brd_v = constantes.VERMELHO if i < self.lives else (60, 40, 40)
            r = pygame.Rect(80 + i * 28, lv_y + 5, 20, 20)
            pygame.draw.rect(self.tela, cor_v, r, border_radius=4)
            pygame.draw.rect(self.tela, brd_v, r, 1, border_radius=4)

        # ── Painel direito: missão ────────────────────────────────────────────
        px = L - 262
        self._desenhar_painel(px, 6, 256, 152)
        self._texto_neon("MISSAO", 11, constantes.CIANO, px + 8, 10, ancora="topleft")
        self._texto(f"Setor {self.fase_atual_idx + 1}/{self.total_fases}", 13, constantes.BRANCO,
                    L - 10, 10, ancora="topright")
        self._texto(self.nome_fase_atual, 11, constantes.CINZA, L - 10, 26, ancora="topright")
        self._texto(f"Dificuldade: {self.dificuldade_nome}", 11, constantes.AMARELO,
                    L - 10, 40, ancora="topright")
        self._texto(f"Intel: {self.intel_coletada_fase}/{self.intel_total_fase}", 12, constantes.BRANCO,
                    L - 10, 54, ancora="topright")

        tempo_ms = pygame.time.get_ticks() - self.tempo_inicio_partida - self._acumulado_pausa_ms
        ts = max(0, tempo_ms // 1000)
        self._texto(f"Nivel {self.nivel}", 16, constantes.BRANCO, L - 10, 70, ancora="topright")
        self._texto(f"{ts // 60:02d}:{ts % 60:02d}", 18, constantes.CIANO, L - 10, 88, ancora="topright")

        # Barra nivel
        bw = 220
        bx = L - bw - 16
        by = 114
        prog = (self.distancia_frente % constantes.DISTANCIA_POR_NIVEL) / constantes.DISTANCIA_POR_NIVEL
        pygame.draw.rect(self.tela, (14, 16, 30), (bx, by, bw, 14), border_radius=7)
        fill = int(bw * prog)
        if fill > 0:
            pygame.draw.rect(self.tela, constantes.AZUL, (bx, by, fill, 14), border_radius=7)
            brilho = pygame.Surface((fill, 7), pygame.SRCALPHA)
            brilho.fill((100, 180, 255, 70))
            self.tela.blit(brilho, (bx, by + 1))
        pygame.draw.rect(self.tela, (60, 80, 130), (bx, by, bw, 14), 1, border_radius=7)
        self._texto("Prox. nivel", 10, constantes.CINZA, bx, by - 2, ancora="bottomleft")

        # Barra Heat
        hby = by + 28
        pct_h = self.heat / constantes.HEAT_MAX
        heat_r = int(80 + 175 * pct_h)
        heat_g = int(60 * (1 - pct_h))
        pygame.draw.rect(self.tela, (18, 12, 16), (bx, hby, bw, 12), border_radius=6)
        if pct_h > 0:
            pygame.draw.rect(self.tela, (heat_r, heat_g, 30),
                             (bx, hby, int(bw * pct_h), 12), border_radius=6)
        pygame.draw.rect(self.tela, (120, 40, 60), (bx, hby, bw, 12), 1, border_radius=6)
        self._texto("ALERTA GLOBAL", 10, constantes.BRANCO, bx, hby - 2, ancora="bottomleft")

        # ── Painel de habilidades (fundo esquerdo) ────────────────────────────
        self._desenhar_painel(6, A - 60, 340, 54)
        agora = pygame.time.get_ticks()

        # Fumaca
        rest_f = max(0, constantes.COOLDOWN_FUMACA_MS - (agora - self.ultimo_tempo_fumaca))
        if rest_f <= 0:
            cor_f, txt_f = constantes.VERDE, "FUMACA: PRONTO"
        else:
            cor_f, txt_f = constantes.AMARELO, f"FUMACA: {rest_f / 1000:.1f}s"
        self._texto("[Clique]", 10, constantes.CINZA, 14, A - 54, ancora="topleft")
        self._texto(txt_f, 13, cor_f, 14, A - 40, ancora="topleft")

        # EMP
        rest_e = max(0, constantes.EMP_COOLDOWN_MS - (agora - self._emp_ultimo_uso))
        if rest_e <= 0:
            cor_e, txt_e = constantes.CIANO, "EMP: PRONTO"
        else:
            cor_e, txt_e = constantes.CINZA, f"EMP: {rest_e / 1000:.1f}s"
        self._texto("[E]", 10, constantes.CINZA, 180, A - 54, ancora="topleft")
        self._texto(txt_e, 13, cor_e, 180, A - 40, ancora="topleft")
        self._texto("CTRL: Esconder | ESC: Pausa", 10, constantes.CINZA, 14, A - 20, ancora="topleft")

        # ── Mensagem saída bloqueada ──────────────────────────────────────────
        if pygame.time.get_ticks() < self._saida_bloqueada_feedback_ate:
            self._texto_neon("COLETE TODA A INTEL PARA LIBERAR A SAIDA", 14,
                             constantes.AMARELO, L // 2, 10, ancora="midtop")

        if self.jogador.is_hidden:
            self._texto_neon("[ ESCONDIDO ]", 16, constantes.VERDE, L // 2, 30, ancora="midtop")

        # ── Minimapa ──────────────────────────────────────────────────────────
        self._desenhar_minimapa()

    def _desenhar_minimapa(self):
        MW = 160
        MH = 80
        MX = constantes.LARGURA - MW - 8
        MY = constantes.ALTURA - MH - 8

        painel = pygame.Surface((MW, MH), pygame.SRCALPHA)
        painel.fill((6, 8, 18, 210))
        self.tela.blit(painel, (MX, MY))
        pygame.draw.rect(self.tela, constantes.CIANO, (MX, MY, MW, MH), 1)

        sx = MW / max(1, self.mundo_largura)
        sy = MH / max(1, self.mundo_altura)

        # Paredes
        for ob in self.obstaculos:
            wx = int(ob.rect.x * sx)
            wy = int(ob.rect.y * sy)
            ww = max(1, int(ob.rect.width * sx))
            wh = max(1, int(ob.rect.height * sy))
            pygame.draw.rect(self.tela, (38, 48, 80), (MX + wx, MY + wy, ww, wh))

        # Intel
        for it in self.intels:
            ix = int(it.rect.centerx * sx)
            iy = int(it.rect.centery * sy)
            pygame.draw.circle(self.tela, constantes.AMARELO, (MX + ix, MY + iy), 2)

        # Saída
        if self._saida:
            ex = int(self._saida.rect.centerx * sx)
            ey = int(self._saida.rect.centery * sy)
            pygame.draw.circle(self.tela, constantes.VERDE, (MX + ex, MY + ey), 3)

        # Guardas
        for g in self.guardas:
            gx = int(g.rect.centerx * sx)
            gy = int(g.rect.centery * sy)
            cor = sprites.Guarda.COR_ESTADOS.get(g.estado, constantes.CINZA)
            pygame.draw.circle(self.tela, cor, (MX + gx, MY + gy), 2)

        # Jogador
        px = int(self.jogador.rect.centerx * sx)
        py = int(self.jogador.rect.centery * sy)
        pygame.draw.circle(self.tela, constantes.CIANO, (MX + px, MY + py), 3)
        pygame.draw.circle(self.tela, constantes.BRANCO, (MX + px, MY + py), 3, 1)

        # Viewport
        vx = int(self.camera_x * sx)
        vy = int(self.camera_y * sy)
        vw = int(constantes.LARGURA * sx)
        vh = int(constantes.ALTURA * sy)
        pygame.draw.rect(self.tela, (80, 90, 160), (MX + vx, MY + vy, vw, vh), 1)

        self._texto("MAPA", 9, constantes.CIANO, MX + 3, MY + 2, ancora="topleft")

    # ─────────────────────────────────────────────────────────────────────────
    #  MENUS
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar_menu(self):
        # Atualizar partículas do menu
        agora = pygame.time.get_ticks()
        if agora - self._menu_timer > 120:
            self._menu_timer = agora
            if len(self._menu_particulas) < 40:
                self._menu_particulas.append({
                    "x": random.randint(0, constantes.LARGURA),
                    "y": constantes.ALTURA + 5,
                    "vy": -random.uniform(0.4, 1.2),
                    "r": random.randint(1, 3),
                    "a": random.randint(60, 180),
                    "cor": random.choice([constantes.CIANO, constantes.AZUL, constantes.MAGENTA]),
                })

        self._menu_particulas = [p for p in self._menu_particulas if p["y"] > -10]
        for p in self._menu_particulas:
            p["y"] += p["vy"]

        # Fundo
        s = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        s.fill((4, 6, 14, 200))
        self.tela.blit(s, (0, 0))

        # Partículas
        for p in self._menu_particulas:
            pygame.draw.circle(self.tela, p["cor"],
                               (int(p["x"]), int(p["y"])), p["r"])

        # Grid de fundo
        for x in range(0, constantes.LARGURA, 60):
            pygame.draw.line(self.tela, (0, 50, 80, 30), (x, 0), (x, constantes.ALTURA), 1)
        for y in range(0, constantes.ALTURA, 60):
            pygame.draw.line(self.tela, (0, 50, 80, 30), (0, y), (constantes.LARGURA, y), 1)

        L = constantes.LARGURA
        A = constantes.ALTURA
        larg = 580
        alt  = 360
        x0   = (L - larg) // 2
        y0   = (A - alt)  // 2

        self._desenhar_painel_cyber(x0, y0, larg, alt)

        # Título pulsante
        t = pygame.time.get_ticks() / 1000.0
        pulse = 0.85 + 0.15 * math.sin(t * 2.5)
        r_t = int(200 + 55 * pulse)
        g_t = int(220 * pulse)
        self._texto("STEALTH OPS", 56, (r_t, g_t, 255), L // 2, y0 + 20)
        self._texto("SOMBRA DIGITAL", 18, constantes.CIANO, L // 2, y0 + 84)
        self._texto("─── MODO CAMPANHA ───", 14, constantes.CINZA, L // 2, y0 + 108)

        self._texto("Selecione a dificuldade:", 16, constantes.BRANCO, L // 2, y0 + 138)

        base_y = y0 + 168
        for i, (nome, _) in enumerate(self.opcoes_dificuldade):
            selecionado = (i == self.indice_dificuldade)
            if selecionado:
                bar_r = pygame.Rect(x0 + 80, base_y + i * 38 - 4, larg - 160, 34)
                s2    = pygame.Surface((bar_r.width, bar_r.height), pygame.SRCALPHA)
                s2.fill((0, 180, 255, 18))
                self.tela.blit(s2, bar_r.topleft)
                pygame.draw.rect(self.tela, constantes.CIANO, bar_r, 1, border_radius=4)
                cor    = constantes.CIANO
                prefixo = "▶  "
            else:
                cor    = constantes.CINZA
                prefixo = "   "
            self._texto(f"{prefixo}{nome}", 26, cor, L // 2, base_y + i * 38)

        self._texto("↑ ↓ para escolher", 13, constantes.CINZA, L // 2, y0 + alt - 72)
        self._texto_neon("[ ENTER ] INICIAR MISSAO", 17, constantes.VERDE, L // 2, y0 + alt - 48)
        self._texto("ESC: sair", 12, constantes.CINZA, L // 2, y0 + alt - 22)

    def _desenhar_pausa(self):
        s = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.tela.blit(s, (0, 0))

        L, A = constantes.LARGURA, constantes.ALTURA
        larg, alt = 440, 210
        x0 = (L - larg) // 2
        y0 = (A - alt)  // 2
        self._desenhar_painel_cyber(x0, y0, larg, alt)
        self._texto_neon("PAUSADO", 46, constantes.CIANO, L // 2, y0 + 20)
        self._texto("ESC: continuar", 18, constantes.BRANCO, L // 2, y0 + 100)
        self._texto("M: voltar ao menu", 18, constantes.CINZA, L // 2, y0 + 130)
        self._texto_neon("MISSAO EM ANDAMENTO", 13, constantes.AMARELO, L // 2, y0 + 170)

    def _desenhar_transicao_fase(self):
        s = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        s.fill((4, 6, 14, 140))
        self.tela.blit(s, (0, 0))

        L, A = constantes.LARGURA, constantes.ALTURA
        larg, alt = 480, 130
        x0 = (L - larg) // 2
        y0 = (A - alt)  // 2
        self._desenhar_painel_cyber(x0, y0, larg, alt)
        self._texto_neon("SETOR LIMPO", 20, constantes.VERDE, L // 2, y0 + 18)
        self._texto(self.mensagem_transicao, 22, constantes.BRANCO, L // 2, y0 + 55)
        self._texto("Prepare-se...", 14, constantes.CINZA, L // 2, y0 + 90)

    # ─────────────────────────────────────────────────────────────────────────
    #  TELA FINAL
    # ─────────────────────────────────────────────────────────────────────────
    def _tela_final(self, mensagem, cor):
        s = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 195))
        self.tela.blit(s, (0, 0))

        L, A = constantes.LARGURA, constantes.ALTURA
        cx, cy = L // 2, A // 2
        larg, alt = 660, 360
        x0 = cx - larg // 2
        y0 = cy - alt  // 2
        self._desenhar_painel_cyber(x0, y0, larg, alt)

        self._texto_neon(mensagem, 50, cor, cx, y0 + 24)
        self._texto(f"Score total: {self.score_total_campanha}", 24, constantes.BRANCO, cx, y0 + 90)
        self._desenhar_resumo_campanha(cx, y0 + 122)
        self._texto_neon("R: recomecar  |  M: menu", 18, constantes.CIANO, cx, y0 + alt - 40)

    def _desenhar_resumo_campanha(self, cx, y0):
        if not self.resultados_fase:
            self._texto("Sem resultados.", 14, constantes.CINZA, cx, y0)
            return
        self._texto_neon("RESUMO DA CAMPANHA", 16, constantes.AMARELO, cx, y0)
        y = y0 + 28
        for r in self.resultados_fase[-4:]:
            ts = r["tempo_seg"]
            linha = (f"F{r['fase']}  {r['rank']}  {r['score']} pts  "
                     f"{ts // 60:02d}:{ts % 60:02d}  "
                     f"det:{r['detec']}  heat:{r['heat_medio']:.0f}")
            cor = constantes.BRANCO if r["concluida"] else constantes.CINZA
            self._texto(linha, 13, cor, cx, y)
            y += 22

    # ─────────────────────────────────────────────────────────────────────────
    #  FUNDO
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar_fundo(self, camera=(0, 0), shake=(0, 0)):
        camx, camy = camera
        ox, oy     = shake
        T = constantes.TAM_TILE
        self.tela.fill(constantes.COR_CHAO)

        tile  = assets_loader.tile_chao(T)
        mapa_cols = self.mundo_largura  // T
        mapa_rows = self.mundo_altura // T
        start_col = int(camx) // T
        start_row = int(camy) // T
        end_col   = start_col + constantes.LARGURA  // T + 2
        end_row   = start_row + constantes.ALTURA // T + 2

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if 0 <= col < mapa_cols and 0 <= row < mapa_rows:
                    sx = col * T - int(camx) + ox
                    sy = row * T - int(camy) + oy
                    self.tela.blit(tile, (sx, sy))

        # Borda escura
        sombra = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 60), (0, 0, constantes.LARGURA, constantes.ALTURA), 30)
        self.tela.blit(sombra, (ox, oy))

    # ─────────────────────────────────────────────────────────────────────────
    #  UTILITÁRIOS VISUAIS
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar_painel(self, x, y, larg, alt):
        painel = pygame.Surface((larg, alt), pygame.SRCALPHA)
        painel.fill((10, 14, 26, 185))
        self.tela.blit(painel, (x, y))
        pygame.draw.rect(self.tela, (50, 70, 110), (x, y, larg, alt), 1, border_radius=6)

    def _desenhar_painel_cyber(self, x, y, larg, alt):
        painel = pygame.Surface((larg, alt), pygame.SRCALPHA)
        painel.fill((8, 12, 24, 210))
        self.tela.blit(painel, (x, y))
        # Borda neon dupla
        pygame.draw.rect(self.tela, constantes.CIANO, (x, y, larg, alt), 1, border_radius=8)
        pygame.draw.rect(self.tela, (0, 80, 120), (x + 3, y + 3, larg - 6, alt - 6), 1, border_radius=6)
        # Cantos decorativos
        sz = 10
        for (cx2, cy2), (dx2, dy2) in [
            ((x, y),           (1, 1)),
            ((x + larg, y),    (-1, 1)),
            ((x, y + alt),     (1, -1)),
            ((x + larg, y + alt), (-1, -1)),
        ]:
            pygame.draw.line(self.tela, constantes.CIANO, (cx2, cy2), (cx2 + dx2 * sz, cy2), 2)
            pygame.draw.line(self.tela, constantes.CIANO, (cx2, cy2), (cx2, cy2 + dy2 * sz), 2)

    def _texto(self, texto, tamanho, cor, x, y, ancora="midtop"):
        fonte = pygame.font.Font(self.fonte, tamanho)
        surf  = fonte.render(texto, True, cor)
        rect  = surf.get_rect()
        setattr(rect, ancora, (x, y))
        self.tela.blit(surf, rect)

    def _texto_neon(self, texto, tamanho, cor, x, y, ancora="midtop"):
        fonte = pygame.font.Font(self.fonte, tamanho)
        # Camada de brilho
        surf_glow = fonte.render(texto, True, (*cor, 60))
        rect_g    = surf_glow.get_rect()
        setattr(rect_g, ancora, (x, y))
        for ox2, oy2 in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.tela.blit(surf_glow, rect_g.move(ox2 * 2, oy2 * 2))
        # Texto principal
        surf = fonte.render(texto, True, cor)
        rect = surf.get_rect()
        setattr(rect, ancora, (x, y))
        self.tela.blit(surf, rect)


# ── ponto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = Game()
    while g.esta_rodando:
        g.novo_jogo()
    pygame.quit()
