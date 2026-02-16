import pygame
import sys
import math
import time
import copy

# Inicializar PyGame
pygame.init()

# Constantes
LARGURA = 800
ALTURA = 800
LINHAS = 8
COLUNAS = 8
TAMANHO_QUADRADO = LARGURA // COLUNAS
RAIO_PECA = TAMANHO_QUADRADO // 2 - 15

# Cores
VERMELHO = (255, 0, 0)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 0, 255)
CINZA = (128, 128, 128)
AMARELO = (255, 255, 0)
VERDE = (0, 180, 0)
MARROM = (165, 42, 42)
AZUL_CLARO = (173, 216, 230)

# Constantes do jogo
VAZIO = 0
PEDRA_BRANCA = 1
PEDRA_PRETA = 2
DAMA_BRANCA = 3
DAMA_PRETA = 4

class Tabuleiro:
    def __init__(self):
        self.tabuleiro = []
        self.criar_tabuleiro()
    
    def criar_tabuleiro(self):
        """Cria o tabuleiro inicial com as peças nas posições corretas"""
        self.tabuleiro = []
        for linha in range(LINHAS):
            self.tabuleiro.append([])
            for coluna in range(COLUNAS):
                # Posiciona peças apenas em quadrados escuros (linha+coluna é ímpar)
                if (linha + coluna) % 2 == 1:
                    if linha < 3:
                        self.tabuleiro[linha].append(PEDRA_PRETA)  # IA
                    elif linha > 4:
                        self.tabuleiro[linha].append(PEDRA_BRANCA)  # Jogador
                    else:
                        self.tabuleiro[linha].append(VAZIO)
                else:
                    self.tabuleiro[linha].append(VAZIO)
    
    def desenhar(self, janela):
        """Desenha o tabuleiro e as peças"""
        janela.fill(MARROM)
        
        # Desenha os quadrados do tabuleiro
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                # Quadrados pretos (onde as peças podem estar)
                if (linha + coluna) % 2 == 1:
                    cor = PRETO
                else:
                    cor = BRANCO
                pygame.draw.rect(janela, cor, (coluna * TAMANHO_QUADRADO, linha * TAMANHO_QUADRADO, TAMANHO_QUADRADO, TAMANHO_QUADRADO))
        
        # Desenha as peças
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                peca = self.tabuleiro[linha][coluna]
                if peca != VAZIO:
                    x = coluna * TAMANHO_QUADRADO + TAMANHO_QUADRADO // 2
                    y = linha * TAMANHO_QUADRADO + TAMANHO_QUADRADO // 2
                    
                    # Cor da peça
                    if peca == PEDRA_BRANCA or peca == DAMA_BRANCA:
                        cor_peca = BRANCO
                    else:
                        cor_peca = VERMELHO
                    
                    # Desenha o círculo da peça
                    pygame.draw.circle(janela, cor_peca, (x, y), RAIO_PECA)
                    pygame.draw.circle(janela, PRETO, (x, y), RAIO_PECA, 2)
                    
                    # Desenha uma coroa se for uma dama
                    if peca == DAMA_BRANCA or peca == DAMA_PRETA:
                        pygame.draw.circle(janela, AMARELO, (x, y), RAIO_PECA // 2)
                        pygame.draw.circle(janela, PRETO, (x, y), RAIO_PECA // 2, 1)
    
    def mover(self, movimento):
        """Executa um movimento no tabuleiro"""
        linha_inicio, col_inicio, linha_fim, col_fim, pecas_capturadas = movimento
        
        # Move a peça
        peca = self.tabuleiro[linha_inicio][col_inicio]
        self.tabuleiro[linha_inicio][col_inicio] = VAZIO
        self.tabuleiro[linha_fim][col_fim] = peca
        
        # Remove peças capturadas
        for (linha, coluna) in pecas_capturadas:
            self.tabuleiro[linha][coluna] = VAZIO
        
        # Verifica se a peça deve se tornar uma dama
        if peca == PEDRA_BRANCA and linha_fim == 0:
            self.tabuleiro[linha_fim][col_fim] = DAMA_BRANCA
            return True, "Pedra branca virou dama!"
        elif peca == PEDRA_PRETA and linha_fim == LINHAS - 1:
            self.tabuleiro[linha_fim][col_fim] = DAMA_PRETA
            return True, "Pedra vermelha virou dama!"
        
        return False, ""
    
    def get_movimentos_validos(self, jogador):
        """Retorna todos os movimentos válidos para um jogador"""
        movimentos = []
        capturas_obrigatorias = []
        
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                peca = self.tabuleiro[linha][coluna]
                
                # Verifica se a peça pertence ao jogador atual
                if (jogador == "branco" and (peca == PEDRA_BRANCA or peca == DAMA_BRANCA)) or \
                   (jogador == "vermelho" and (peca == PEDRA_PRETA or peca == DAMA_PRETA)):
                    
                    # Obtém movimentos para esta peça
                    movs_peca = self.get_movimentos_peca(linha, coluna)
                    
                    for movimento in movs_peca:
                        if movimento[4]:  # Se tem capturas
                            capturas_obrigatorias.append(movimento)
                        else:
                            movimentos.append(movimento)
        
        # Regra da captura obrigatória
        if capturas_obrigatorias:
            return capturas_obrigatorias
        return movimentos
    
    def get_movimentos_peca(self, linha, coluna):
        """Obtém todos os movimentos válidos para uma peça específica"""
        peca = self.tabuleiro[linha][coluna]
        if peca == VAZIO:
            return []
        
        movimentos = []
        
        # Define direções baseadas no tipo de peça
        if peca == PEDRA_BRANCA:
            direcoes = [(-1, -1), (-1, 1)]  # Move para cima
        elif peca == PEDRA_PRETA:
            direcoes = [(1, -1), (1, 1)]    # Move para baixo
        else:  # Dama
            direcoes = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        # Verifica movimentos simples
        for dlinha, dcoluna in direcoes:
            nova_linha = linha + dlinha
            nova_coluna = coluna + dcoluna
            
            if 0 <= nova_linha < LINHAS and 0 <= nova_coluna < COLUNAS:
                if self.tabuleiro[nova_linha][nova_coluna] == VAZIO:
                    movimentos.append((linha, coluna, nova_linha, nova_coluna, []))
        
        # Verifica capturas
        movimentos_captura = self.get_capturas_peca(linha, coluna, peca, [])
        movimentos.extend(movimentos_captura)
        
        return movimentos
    
    def get_capturas_peca(self, linha, coluna, peca, capturadas_anteriores):
        """Obtém capturas em cadeia para uma peça"""
        movimentos = []
        direcoes = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        # Para pedras, restringe direções
        if peca == PEDRA_BRANCA:
            direcoes = [(-1, -1), (-1, 1)]
        elif peca == PEDRA_PRETA:
            direcoes = [(1, -1), (1, 1)]
        
        for dlinha, dcoluna in direcoes:
            # Posição da possível peça inimiga
            linha_inimigo = linha + dlinha
            coluna_inimigo = coluna + dcoluna
            
            # Posição de destino após a captura
            linha_destino = linha + 2 * dlinha
            coluna_destino = coluna + 2 * dcoluna
            
            # Verifica se a captura é válida
            if (0 <= linha_inimigo < LINHAS and 0 <= coluna_inimigo < COLUNAS and
                0 <= linha_destino < LINHAS and 0 <= coluna_destino < COLUNAS):
                
                peca_inimiga = self.tabuleiro[linha_inimigo][coluna_inimigo]
                
                # Verifica se há uma peça inimiga e se o destino está vazio
                if (self.eh_inimigo(peca, peca_inimiga) and 
                    self.tabuleiro[linha_destino][coluna_destino] == VAZIO and
                    (linha_inimigo, coluna_inimigo) not in capturadas_anteriores):
                    
                    # Cria a lista de peças capturadas
                    novas_capturadas = capturadas_anteriores + [(linha_inimigo, coluna_inimigo)]
                    
                    # Cria movimento de captura
                    movimento = (linha, coluna, linha_destino, coluna_destino, novas_capturadas)
                    movimentos.append(movimento)
                    
                    # Verifica capturas múltiplas
                    # Cria um tabuleiro temporário para verificar mais capturas
                    tab_temp = self.copiar()
                    tab_temp.mover(movimento)
                    
                    # Verifica se a mesma peça pode capturar novamente
                    mais_capturas = tab_temp.get_capturas_peca(linha_destino, coluna_destino, peca, novas_capturadas)
                    
                    # Se houver mais capturas, substitui o movimento atual
                    if mais_capturas:
                        # Remove o movimento atual e adiciona os movimentos com múltiplas capturas
                        movimentos.remove(movimento)
                        for mc in mais_capturas:
                            # Mantém a posição inicial original
                            mov_final = (linha, coluna, mc[2], mc[3], mc[4])
                            movimentos.append(mov_final)
        
        return movimentos
    
    def eh_inimigo(self, peca1, peca2):
        """Verifica se duas peças são inimigas"""
        if peca1 == VAZIO or peca2 == VAZIO:
            return False
        
        brancas = [PEDRA_BRANCA, DAMA_BRANCA]
        pretas = [PEDRA_PRETA, DAMA_PRETA]
        
        return (peca1 in brancas and peca2 in pretas) or (peca1 in pretas and peca2 in brancas)
    
    def contar_pecas(self):
        """Conta o número de peças de cada tipo"""
        brancas = pretas = damas_brancas = damas_pretas = 0
        
        for linha in range(LINHAS):
            for coluna in range(COLUNAS):
                peca = self.tabuleiro[linha][coluna]
                if peca == PEDRA_BRANCA:
                    brancas += 1
                elif peca == PEDRA_PRETA:
                    pretas += 1
                elif peca == DAMA_BRANCA:
                    damas_brancas += 1
                elif peca == DAMA_PRETA:
                    damas_pretas += 1
        
        return brancas, pretas, damas_brancas, damas_pretas
    
    def avaliar(self):
        """
        Função de avaliação heurística
        Retorna valor positivo se brancas (jogador) estão em vantagem
        """
        brancas, pretas, damas_brancas, damas_pretas = self.contar_pecas()
        
        # Valores básicos
        valor_pedra = 1
        valor_dama = 3
        
        # Calcula vantagem material
        vantagem = (brancas - pretas) * valor_pedra
        vantagem += (damas_brancas - damas_pretas) * valor_dama
        
        return vantagem
    
    def copiar(self):
        """Cria uma cópia profunda do tabuleiro"""
        novo_tabuleiro = Tabuleiro()
        novo_tabuleiro.tabuleiro = [linha[:] for linha in self.tabuleiro]
        return novo_tabuleiro
    
    def vencedor(self):
        """Verifica se há um vencedor"""
        brancas, pretas, _, _ = self.contar_pecas()
        
        if brancas == 0 or not self.get_movimentos_validos("branco"):
            return "vermelho"  # IA vence
        elif pretas == 0 or not self.get_movimentos_validos("vermelho"):
            return "branco"    # Jogador vence
        
        return None

class Jogo:
    def __init__(self):
        self.janela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Damas com IA - Minimax e Alpha-Beta")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont('Arial', 24)
        self.fonte_grande = pygame.font.SysFont('Arial', 36, bold=True)
        self.resetar()
    
    def resetar(self):
        """Reseta o jogo para o estado inicial"""
        self.tabuleiro = Tabuleiro()
        self.turno = "branco"  # Jogador humano começa
        self.peca_selecionada = None
        self.movimentos_validos = []
        self.jogando = True
        self.vencedor = None
        self.movimento_ia_pendente = False
        self.tempo_ia = 0
    
    def atualizar(self):
        """Atualiza a tela do jogo"""
        self.tabuleiro.desenhar(self.janela)
        self.desenhar_movimentos_validos()
        self.desenhar_informacoes()
        pygame.display.update()
    
    def desenhar_movimentos_validos(self):
        """Desenha os movimentos válidos para a peça selecionada"""
        if self.peca_selecionada:
            linha, coluna = self.peca_selecionada
            
            # Destaca a peça selecionada
            x = coluna * TAMANHO_QUADRADO + TAMANHO_QUADRADO // 2
            y = linha * TAMANHO_QUADRADO + TAMANHO_QUADRADO // 2
            pygame.draw.circle(self.janela, VERDE, (x, y), RAIO_PECA + 5, 3)
            
            # Desenha os movimentos válidos para esta peça
            for movimento in self.movimentos_validos:
                if movimento[0] == linha and movimento[1] == coluna:
                    linha_dest, col_dest = movimento[2], movimento[3]
                    x_dest = col_dest * TAMANHO_QUADRADO + TAMANHO_QUADRADO // 2
                    y_dest = linha_dest * TAMANHO_QUADRADO + TAMANHO_QUADRADO // 2
                    
                    # Cor diferente para capturas
                    cor = AMARELO if movimento[4] else AZUL_CLARO
                    pygame.draw.circle(self.janela, cor, (x_dest, y_dest), 15)
                    pygame.draw.circle(self.janela, PRETO, (x_dest, y_dest), 15, 1)
    
    def desenhar_informacoes(self):
        """Desenha informações do jogo na tela"""
        # Informações do turno
        turno_texto = f"TURNO: {'JOGADOR (Brancas)' if self.turno == 'branco' else 'IA (Vermelhas)'}"
        turno_surface = self.fonte.render(turno_texto, True, PRETO)
        self.janela.blit(turno_surface, (10, 10))
        
        # Contador de peças
        brancas, pretas, damas_b, damas_p = self.tabuleiro.contar_pecas()
        contador_texto = f"Brancas: {brancas} (Damas: {damas_b}) | Vermelhas: {pretas} (Damas: {damas_p})"
        contador_surface = self.fonte.render(contador_texto, True, PRETO)
        self.janela.blit(contador_surface, (10, 40))
        
        # Instruções
        instrucoes = self.fonte.render("R-Reiniciar | 1-4 Dificuldade | ESPAÇO-IA joga", True, PRETO)
        self.janela.blit(instrucoes, (10, ALTURA - 40))
        
        # Mostrar que a IA está pensando
        if self.turno == "vermelho" and self.jogando:
            pensar_texto = "IA pensando..." + "." * (int(pygame.time.get_ticks() / 500) % 4)
            pensar_surface = self.fonte.render(pensar_texto, True, VERMELHO)
            self.janela.blit(pensar_surface, (LARGURA - 200, 10))
        
        # Mostrar vencedor
        if self.vencedor:
            vencedor_texto = "VOCÊ VENCEU!" if self.vencedor == "branco" else "IA VENCEU!"
            vencedor_surface = self.fonte_grande.render(vencedor_texto, True, VERDE if self.vencedor == "branco" else VERMELHO)
            
            # Fundo semi-transparente
            surf = pygame.Surface((400, 100), pygame.SRCALPHA)
            surf.fill((255, 255, 255, 200))
            self.janela.blit(surf, (LARGURA//2 - 200, ALTURA//2 - 50))
            
            self.janela.blit(vencedor_surface, (LARGURA//2 - vencedor_surface.get_width()//2, ALTURA//2 - 30))
            
            reiniciar_text = self.fonte.render("Pressione R para jogar novamente", True, PRETO)
            self.janela.blit(reiniciar_text, (LARGURA//2 - reiniciar_text.get_width()//2, ALTURA//2 + 20))
    
    def selecionar(self, linha, coluna):
        """Seleciona uma peça no tabuleiro ou move uma peça selecionada"""
        if not self.jogando or self.turno != "branco":
            return
        
        # Se já tem uma peça selecionada, tenta mover
        if self.peca_selecionada:
            # Verifica se o clique é em um movimento válido
            for movimento in self.movimentos_validos:
                if (movimento[0] == self.peca_selecionada[0] and 
                    movimento[1] == self.peca_selecionada[1] and
                    movimento[2] == linha and 
                    movimento[3] == coluna):
                    
                    # Executa o movimento
                    self.executar_movimento(movimento)
                    return
            
            # Se não foi um movimento válido, desseleciona ou seleciona outra peça
            self.peca_selecionada = None
            self.movimentos_validos = []
        
        # Seleciona uma nova peça (se for do jogador atual)
        peca = self.tabuleiro.tabuleiro[linha][coluna]
        if peca in [PEDRA_BRANCA, DAMA_BRANCA]:  # Só pode selecionar peças brancas
            self.peca_selecionada = (linha, coluna)
            # Obtém todos os movimentos válidos para o jogador
            todos_movimentos = self.tabuleiro.get_movimentos_validos("branco")
            # Filtra apenas os movimentos desta peça
            self.movimentos_validos = [m for m in todos_movimentos if m[0] == linha and m[1] == coluna]
    
    def executar_movimento(self, movimento):
        """Executa um movimento no tabuleiro"""
        virou_dama, mensagem = self.tabuleiro.mover(movimento)
        
        if virou_dama and mensagem:
            print(mensagem)
        
        # Limpa seleção
        self.peca_selecionada = None
        self.movimentos_validos = []
        
        # Verifica se o jogo acabou
        self.vencedor = self.tabuleiro.vencedor()
        if self.vencedor:
            self.jogando = False
            print(f"Fim de jogo! Vencedor: {self.vencedor}")
            return
        
        # Muda o turno
        self.turno = "vermelho" if self.turno == "branco" else "branco"
    
    def minimax(self, tabuleiro, profundidade, alpha, beta, maximizando):
        """
        Implementação do algoritmo Minimax com poda Alpha-Beta
        """
        # Condição de parada
        if profundidade == 0 or tabuleiro.vencedor():
            return tabuleiro.avaliar()
        
        if maximizando:
            # IA (vermelhas) quer minimizar a vantagem do jogador
            max_eval = float('-inf')
            movimentos = tabuleiro.get_movimentos_validos("vermelho")
            
            for movimento in movimentos:
                tabuleiro_copia = tabuleiro.copiar()
                tabuleiro_copia.mover(movimento)
                
                eval = self.minimax(tabuleiro_copia, profundidade - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                
                # Poda Alpha-Beta
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            # Simula jogador (brancas) querendo maximizar
            min_eval = float('inf')
            movimentos = tabuleiro.get_movimentos_validos("branco")
            
            for movimento in movimentos:
                tabuleiro_copia = tabuleiro.copiar()
                tabuleiro_copia.mover(movimento)
                
                eval = self.minimax(tabuleiro_copia, profundidade - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                
                # Poda Alpha-Beta
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            
            return min_eval
    
    def melhor_movimento_ia(self, profundidade=3):
        """Encontra o melhor movimento para a IA usando Minimax"""
        print(f"\nIA pensando (profundidade {profundidade})...")
        tempo_inicio = time.time()
        
        melhor_movimento = None
        melhor_valor = float('-inf')
        
        movimentos = self.tabuleiro.get_movimentos_validos("vermelho")
        
        if not movimentos:
            return None
        
        # Para cada movimento possível
        for i, movimento in enumerate(movimentos):
            # Cria cópia do tabuleiro
            tabuleiro_copia = self.tabuleiro.copiar()
            tabuleiro_copia.mover(movimento)
            
            # Avalia o movimento
            valor_movimento = self.minimax(tabuleiro_copia, profundidade - 1, float('-inf'), float('inf'), False)
            
            # Atualiza melhor movimento
            if valor_movimento > melhor_valor:
                melhor_valor = valor_movimento
                melhor_movimento = movimento
        
        tempo_total = time.time() - tempo_inicio
        print(f"IA escolheu um movimento em {tempo_total:.2f} segundos")
        print(f"Valor da jogada: {melhor_valor:.2f}")
        
        return melhor_movimento
    
    def jogada_ia(self, profundidade=3):
        """Executa a jogada da IA"""
        if self.turno != "vermelho" or not self.jogando or self.vencedor:
            return
        
        # Encontra o melhor movimento
        melhor_movimento = self.melhor_movimento_ia(profundidade)
        
        if melhor_movimento:
            # Pequeno delay para parecer mais natural
            pygame.time.delay(500)
            
            # Executa o movimento
            self.executar_movimento(melhor_movimento)
            
            # Mostra informações no console
            linha_i, col_i, linha_f, col_f, capturas = melhor_movimento
            print(f"IA moveu de ({linha_i},{col_i}) para ({linha_f},{col_f})")
            if capturas:
                print(f"Capturou {len(capturas)} peça(s)")
        else:
            # Se não há movimentos válidos, o jogador vence
            self.vencedor = "branco"
            self.jogando = False
    
    def obter_posicao_mouse(self, pos):
        """Converte a posição do mouse para coordenadas do tabuleiro"""
        x, y = pos
        linha = y // TAMANHO_QUADRADO
        coluna = x // TAMANHO_QUADRADO
        return linha, coluna
    
    def executar(self):
        """Loop principal do jogo"""
        executando = True
        profundidade_ia = 3  # Profundidade padrão
        
        while executando:
            self.relogio.tick(60)
            
            # Processa eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    executando = False
                
                if evento.type == pygame.KEYDOWN:
                    # Reiniciar o jogo
                    if evento.key == pygame.K_r:
                        print("\n=== Jogo reiniciado ===")
                        self.resetar()
                    
                    # Forçar jogada da IA
                    if evento.key == pygame.K_SPACE and self.turno == "vermelho" and self.jogando:
                        print("Forçando jogada da IA...")
                        self.jogada_ia(profundidade_ia)
                    
                    # Ajustar dificuldade
                    if evento.key == pygame.K_1:
                        profundidade_ia = 1
                        print(f"Dificuldade: Fácil (profundidade {profundidade_ia})")
                    if evento.key == pygame.K_2:
                        profundidade_ia = 2
                        print(f"Dificuldade: Médio (profundidade {profundidade_ia})")
                    if evento.key == pygame.K_3:
                        profundidade_ia = 3
                        print(f"Dificuldade: Difícil (profundidade {profundidade_ia})")
                    if evento.key == pygame.K_4:
                        profundidade_ia = 4
                        print(f"Dificuldade: Expert (profundidade {profundidade_ia})")
                
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    linha, coluna = self.obter_posicao_mouse(pos)
                    if 0 <= linha < LINHAS and 0 <= coluna < COLUNAS:
                        self.selecionar(linha, coluna)
            
            # Jogada automática da IA
            if self.jogando and self.turno == "vermelho":
                # Pequeno delay antes da IA jogar
                if pygame.time.get_ticks() > 2000:  # Espera 1 segundo após mudança de turno
                    self.jogada_ia(profundidade_ia)
            
            # Atualiza a tela
            self.atualizar()
        
        pygame.quit()
        sys.exit()

# Executar o jogo
if __name__ == "__main__":
    print("=" * 60)
    print("DAMAS COM IA - ALGORITMO MINIMAX E ALPHA-BETA PRUNING")
    print("=" * 60)
    print("\nREGRAS:")
    print("1. Você joga com as peças BRANCAS")
    print("2. Captura é OBRIGATÓRIA se disponível")
    print("3. Clique em uma peça para selecioná-la")
    print("4. Clique em um destaque para mover")
    print("\nCONTROLES:")
    print("R - Reiniciar jogo")
    print("ESPAÇO - Forçar jogada da IA (quando for a vez dela)")
    print("\nIniciando jogo...")
    
    jogo = Jogo()
    jogo.executar()
JogodeDamas.py
A mostrar JogodeDamas.py.