import pygame
import sys
import os
import time

# Inicialização do Pygame e da janela
largura = 1240
altura = 620
pygame.init()
pygame.font.init() 
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("REAL FIGHT")

# Cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

# Carregar efeitos sonoros e música de fundo
pygame.mixer.music.load("musica_fundo.mp3")
pygame.mixer.music.play(-1)  # Loop infinito para a música de fundo

def texto(surface, texto, cor, tamanho_fonte, x, y):
    fonte = pygame.font.SysFont("comicsansms", tamanho_fonte)
    texto_surface = fonte.render(texto, True, cor)
    texto_retangulo = texto_surface.get_rect()
    texto_retangulo.midtop = (x, y)
    surface.blit(texto_surface, texto_retangulo)

# Função para desenhar o menu
def desenhar_menu():
    # Carregar imagem de fundo do menu
    caminho_menu = "cp.jpeg"
    menu_imagem = pygame.image.load(caminho_menu).convert_alpha()
    menu_imagem = pygame.transform.scale(menu_imagem, (largura, altura))
    tela.blit(menu_imagem, (0, 0))
    texto(tela, "Iniciar", BRANCO, 38, largura // 8, altura // 8)
    # Renderizar texto

# Função para carregar sprites com animações e redimensioná-los
def carregar_animacoes(diretorio, acoes, escala):
    animacoes = {}
    for acao in acoes:
        lista_sprites = []
        caminho_acao = os.path.join(diretorio, acao)
        for imagem_nome in os.listdir(caminho_acao):
            caminho_imagem = os.path.join(caminho_acao, imagem_nome)
            sprite = pygame.image.load(caminho_imagem).convert_alpha()
            sprite_redimensionado = pygame.transform.scale(sprite, escala)
            lista_sprites.append(sprite_redimensionado)
        animacoes[acao] = lista_sprites
    return animacoes

# Definir a escala para redimensionar os sprites
escala = (100, 150)  # Largura x Altura

# Carregar as animações para o primeiro jogador e redimensioná-las
acoes_disponiveis_p1 = ["parar", "correr", "soco", "saltar"]  # Adicionado "saltar" e "soco"
animacoes_p1 = carregar_animacoes("personagem1", acoes_disponiveis_p1, escala)

# Aplicar flip horizontal nas animações do personagem1
for acao in animacoes_p1:
    for i in range(len(animacoes_p1[acao])):
        animacoes_p1[acao][i] = pygame.transform.flip(animacoes_p1[acao][i], True, False)

# Carregar as animações para o segundo jogador e redimensioná-las
acoes_disponiveis_p2 = ["parar", "andar", "soco", "saltar"]  # Adicionado "saltar" e "soco"
animacoes_p2 = carregar_animacoes("perso2", acoes_disponiveis_p2, escala)

# Posições iniciais dos jogadores
pos_x_p1 = 100
pos_y_p1 = altura - animacoes_p1["parar"][0].get_height()
pos_x_p2 = largura - 100 - animacoes_p2["parar"][0].get_width()
pos_y_p2 = altura - animacoes_p2["parar"][0].get_height()

# Direções dos jogadores
direcao_p1 = 1  # 1 para direita, -1 para esquerda
direcao_p2 = -1  # 1 para direita, -1 para esquerda

# Velocidades verticais dos jogadores
velocidade_y_p1 = 0
velocidade_y_p2 = 0

# Gravidade
gravidade = 5

# Vida inicial dos jogadores
vida_p1 = 100
vida_p2 = 100

# Tamanho e posição das barras de vida
barra_largura = 400
barra_altura = 30
barra_espaco = 30  # Espaço entre as barras
barra_x_p1 = (largura - barra_largura) // 4  # Posição da barra do jogador 1
barra_x_p2 = (largura - barra_largura) * 3 // 4  # Posição da barra do jogador 2
barra_y = 5  # Posição vertical das barras

# Ajuste o valor de movimento para a esquerda e direita
MOVIMENTO_X = 30

def controle_eventos():
    comandos_p1 = {"esquerda": False, "direita": False, "soco": False, "salto": False}  # Adicionado "salto" e "soco"
    comandos_p2 = {"esquerda": False, "direita": False, "soco": False, "salto": False}  # Adicionado "salto" e "soco"
    iniciar = False
    fechar_jogo = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                fechar_jogo = True
            elif evento.key == pygame.K_LEFT:
                comandos_p1["esquerda"] = True
            elif evento.key == pygame.K_RIGHT:
                comandos_p1["direita"] = True
            elif evento.key == pygame.K_a:
                comandos_p2["esquerda"] = True
            elif evento.key == pygame.K_d:
                comandos_p2["direita"] = True
            elif evento.key == pygame.K_UP:  # Adicionado detecção de salto para o jogador 1
                comandos_p1["salto"] = True
            elif evento.key == pygame.K_w:   # Adicionado detecção de salto para o jogador 2
                comandos_p2["salto"] = True
            elif evento.key == pygame.K_e:   # Adicionado detecção de soco para o jogador 2
                comandos_p2["soco"] = True
            elif evento.key == pygame.K_SLASH:  # Adicionado detecção de soco para o jogador 1
                comandos_p1["soco"] = True
            elif evento.key == pygame.K_RETURN:
                iniciar = True  
    return comandos_p1, comandos_p2, iniciar, fechar_jogo

# Função para desenhar a barra de vida
# Carregar a fonte padrão do Pygame
 # Inicializar o módulo de fonte do Pygame
font_padrao = pygame.font.SysFont("SnapITC", 20)

# Função para desenhar a barra de vida e o nome do personagem com a fonte padrão
def desenhar_barra_de_vida(surface, cor, x, y, largura, altura, vida_atual, vida_total, nome_personagem):
    # Desenhar barra de fundo
    pygame.draw.rect(surface, BRANCO, (x, y, largura, altura))
    # Calcular comprimento da barra de vida proporcional à vida atual
    comprimento_vida = int(largura * vida_atual / vida_total)
    # Desenhar barra de vida
    pygame.draw.rect(surface, cor, (x, y, comprimento_vida, altura))
    # Renderizar o nome do personagem com a fonte padrão
    fonte = pygame.font.SysFont("SnapITC", 20)
    texto_surface = fonte.render(nome_personagem, True, BRANCO)
    # Obter retângulo do texto
    texto_retangulo = texto_surface.get_rect()
    # Centralizar o texto abaixo da barra de vida
    texto_retangulo.midtop = (x + largura // 2, y + altura + 5 + barra_espaco)
    # Desenhar o nome do personagem na tela
    surface.blit(texto_surface, texto_retangulo)

# Função principal do jogo
def jogo():
    global pos_x_p1, pos_y_p1, pos_x_p2, pos_y_p2, direcao_p1, direcao_p2, vida_p1, vida_p2, velocidade_y_p1, velocidade_y_p2

    # Contadores para animação dos sprites
    contador_p1 = 0
    contador_p2 = 0

    # Ação inicial dos jogadores
    acao_atual_p1 = "parar"
    acao_atual_p2 = "parar"

    # Atraso para animação (em milissegundos)
    atraso_animacao = 200  # Ajuste conforme necessário

    # Clock para controlar o tempo
    clock = pygame.time.Clock()

    # Carregar o background do jogo e redimensioná-lo para o tamanho da tela
    caminho_background = "background/back.png"
    background = pygame.image.load(caminho_background).convert_alpha()
    background = pygame.transform.scale(background, (largura, altura))

    # Fonte para a contagem regressiva
    fonte_contagem = pygame.font.SysFont("Ravie", 100)

    # Contagem regressiva
    for numero in range(3, 0, -1):
        # Desenhar o background do jogo
        tela.blit(background, (0, 0))
        # Renderizar e desenhar o número
        texto_contagem = fonte_contagem.render(str(numero), True, BRANCO)
        tela.blit(texto_contagem, ((largura - texto_contagem.get_width()) // 2, (altura - texto_contagem.get_height()) // 2))
        # Atualizar a tela
        pygame.display.flip()
        # Aguardar 1 segundo antes de exibir o próximo número
        time.sleep(1)

    # Loop principal do jogo
    while True:
        comandos_p1, comandos_p2, iniciar, fechar_jogo = controle_eventos()

        # Verificar se o jogo deve ser fechado
        if fechar_jogo:
            pygame.quit()
            sys.exit()

        # Aplicar gravidade aos jogadores
        if pos_y_p1 < altura - animacoes_p1["parar"][0].get_height():
            # Aplicar gravidade apenas se o jogador não estiver no chão
            velocidade_y_p1 += gravidade
            pos_y_p1 += velocidade_y_p1
        else:
            # Se o jogador estiver no chão, reiniciar a velocidade vertical
            pos_y_p1 = altura - animacoes_p1["parar"][0].get_height()
            velocidade_y_p1 = 0

        # A mesma lógica se aplica ao segundo jogador
        if pos_y_p2 < altura - animacoes_p2["parar"][0].get_height():
            velocidade_y_p2 += gravidade
            pos_y_p2 += velocidade_y_p2
        else:
            pos_y_p2 = altura - animacoes_p2["parar"][0].get_height()
            velocidade_y_p2 = 0

        # Atualizar a posição dos jogadores de acordo com os comandos
        if comandos_p1["esquerda"]:
            pos_x_p1 -= MOVIMENTO_X
            direcao_p1 = -1
            acao_atual_p1 = "correr"
        elif comandos_p1["direita"]:
            pos_x_p1 += MOVIMENTO_X
            direcao_p1 = 1
            acao_atual_p1 = "correr"
        else:
            acao_atual_p1 = "parar"  # Corrigido: Definir ação atual como "parar" quando não há entrada de movimento

        # A mesma lógica se aplica ao segundo jogador
        if comandos_p2["esquerda"]:
            pos_x_p2 -= MOVIMENTO_X
            direcao_p2 = -1
            acao_atual_p2 = "andar"
        elif comandos_p2["direita"]:
            pos_x_p2 += MOVIMENTO_X
            direcao_p2 = 1
            acao_atual_p2 = "andar"
        else:
            acao_atual_p2 = "parar"  # Corrigido: Definir ação atual como "parar" quando não há entrada de movimento

        # Verificar e aplicar salto para o jogador 1
        if comandos_p1["salto"] and pos_y_p1 == altura - animacoes_p1["parar"][0].get_height():
            velocidade_y_p1 = -40  # Definir velocidade vertical negativa para saltar
            acao_atual_p1 = "saltar"  # Definir ação atual como "saltar" durante o salto

        # Verificar e aplicar salto para o jogador 2
        if comandos_p2["salto"] and pos_y_p2 == altura - animacoes_p2["parar"][0].get_height():
            velocidade_y_p2 = -40  # Definir velocidade vertical negativa para saltar
            acao_atual_p2 = "saltar"  # Definir ação atual como "saltar" durante o salto

        # Verificar e aplicar soco para o jogador 1
        
        # Verificar e aplicar soco para o jogador 1
        if comandos_p1["soco"]:
            acao_atual_p1 = "soco"
            # Verificar colisão com o segundo jogador
            if pos_x_p1 < pos_x_p2 + animacoes_p2["parar"][0].get_width() and pos_x_p1 + animacoes_p1["soco"][0].get_width() > pos_x_p2:
                vida_p2 -= 10  # Reduzir vida do segundo jogador se houver colisão
                  # Exibir mensagem de soco
                print("Vida do Jogador 2:", vida_p2)  # Exibir vida restante do segundo jogador
        else:
            acao_atual_p1 = "parar"

        # Verificar e aplicar soco para o jogador 2
        if comandos_p2["soco"]:
            acao_atual_p2 = "soco"
            # Verificar colisão com o primeiro jogador
            if pos_x_p2 < pos_x_p1 + animacoes_p1["parar"][0].get_width() and pos_x_p2 + animacoes_p2["soco"][0].get_width() > pos_x_p1:
                vida_p1 -= 10  # Reduzir vida do primeiro jogador se houver colisão
                  # Exibir mensagem de soco
                print("Vida do Jogador 1:", vida_p1)  # Exibir vida restante do primeiro jogador
        else:
            acao_atual_p2 = "parar"
        # Limitar a posição dos jogadores para não saírem da tela
        if pos_x_p1 < 0:
            pos_x_p1 = 0
        elif pos_x_p1 + animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)].get_width() > largura:
            pos_x_p1 = largura - animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)].get_width()

        # A mesma lógica se aplica ao segundo jogador
        if pos_x_p2 < 0:
            pos_x_p2 = 0
        elif pos_x_p2 + animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)].get_width() > largura:
            pos_x_p2 = largura - animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)].get_width()

        # Desenhar os jogadores
        tela.blit(background, (0, 0))  # Limpar tela antes de desenhar os jogadores
        if direcao_p1 == 1:
            tela.blit(animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)], (pos_x_p1, pos_y_p1))
        else:
            tela.blit(pygame.transform.flip(animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)], True, False), (pos_x_p1, pos_y_p1))

        if direcao_p2 == 1:
            tela.blit(animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)], (pos_x_p2, pos_y_p2))
        else:
            tela.blit(pygame.transform.flip(animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)], True, False), (pos_x_p2, pos_y_p2))

        # Atualizar os contadores para animação dos sprites
        contador_p1 += 1
        if contador_p1 >= len(animacoes_p1[acao_atual_p1]):
            contador_p1 = 0

        contador_p2 += 1
        if contador_p2 >= len(animacoes_p2[acao_atual_p2]):
            contador_p2 = 0

        # Desenhar as barras de vida
        desenhar_barra_de_vida(tela, VERMELHO, barra_x_p1, barra_y, barra_largura, barra_altura, vida_p1, 100, "Kyo")
        desenhar_barra_de_vida(tela, AZUL, barra_x_p2, barra_y, barra_largura, barra_altura, vida_p2, 100, "R")

        # Atualizar a tela
        pygame.display.flip()

        # Limitar a taxa de quadros por segundo
        clock.tick(10)  # Ajuste conforme necessário

# Loop principal do jogo
while True:
    desenhar_menu()
    pygame.display.flip()
    iniciar = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                iniciar = True
                jogo()
