import pygame
import random
import sys

# Inicializa o pygame
pygame.init()

# Configurações da tela (tamanho padrão para modo janela)
LARGURA_PADRAO = 400
ALTURA_PADRAO = 600
tela = pygame.display.set_mode((LARGURA_PADRAO, ALTURA_PADRAO))
pygame.display.set_caption('Flappy Bird')

# Variável para controlar o estado do fullscreen
fullscreen = True

# Cores
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
PRETO = (0, 0, 0)
AMARELO = (255, 251, 0)
ROSA = (255, 0, 170)

# Configurações do jogo
GRAVIDADE = 0.50
VELOCIDADE_PASSARO = 100
PULO = -7
VELOCIDADE_CANO = 3
ESPACO_CANOS = 150
FREQUENCIA_CANOS = 1500  # ms

# Função para alternar entre fullscreen e modo janela
def toggle_fullscreen():
    global fullscreen, tela
    fullscreen = not fullscreen
    
    if fullscreen:
        # Modo fullscreen
        tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        # Modo janela
        tela = pygame.display.set_mode((LARGURA_PADRAO, ALTURA_PADRAO))

# Passaro
class Passaro:
    def __init__(self):
        self.x = 100
        self.y = ALTURA_PADRAO // 2
        self.velocidade = 0
        self.raio = 15
    
    def pular(self):
        self.velocidade = PULO
    
    def mover(self):
        self.velocidade += GRAVIDADE
        self.y += self.velocidade
    
    def desenhar(self, tela):
        # Ajusta a posição proporcionalmente quando em fullscreen
        if fullscreen:
            proporcao_x = tela.get_width() / LARGURA_PADRAO
            proporcao_y = tela.get_height() / ALTURA_PADRAO
            pygame.draw.circle(tela, VERDE, (int(self.x * proporcao_x), int(self.y * proporcao_y)), int(self.raio * min(proporcao_x, proporcao_y)))
        else:
            pygame.draw.circle(tela, AZUL, (self.x, int(self.y)), self.raio)
    
    def get_mask(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)

# Canos
class Cano:
    def __init__(self):
        self.x = LARGURA_PADRAO
        self.altura = random.randint(150, 450)
        self.topo = self.altura - ESPACO_CANOS // 2
        self.base = self.altura + ESPACO_CANOS // 2
        self.largura = 70
        self.passou = False
    
    def mover(self):
        self.x -= VELOCIDADE_CANO
    
    def desenhar(self, tela):
        if fullscreen:
            proporcao_x = tela.get_width() / LARGURA_PADRAO
            proporcao_y = tela.get_height() / ALTURA_PADRAO
            # Desenha o cano do topo
            pygame.draw.rect(tela, VERDE, (self.x * proporcao_x, 0, self.largura * proporcao_x, self.topo * proporcao_y))
            # Desenha o cano da base
            pygame.draw.rect(tela, VERDE, (self.x * proporcao_x, self.base * proporcao_y, self.largura * proporcao_x, (ALTURA_PADRAO - self.base) * proporcao_y))
        else:
            pygame.draw.rect(tela, VERDE, (self.x, 0, self.largura, self.topo))
            pygame.draw.rect(tela, VERDE, (self.x, self.base, self.largura, ALTURA_PADRAO - self.base))
    
    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.Rect(self.x, 0, self.largura, self.topo)
        base_mask = pygame.Rect(self.x, self.base, self.largura, ALTURA_PADRAO - self.base)
        
        colisao_topo = passaro_mask.colliderect(topo_mask)
        colisao_base = passaro_mask.colliderect(base_mask)
        
        return colisao_topo or colisao_base

# Jogo principal
def jogo():
    global fullscreen, tela
    
    passaro = Passaro()
    canos = [Cano()]
    placar = 0
    fonte = pygame.font.SysFont('Arial', 30)
    
    ultimo_cano = pygame.time.get_ticks()
    rodando = True
    
    while rodando:
        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    passaro.pular()
                elif evento.key == pygame.K_f:  # Tecla F para alternar fullscreen
                    toggle_fullscreen()
                elif evento.key == pygame.K_ESCAPE:  # ESC para sair do fullscreen
                    if fullscreen:
                        toggle_fullscreen()
        
        # Movimentação
        passaro.mover()
        
        # Gerar canos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_cano > FREQUENCIA_CANOS:
            canos.append(Cano())
            ultimo_cano = tempo_atual
        
        # Mover e remover canos
        for cano in canos:
            cano.mover()
            
            # Verificar colisão
            if cano.colidir(passaro):
                rodando = False
            
            # Verificar pontuação
            if cano.x + cano.largura < passaro.x and not cano.passou:
                cano.passou = True
                placar += 1
            
            if cano.x < -cano.largura:
                canos.remove(cano)
        
        # Verificar se o pássaro saiu da tela
        if passaro.y < 0 or passaro.y > ALTURA_PADRAO:
            rodando = False
        
        # Desenhar
        tela.fill(ROSA)
        for cano in canos:
            cano.desenhar(tela)
        passaro.desenhar(tela)
        
        # Mostrar placar
        texto_placar = fonte.render(f'Pontos: {placar}', True, PRETO)
        if fullscreen:
            proporcao_x = tela.get_width() / LARGURA_PADRAO
            proporcao_y = tela.get_height() / ALTURA_PADRAO
            tela.blit(pygame.transform.scale(texto_placar, 
                      (int(texto_placar.get_width() * proporcao_x), 
                      int(texto_placar.get_height() * proporcao_y))), 
                      (10 * proporcao_x, 10 * proporcao_y))
        else:
            tela.blit(texto_placar, (10, 10))
        
        pygame.display.update()
        pygame.time.Clock().tick(60)

# Iniciar o jogo
if __name__ == "__main__":
    jogo()