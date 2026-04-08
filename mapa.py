# Legenda:
#   #  → parede
#   .  → chão (vazio)
#   B  → caixa (obstáculo + esconderijo)
#   E  → saída (objetivo)
#
# Grade: 20 colunas × 15 linhas  →  800 × 600 px  (TAM_TILE = 40)

NIVEL_1 = [
    "####################",   # linha 0
    "#..................#",   # linha 1  – corredor superior
    "#.BB..........BB...#",   # linha 2  – caixas para esconder
    "#..................#",   # linha 3  – corredor superior
    "#......####........#",   # linha 4  – topo da sala central
    "#......#..#........#",   # linha 5  – lateral da sala
    "#......#..#........#",   # linha 6  – lateral da sala
    "#..BB..#..#.BB.....#",   # linha 7  – caixas flanqueando a sala
    "#......####........#",   # linha 8  – fundo da sala central
    "#.......#..........#",   # linha 9  – corredor inferior
    "#.BB....#.....BB...#",   # linha 10 – caixas para esconder
    "#.......#..........#",   # linha 11 – corredor inferior
    "#..................#",   # linha 12 – corredor inferior
    "#.................E#",   # linha 13 – saída (canto direito)
    "####################",   # linha 14
]
