import pygame
import sys
import os
import time

# Inicialização do Pygame e da janela
largura = 1240
altura = 620
pygame.init()
som_contagem = pygame.mixer.Sound("regressiva.mp3")
som_soco = pygame.mixer.Sound("colisao.wav")  # Substitua "soco.wav" pelo caminho do seu arquivo de som de soco

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("REAL FIGHT")

# Cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

# Carregar efeitos sonoros e música de fundo
pygame.mixer.music.load("musica_fundo.mp3")
pygame.mixer.music.play(-1)  # Loop infinito para a música de fundo
pygame.mixer.music.set_volume(0.5)  # Define o volume para 50%

def texto(surface, texto, cor, tamanho_fonte, x, y, centro=False):
    fonte = pygame.font.SysFont("comicsansms", tamanho_fonte)
    texto_surface = fonte.render(texto, True, cor)
    texto_retangulo = texto_surface.get_rect()
    if centro:
        texto_retangulo.center = (x, y)
    else:
        texto_retangulo.topleft = (x, y)
    surface.blit(texto_surface, texto_retangulo)

def desenhar_menu():
    # Carregar imagem de fundo do menu
    caminho_menu = "cp.jpeg"
    menu_imagem = pygame.image.load(caminho_menu).convert_alpha()
    menu_imagem = pygame.transform.scale(menu_imagem, (largura, altura))
    tela.blit(menu_imagem, (0, 0))
    texto(tela, "Iniciar", BRANCO, 38, largura // 2, altura - 50, centro=True)

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

escala = (150, 220)  

acoes_disponiveis_p1 = ["parar", "correr", "soco", "saltar"]  
animacoes_p1 = carregar_animacoes("personagem1", acoes_disponiveis_p1, escala)

for acao in animacoes_p1:
    for i in range(len(animacoes_p1[acao])):
        animacoes_p1[acao][i] = pygame.transform.flip(animacoes_p1[acao][i], True, False)

acoes_disponiveis_p2 = ["parar", "andar", "soco", "saltar"]  
animacoes_p2 = carregar_animacoes("perso2", acoes_disponiveis_p2, escala)

pos_x_p1 = 100
pos_y_p1 = altura - animacoes_p1["parar"][0].get_height()
pos_x_p2 = largura - 100 - animacoes_p2["parar"][0].get_width()
pos_y_p2 = altura - animacoes_p2["parar"][0].get_height()

direcao_p1 = 1  
direcao_p2 = -1  

velocidade_y_p1 = 0
velocidade_y_p2 = 0

gravidade = 5

vida_p1 = 100
vida_p2 = 100

barra_largura = 400
barra_altura = 30
barra_espaco = 30  
barra_x_p1 = (largura - barra_largura) // 4  
barra_x_p2 = (largura - barra_largura) * 3 // 4  
barra_y = 5  

MOVIMENTO_X = 30

def controle_eventos():
    comandos_p1 = {"esquerda": False, "direita": False, "soco": False, "salto": False}  
    comandos_p2 = {"esquerda": False, "direita": False, "soco": False, "salto": False}  
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
            elif evento.key == pygame.K_UP:
                comandos_p1["salto"] = True
            elif evento.key == pygame.K_w:
                comandos_p2["salto"] = True
            elif evento.key == pygame.K_e:
                comandos_p2["soco"] = True
            elif evento.key == pygame.K_SLASH:
                comandos_p1["soco"] = True
            elif evento.key == pygame.K_RETURN:
                iniciar = True  
    return comandos_p1, comandos_p2, iniciar, fechar_jogo

def desenhar_barra_de_vida(surface, cor, x, y, largura, altura, vida_atual, vida_total, nome):
    pygame.draw.rect(surface, BRANCO, (x, y, largura, altura))
    comprimento_vida = int(largura * vida_atual / vida_total)
    pygame.draw.rect(surface, cor, (x, y, comprimento_vida, altura))
    
    # Adicionar o nome do personagem abaixo da barra de vida
    texto(surface, nome, BRANCO, 24, x + largura // 2, y + altura + 5, centro=True)

def detectar_colisao(x1, y1, largura1, altura1, x2, y2, largura2, altura2, acao_atual_p1, acao_atual_p2):
    if (x1 < x2 + largura2 and
            x1 + largura1 > x2 and
            y1 < y2 + altura2 and
            y1 + altura1 > y2):
        if acao_atual_p1 == "soco" and acao_atual_p2 != "soco":  
            return True, 10  # Retorna True e a quantidade de dano
        elif acao_atual_p2 == "soco" and acao_atual_p1 != "soco":  
            return True, 10  # Retorna True e a quantidade de dano
    return False, 0

def mostrar_vencedor(nome_pasta):
    if not os.path.exists(nome_pasta):
        print(f"O diretório '{nome_pasta}' não foi encontrado.")
        return
    
    texto(tela, "You Win!", BRANCO, 48, largura // 2, altura // 4, centro=True)
    
    caminho_animacao = os.path.join(nome_pasta, "vencedor")
    lista_frames = []
    for imagem_nome in os.listdir(caminho_animacao):
        caminho_imagem = os.path.join(caminho_animacao, imagem_nome)
        frame = pygame.image.load(caminho_imagem).convert_alpha()
        lista_frames.append(frame)

    frame_atual = 0
    tempo_frame = 100
    tempo_anterior = pygame.time.get_ticks()

    while True:
        tela.fill(BRANCO)
        tela.blit(lista_frames[frame_atual], ((largura - lista_frames[frame_atual].get_width()) // 2, altura // 2))

        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - tempo_anterior >= tempo_frame:
            frame_atual = (frame_atual + 1) % len(lista_frames)
            tempo_anterior = tempo_atual

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
def jogo():
    global pos_x_p1, pos_y_p1, pos_x_p2, pos_y_p2, direcao_p1, direcao_p2, vida_p1, vida_p2, velocidade_y_p1, velocidade_y_p2
    if vida_p1 <= 0:
            mostrar_vencedor("Rio_vencedor")
            return
    elif vida_p2 <= 0:
            mostrar_vencedor("Kyo_vencedor")
    contador_p1 = 0
    contador_p2 = 0

    acao_atual_p1 = "parar"
    acao_atual_p2 = "parar"

    atraso_animacao = 200  

    clock = pygame.time.Clock()

    caminho_background = "background/bk4.jpg"
    background = pygame.image.load(caminho_background).convert_alpha()
    background = pygame.transform.scale(background, (largura, altura))

    fonte_contagem = pygame.font.SysFont("Ravie", 100)
    som_contagem.play()
    som_contagem.set_volume(0.8)  # Define o volume para 80%

    for numero in range(3, 0, -1):
        
        tela.blit(background, (0, 0))
        texto_contagem = fonte_contagem.render(str(numero), True, BRANCO)
        tela.blit(texto_contagem, ((largura - texto_contagem.get_width()) // 2, (altura - texto_contagem.get_height()) // 2))
        pygame.display.flip()
        
          # Reproduz o som
        time.sleep(1)

    while True:
        comandos_p1, comandos_p2, iniciar, fechar_jogo = controle_eventos()

        if fechar_jogo:
            pygame.quit()
            sys.exit()

        if pos_y_p1 < altura - animacoes_p1["parar"][0].get_height():
            velocidade_y_p1 += gravidade
            pos_y_p1 += velocidade_y_p1
        else:
            pos_y_p1 = altura - animacoes_p1["parar"][0].get_height()
            velocidade_y_p1 = 0

        if pos_y_p2 < altura - animacoes_p2["parar"][0].get_height():
            velocidade_y_p2 += gravidade
            pos_y_p2 += velocidade_y_p2
        else:
            pos_y_p2 = altura - animacoes_p2["parar"][0].get_height()
            velocidade_y_p2 = 0

        if comandos_p1["esquerda"]:
            pos_x_p1 -= MOVIMENTO_X
            direcao_p1 = -1
            acao_atual_p1 = "correr"
        elif comandos_p1["direita"]:
            pos_x_p1 += MOVIMENTO_X
            direcao_p1 = 1
            acao_atual_p1 = "correr"
        else:
            acao_atual_p1 = "parar"  

        if comandos_p2["esquerda"]:
            pos_x_p2 -= MOVIMENTO_X
            direcao_p2 = -1
            acao_atual_p2 = "andar"
        elif comandos_p2["direita"]:
            pos_x_p2 += MOVIMENTO_X
            direcao_p2 = 1
            acao_atual_p2 = "andar"
        else:
            acao_atual_p2 = "parar"  

        if comandos_p1["salto"] and pos_y_p1 == altura - animacoes_p1["parar"][0].get_height():
            velocidade_y_p1 = -40  
            acao_atual_p1 = "saltar"  

        if comandos_p2["salto"] and pos_y_p2 == altura - animacoes_p2["parar"][0].get_height():
            velocidade_y_p2 = -40  
            acao_atual_p2 = "saltar"  

        if comandos_p1["soco"]:
            acao_atual_p1 = "soco" 
            som_soco.set_volume(0.4) 
            som_soco.play()
        if comandos_p2["soco"]:
            acao_atual_p2 = "soco"
            som_soco.set_volume(0.4)  
            som_soco.play()
        if pos_x_p1 < 0:
            pos_x_p1 = 0
        elif pos_x_p1 + animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)].get_width() > largura:
            pos_x_p1 = largura - animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)].get_width()

        if pos_x_p2 < 0:
            pos_x_p2 = 0
        elif pos_x_p2 + animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)].get_width() > largura:
            pos_x_p2 = largura - animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)].get_width()

        tela.blit(background, (0, 0))  
        if direcao_p1 == 1:
            tela.blit(animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)], (pos_x_p1, pos_y_p1))
        else:
            tela.blit(pygame.transform.flip(animacoes_p1[acao_atual_p1][min(contador_p1, len(animacoes_p1[acao_atual_p1]) - 1)], True, False), (pos_x_p1, pos_y_p1))

        if direcao_p2 == 1:
            tela.blit(animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)], (pos_x_p2, pos_y_p2))
        else:
            tela.blit(pygame.transform.flip(animacoes_p2[acao_atual_p2][min(contador_p2, len(animacoes_p2[acao_atual_p2]) - 1)], True, False), (pos_x_p2, pos_y_p2))

        contador_p1 += 1
        if contador_p1 >= len(animacoes_p1[acao_atual_p1]):
            contador_p1 = 0

        contador_p2 += 1
        if contador_p2 >= len(animacoes_p2[acao_atual_p2]):
            contador_p2 = 0

        desenhar_barra_de_vida(tela, VERMELHO, barra_x_p1, barra_y, barra_largura, barra_altura, vida_p1, 100,"Kyo")
        desenhar_barra_de_vida(tela, AZUL, barra_x_p2, barra_y, barra_largura, barra_altura, vida_p2, 100,"Rio")

        # Verificar colisão entre os jogadores
        colisao, dano = detectar_colisao(pos_x_p1, pos_y_p1, animacoes_p1[acao_atual_p1][contador_p1].get_width(),
                                         animacoes_p1[acao_atual_p1][contador_p1].get_height(),
                                         pos_x_p2, pos_y_p2, animacoes_p2[acao_atual_p2][contador_p2].get_width(),
                                         animacoes_p2[acao_atual_p2][contador_p2].get_height(),
                                         acao_atual_p1, acao_atual_p2)
        if colisao:
            # Se houver colisão, os personagens não atravessarão um ao outro
            if direcao_p1 == 1:
                pos_x_p1 = pos_x_p2 - animacoes_p1[acao_atual_p1][contador_p1].get_width()
            else:
                pos_x_p1 = pos_x_p2 + animacoes_p2[acao_atual_p2][contador_p2].get_width()
            if acao_atual_p1 == "soco" and acao_atual_p2 != "soco":  
                vida_p2 -= dano  
            elif acao_atual_p2 == "soco" and acao_atual_p1 != "soco":  
                vida_p1 -= dano  

        if vida_p1 <= 0:
            mostrar_vencedor("Rio_vencedor")
            pygame.display.flip()
            time.sleep(3)
            return
        elif vida_p2 <= 0:
            mostrar_vencedor("Kyo_vencedor")
            pygame.display.flip()
            time.sleep(3)
            return
        
        pygame.display.flip()
        clock.tick(10)  

while True:
    desenhar_menu()
    pygame.display.flip()
    iniciar = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            iniciar = True
            jogo()
