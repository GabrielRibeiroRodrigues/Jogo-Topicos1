"""
Script de teste: renderiza cenas do jogo e salva como PNG para revisão visual.
"""
import os, sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

import constantes
import sprites
import mapa
import principal


class TestGame(principal.Game):
    """Game sem loop bloqueante para testes."""
    def _rodar(self):
        pass


def salvar(tela, nome):
    path = os.path.join(os.path.dirname(__file__), nome)
    pygame.image.save(tela, path)
    print(f"  Salvo: {path}")


def testar_menu(g):
    g.estado_tela = "MENU"
    g._bg_cache = None
    g._desenhar_fundo()
    g._desenhar_menu()
    g.tela.blit(g._scanlines, (0, 0))
    g.tela.blit(g._vignette, (0, 0))
    salvar(g.tela, "screenshot_menu.png")


def testar_gameplay(g):
    g.estado_tela = "JOGANDO"
    g.em_transicao_fase = False
    g.tempo_inicio_partida = pygame.time.get_ticks()
    g._acumulado_pausa_ms  = 0
    g._ultimo_x_jogador    = float(g.jogador.rect.centerx)
    g._atualizar_camera()

    # Simula 30 frames de update
    for _ in range(30):
        g.todas_as_sprites.update()
        g._atualizar_progressao()
        g._atualizar_heat()
        g._atualizar_metricas_fase()
        g._atualizar_camera()

    g._desenhar()
    salvar(g.tela, "screenshot_gameplay.png")


def testar_gameplay_fase2(g2):
    g2.estado_tela = "JOGANDO"
    g2.em_transicao_fase = False
    g2.tempo_inicio_partida = pygame.time.get_ticks()
    g2._acumulado_pausa_ms  = 0
    g2._ultimo_x_jogador    = float(g2.jogador.rect.centerx)
    g2._atualizar_camera()

    for _ in range(20):
        g2.todas_as_sprites.update()
        g2._atualizar_camera()

    g2._desenhar()
    salvar(g2.tela, "screenshot_fase2.png")


def testar_pausa(g):
    g.estado_tela = "PAUSADO"
    g._desenhar()
    salvar(g.tela, "screenshot_pausa.png")


def testar_game_over(g):
    g.estado_tela = "FIM"
    g.game_over   = True
    g.vitoria     = False
    g.lives       = 0
    g.detectacoes_fase = 2
    g.score_total_campanha = 850
    g.resultados_fase = [{
        "fase": 1, "nome": "Setor 01 - Doca Estendida",
        "concluida": False, "tempo_seg": 95, "detec": 2,
        "heat_medio": 34.5, "score": 850, "rank": "C",
    }]
    g._desenhar()
    salvar(g.tela, "screenshot_game_over.png")


def testar_vitoria(g):
    g.estado_tela  = "FIM"
    g.game_over    = False
    g.vitoria      = True
    g.lives        = 2
    g.score_total_campanha = 9840
    g.resultados_fase = [
        {"fase": 1, "nome": "Setor 01", "concluida": True, "tempo_seg": 72,
         "detec": 0, "heat_medio": 8.2, "score": 1820, "rank": "S"},
        {"fase": 2, "nome": "Setor 02", "concluida": True, "tempo_seg": 88,
         "detec": 1, "heat_medio": 14.0, "score": 1640, "rank": "A"},
        {"fase": 3, "nome": "Setor 03", "concluida": True, "tempo_seg": 105,
         "detec": 0, "heat_medio": 11.0, "score": 1780, "rank": "S"},
    ]
    g._desenhar()
    salvar(g.tela, "screenshot_vitoria.png")


# ── Execução ──────────────────────────────────────────────────────────────────
print("\n=== INICIANDO TESTES DE RENDER ===\n")

print("1) Menu principal...")
g = TestGame()
g.novo_jogo()
testar_menu(g)

print("2) Gameplay - Fase 1...")
g2 = TestGame()
g2.novo_jogo()
g2.estado_tela = "JOGANDO"
testar_gameplay(g2)

print("3) Tela de pausa...")
testar_pausa(g2)

print("4) Game Over...")
g3 = TestGame()
g3.novo_jogo()
g3.estado_tela = "JOGANDO"
g3._desenhar_fundo()
testar_game_over(g3)

print("5) Vitoria / Fim de campanha...")
g4 = TestGame()
g4.novo_jogo()
g4.estado_tela = "JOGANDO"
g4._desenhar_fundo()
testar_vitoria(g4)

print("6) Fase 2 (Corredor Industrial)...")
g5 = TestGame()
g5.novo_jogo()
g5._carregar_fase(1)  # fase 2
g5.lives = 2
g5.score_total_campanha = 1820
testar_gameplay_fase2(g5)

pygame.quit()
print("\n=== TESTES CONCLUIDOS ===")
print("Screenshots gerados na pasta stealth/")
