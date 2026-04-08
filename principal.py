import pygame
import constantes
import sprites
import mapa


class Game:
    def __init__(self):
        pygame.init()
        self.tela    = pygame.display.set_mode((constantes.LARGURA, constantes.ALTURA))
        pygame.display.set_caption(constantes.TITULO_JOGO)
        self.relogio = pygame.time.Clock()
        self.fonte   = pygame.font.match_font(constantes.FONTE)
        self.esta_rodando = True
        # Surface reutilizável com canal alpha (cones + ondas de som)
        self.overlay = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)

    # ─────────────────────────────────────────────────────────────────────────
    #  INICIALIZAR UMA PARTIDA
    # ─────────────────────────────────────────────────────────────────────────
    def novo_jogo(self):
        # ── grupos de sprites ─────────────────────────────────────────────────
        self.todas_as_sprites = pygame.sprite.Group()   # atualização unificada
        self.obstaculos       = pygame.sprite.Group()   # paredes + caixas
        self.caixas           = pygame.sprite.Group()   # só caixas (esconderijo)
        self.guardas          = pygame.sprite.Group()   # guardas (FSM)
        self.sons             = pygame.sprite.Group()   # ondas sonoras

        # ── carregar mapa ──────────────────────────────────────────────────────
        self._saida = None
        for linha_idx, linha in enumerate(mapa.NIVEL_1):
            for col_idx, tile in enumerate(linha):
                x = col_idx * constantes.TAM_TILE
                y = linha_idx * constantes.TAM_TILE
                if tile == '#':
                    sprites.Parede(self, x, y)
                elif tile == 'B':
                    sprites.Caixa(self, x, y)
                elif tile == 'E':
                    self._saida = sprites.Saida(self, x, y)

        # ── jogador ────────────────────────────────────────────────────────────
        # tile (1, 11) → pixel top-left (40, 440)
        self.jogador = sprites.Jogador(self, 40, 440)

        # ── guarda 1 – patrulha a seção superior (linhas 1-3) ─────────────────
        wp1 = [(60, 60), (740, 60), (740, 140), (60, 140)]
        sprites.Guarda(self, 60, 60, wp1)

        # ── guarda 2 – patrulha a seção inferior (linhas 9-12) ────────────────
        wp2 = [(740, 380), (60, 380), (60, 500), (740, 500)]
        sprites.Guarda(self, 740, 380, wp2)

        self.jogando   = True
        self.game_over = False
        self.vitoria   = False
        self._rodar()

    # ─────────────────────────────────────────────────────────────────────────
    #  LOOP DO JOGO
    # ─────────────────────────────────────────────────────────────────────────
    def _rodar(self):
        while self.jogando:
            self.relogio.tick(constantes.FPS)
            self._eventos()
            if not self.game_over and not self.vitoria:
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

            # clique esquerdo → jogar pedra (distração sonora)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.game_over and not self.vitoria:
                    mx, my = event.pos
                    sprites.Som(self, mx, my)

            # tecla R → reiniciar após fim de jogo
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_over or self.vitoria):
                    self.jogando = False

    # ─────────────────────────────────────────────────────────────────────────
    #  ATUALIZAR
    # ─────────────────────────────────────────────────────────────────────────
    def _atualizar(self):
        # uma única chamada atualiza jogador, guardas, sons, etc.
        self.todas_as_sprites.update()

        # ── verificar game over: guarda em perseguição toca o jogador ──────────
        for guarda in self.guardas:
            if (guarda.estado == "PERSEGUICAO"
                    and guarda.rect.colliderect(self.jogador.rect)):
                self.game_over = True

        # ── verificar vitória: jogador alcança a saída ─────────────────────────
        if self._saida and self.jogador.rect.colliderect(self._saida.rect):
            self.vitoria = True

    # ─────────────────────────────────────────────────────────────────────────
    #  DESENHAR
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar(self):
        # 1. chão
        self.tela.fill(constantes.COR_CHAO)

        # 2. obstáculos (paredes e caixas)
        for sprite in self.obstaculos:
            self.tela.blit(sprite.image, sprite.rect)

        # 3. saída
        if self._saida:
            self.tela.blit(self._saida.image, self._saida.rect)

        # 4. overlay translúcido: cones de visão + ondas sonoras
        self.overlay.fill((0, 0, 0, 0))
        for guarda in self.guardas:
            guarda.desenhar_cone(self.overlay)
        for som in self.sons:
            som.desenhar(self.overlay)
        self.tela.blit(self.overlay, (0, 0))

        # 5. jogador (sobre os cones)
        self.tela.blit(self.jogador.image, self.jogador.rect)

        # 6. guardas
        for guarda in self.guardas:
            self.tela.blit(guarda.image, guarda.rect)

        # 7. HUD
        self._desenhar_hud()

        # 8. tela de fim de jogo
        if self.game_over:
            self._tela_final("CAPTURADO!", constantes.VERMELHO)
        elif self.vitoria:
            self._tela_final("ESCAPOU!", constantes.VERDE)

        pygame.display.flip()

    # ─────────────────────────────────────────────────────────────────────────
    #  HUD
    # ─────────────────────────────────────────────────────────────────────────
    def _desenhar_hud(self):
        # estado de cada guarda (canto superior esquerdo)
        y = 6
        for i, guarda in enumerate(self.guardas, start=1):
            cor = sprites.Guarda.COR_ESTADOS[guarda.estado]
            self._texto(f"Guarda {i}: {guarda.estado}", 16, cor,
                        6, y, ancora="topleft")
            y += 20

        # indicador de esconderijo (canto superior direito)
        if self.jogador.is_hidden:
            self._texto("[ ESCONDIDO ]", 16, constantes.AMARELO,
                        constantes.LARGURA - 6, 6, ancora="topright")

        # instruções (canto inferior esquerdo)
        instrucoes = [
            "WASD / Setas: Mover",
            "CTRL: Esconder (perto de caixa)",
            "Clique Esq: Jogar pedra (distração)",
        ]
        y_base = constantes.ALTURA - 6
        for instrucao in reversed(instrucoes):
            self._texto(instrucao, 13, constantes.CINZA,
                        6, y_base, ancora="bottomleft")
            y_base -= 17

    # ─────────────────────────────────────────────────────────────────────────
    #  TELA FINAL
    # ─────────────────────────────────────────────────────────────────────────
    def _tela_final(self, mensagem, cor):
        # fundo semi-transparente
        s = pygame.Surface((constantes.LARGURA, constantes.ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.tela.blit(s, (0, 0))
        cx = constantes.LARGURA  // 2
        cy = constantes.ALTURA   // 2
        self._texto(mensagem, 72, cor, cx, cy - 55)
        self._texto("Pressione R para recomeçar", 24, constantes.BRANCO, cx, cy + 25)

    # ─────────────────────────────────────────────────────────────────────────
    #  UTILITÁRIO DE TEXTO
    # ─────────────────────────────────────────────────────────────────────────
    def _texto(self, texto, tamanho, cor, x, y, ancora="midtop"):
        fonte     = pygame.font.Font(self.fonte, tamanho)
        superficie = fonte.render(texto, True, cor)
        rect      = superficie.get_rect()
        setattr(rect, ancora, (x, y))
        self.tela.blit(superficie, rect)


# ── ponto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = Game()
    while g.esta_rodando:
        g.novo_jogo()
    pygame.quit()
