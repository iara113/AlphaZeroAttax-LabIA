#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Trabalho realizado por: Beatriz Silva && Margarida Vila-Chã


from tkinter import *
import numpy as np
import copy
import random as r



b_w="BLUE WINS!!"
r_w="RED WINS!!"


NB = int(input())  # Board number of rows/columns
size_of_board = 600
size_of_square = size_of_board/NB
symbol_size = (size_of_square*0.75-10)/2
symbol_thickness = 20
blue_color = '#496BAB'
red_color = '#F33E30'
possible_moves_global=[]
position_global=[]
bool=False
origin_pos=[]
moves_blue_global=[]
moves_red_global=[]
blue_pieces=[]
red_pieces=[]
board2=[]







class ataxx():
    def __init__(self):
        self.window = Tk()
        self.window.title('Ataxx')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board, background="white")
        self.canvas.pack()
        self.window.bind('<Button-1>', self.click)
        self.board = np.zeros(shape=(NB, NB))
        self.board[0][0]=2
        self.board[0][NB-1]=1
        self.board[NB-1][NB-1]=1
        self.board[NB-1][0]=2
        self.player_blue_turn = True
        self.game_ended = False
        self.mode1=0
        self.mode2=0
        self.init_draw_board()


    def mainloop(self):
        self.window.mainloop()
        if self.mode1==1 and self.mode2==1:
            self.ai_vs_ai()
            
            
            
            
            
            
    #def __init__(self):
        #self.janela = Tk(className="Teste")
        #self.janela.geometry("200x200")
        #self.janela['bg'] = "#1E90FF"
        #b1 = Button(self.janela,text = "Jogador vs Jogador",activeforeground = "blue",activebackground = "#FF6347",width=15,
                           #height=2)  
  
        #b2 = Button(self.janela, text = "Jogador vs PC",activeforeground = "blue",activebackground = "#FF6347",width=15,
                           #height=2) 
  
        #b3 = Button(self.janela, text = "PC vs PC",activeforeground = "blue",activebackground = "#FF6347", width=15,
                           #height=2)
        
        #b1.place(x=200/3 - 25, y=20)
  
        #b2.place(x=200/3 - 25, y = 75)  
  
        #b3.place(x = 200/3 - 25, y=130)  
        
        
    #def mainloop(self):
        #self.janela.mainloop()


    #----------------DESENHO DO TABULEIRO---------------------------------------------------------------------------------------------------------

    def init_draw_board(self):
        self.canvas.delete("all")
        for i in range(NB-1):
            self.canvas.create_line((i+1)*size_of_square, 0, (i+1)*size_of_square, size_of_board)
        for i in range(NB-1):
            self.canvas.create_line(0,(i+1)*size_of_square, size_of_board, (i+1)*size_of_square)
        self.canvas.create_oval(size_of_square/2 - symbol_size, size_of_square/2 - symbol_size,
                                size_of_square/2 + symbol_size, size_of_square/2 + symbol_size,
                                width=symbol_thickness, outline=red_color,
                                fill=red_color)
        self.canvas.create_oval(size_of_board - size_of_square/2 - symbol_size,size_of_board - size_of_square/2 - symbol_size,
                                size_of_board - size_of_square/2 + symbol_size, size_of_board - size_of_square/2 + symbol_size,
                                width=symbol_thickness, outline=blue_color,
                                fill=blue_color)
        self.canvas.create_oval(size_of_square/2 - symbol_size,size_of_board - size_of_square/2 - symbol_size,
                                size_of_square/2 + symbol_size, size_of_board - size_of_square/2 + symbol_size,
                                width=symbol_thickness, outline=blue_color,
                                fill=blue_color)
        self.canvas.create_oval(size_of_board - size_of_square/2 - symbol_size, size_of_square/2- symbol_size,
                                size_of_board - size_of_square/2 + symbol_size, size_of_square/2 + symbol_size,
                                width=symbol_thickness, outline=red_color,
                                fill=red_color)


    def update_board(self, x, y, origin):

        #atualiza a matriz do tabuleiro

        for i in range(max(0, x-1), min(NB, x+2)):
            for j in range(max(0, y-1), min(NB, y+2)):
                if not self.is_square_clear([i,j]):
                    if self.player_blue_turn:
                        self.draw_blue([i,j])
                    else:
                        self.draw_red([i,j])
                    self.board[i][j]=self.board[x][y]
        if x-origin[0]== 2 or y-origin[1]== 2 or x-origin[0]== -2 or y-origin[1]== -2:
            self.board[origin[0]][origin[1]]=0
            pos=self.convert_logical_to_grid_position(origin)
            self.draw_whitespace(pos)
        self.score()
        self.all_moves()
        self.player_blue_turn = not self.player_blue_turn

    def update_board2(self, board, x, y, origin):
        for i in range(max(0, x-1), min(NB, x+2)):
            for j in range(max(0, y-1), min(NB, y+2)):
                if not board[pos[0]][pos[1]] == 0:
                    board[i][j]=board[x][y]
        if x-origin[0]== 2 or y-origin[1]== 2 or x-origin[0]== -2 or y-origin[1]== -2:
            board[origin[0]][origin[1]]=0

    def all_moves(self):
        global moves_blue_global
        global moves_red_global
        global blue_pieces
        global red_pieces
        for i in range(NB):
            for j in range(NB):
                if self.board[i][j]==1:
                    moves_blue_global.append(self.possible_moves([i,j]))
                    blue_pieces.append([i,j])
                elif self.board[i][j]==2:
                    moves_red_global.append(self.possible_moves([i,j]))
                    red_pieces.append([i,j])
        if len(moves_blue_global)==0:
            self.no_moves(1)
        elif len(moves_red_global)==0:
            self.no_moves(2)
        moves_blue_global=[]
        moves_red_global=[]

    def no_moves(self, player):
        print("3")
        if player==1:
            for i in range(NB):
                for j in range(NB):
                    if self.board[i][j]==0:
                        self.board[i][j]=2
                        self.draw_red([i,j])
        elif player==2:
            for i in range(NB):
                for j in range(NB):
                    if self.board[i][j]==0:
                        self.board[i][j]=1
                        self.draw_blue([i,j])
        self.score()




    def execute_move(self, move, origin, player):

        
        self.board[move[0]][move[1]] = player
        self.update_board(move[0], move[1], origin)

    def is_square_clear(self, pos):
        #print(pos)
        if not np.array_equal(pos, []):
            return self.board[pos[0]][pos[1]] == 0

    def valid_move(self, logical_pos):
        return self.is_square_clear(logical_pos)

    def possible_moves(self, move):

      #dado a peça selecionada, devolve uma lista
    #com todos os movimentos possiveis da mesma 

        possible_moves=[]
        for i in range(max(0,move[0]-2), min(NB, move[0]+3)):
            for j in range(max(0,move[1]-2), min(NB, move[1]+3)):
                
                if self.is_square_clear([i,j]):
                    possible_moves.append([i,j])
        
        return possible_moves

    def score(self):
        cont_blue=0
        cont_red=0
        cheio=True
        for i in range(NB):
            for j in range(NB):
                if self.board[i][j]==1:
                    cont_blue+=1
                elif self.board[i][j]==2:
                    cont_red+=1
                if self.board[i][j]==0:
                    cheio=False
        print("Blue score= ",  cont_blue)
        print("Red score= ",  cont_red)
        print("------------------------")
        self.window.title("Ataxx - Red : %d vs %d : Blue" % (cont_red, cont_blue))
        if cont_blue==0:
            self.game_is_over(cont_red, cont_blue)
        elif cont_red==0:
            self.game_is_over(cont_red, cont_blue)
        elif cheio:
            self.game_is_over(cont_red, cont_blue)








    def game_is_over(self, red, blue):
        print("Blue score= ",  blue)
        print("Red score= ",  red)
        print("\n")
        if blue>red:
            print(b_w)
            a=1
        else:
            print(r_w)
            a=2
        print("\n")
        self.clear_possible_moves()
        self.window.destroy()





         














#----------------------TRANSFORMAR EM MATRIZ PARA APLICAR REGRAS-------------------------------------------------------------------------------
# Drawing Functions:
# The modules required to draw required game based object on canvas
# logical_position = grid value on the board
# grid_position = actual pixel values of the center of the grid

    def convert_logical_to_grid_position(self, logical_pos):
        logical_pos = np.array(logical_pos, dtype=int)
        return np.array((size_of_square)*logical_pos + size_of_square/2)

    def convert_grid_to_logical_position(self, grid_pos):
        grid_pos = np.array(grid_pos)
        return np.array(grid_pos//size_of_square, dtype=int)

#-----------------------DESENHAR PECAS----------------------------------------
    def draw_whitespace(self, grid_pos):

        

        self.canvas.create_rectangle(grid_pos[0] - symbol_size, grid_pos[1] - symbol_size,
                            grid_pos[0] + symbol_size, grid_pos[1] + symbol_size,
                            width=symbol_thickness, outline="white",
                            fill="white")


    def draw_blue(self, logical_pos):
        logical_pos = np.array(logical_pos)
        grid_pos = self.convert_logical_to_grid_position(logical_pos)
        self.canvas.create_oval(grid_pos[0] - symbol_size, grid_pos[1] - symbol_size,
                            grid_pos[0] + symbol_size, grid_pos[1] + symbol_size,
                            width=symbol_thickness, outline=blue_color,
                            fill=blue_color)

    def draw_red(self, logical_pos):
        logical_pos = np.array(logical_pos)
        grid_pos = self.convert_logical_to_grid_position(logical_pos)
        self.canvas.create_oval(grid_pos[0] - symbol_size, grid_pos[1] - symbol_size,
                            grid_pos[0] + symbol_size, grid_pos[1] + symbol_size,
                            width=symbol_thickness, outline=red_color,
                            fill=red_color)

    def draw_possible_moves(self, possible_moves):

        # desenha no tabuleiro as jogadas possiveis da bola selecionada

        moves=[0]*len(possible_moves)
        for i in range(len(possible_moves)):
            moves[i]=self.convert_logical_to_grid_position(possible_moves[i])
            self.canvas.create_oval(moves[i][0]-symbol_size, moves[i][1] - symbol_size,
                                    moves[i][0]+symbol_size, moves[i][1]+ symbol_size,
                                    width=symbol_thickness, outline="gray", fill="gray", tags="possible")


    def clear_possible_moves(self):

        

        self.canvas.delete("possible")
        
    #-------------------------------------- Minimax Algoritmo ----------------------------------------------------


    def minimax2(board, depth, alpha, beta, ROWS, win, maximazing):
        if depth == 0 or verif_end(playerMax,win,ROWS,board) != -1:
            return avali(changeplayer(playerMin),ROWS,board), board

        if maximazing:
            maxEval = -math.inf
            best_move = None
            for move in total_moves(board, playerMax, ROWS):
                evaluation = minimax2(move, depth-1, alpha, beta, ROWS, win, False)
                if evaluation > maxEval:
                    best_move = move
                    maxEval = evaluation
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    return math.inf, board
            return maxEval
        minEval = math.inf
        for move in total_moves(board, playerMax, ROWS):
            evaluation = minimax2(move, depth-1, alpha, beta, ROWS, win, True)
            if evaluation < minEval:
                minEval = evaluation
            beta = min(beta, evaluation)
            if beta <= alpha:
                return -math.inf, board
        return minEval

    
    def minimax(board, depth, playerMax, ROWS, win, playerMin):
        if depth == 0 or verif_end(playerMax,win,ROWS,board) != -1:
            return avali(changeplayer(playerMin),ROWS,board), board

        if playerMax != playerMin:
            maxEval = -math.inf
            best_move = None
            for move in total_moves(board, playerMax, ROWS):
                evaluation = minimax(move, depth-1, changeplayer(playerMax), ROWS, win, playerMin)[0]
                if evaluation > maxEval:
                    best_move = move
                    maxEval = evaluation
            return maxEval, best_move
        minEval = math.inf
        for move in total_moves(board, playerMax, ROWS):
            evaluation = minimax(move, depth-1, changeplayer(playerMax), ROWS, win, playerMin)[0]
            if evaluation < minEval:
                minEval = evaluation
        return minEval, minEval
    
    #----------------------------------- Verificaçao movimentos e jogadas ------------------------------------


    def total_moves(board, player,ROWS):
        moves = []
        moves_aval = []
        for peca in totalpecas(board, ROWS, player):
            moves_aval = plays_eval(peca,ROWS,board)
            for move in moves_aval:
                temp_board = deepcopy(board)
                temp_peca = (peca[0],peca[1])
                new_board = simula_move(temp_peca, move, temp_board, player, ROWS)
                moves.append(new_board)
        return moves

    def random(self):
        if NB ==6 or NB==7:
            # move aleatório
            if not self.game_ended:
                moves_total={}
                pieces=[]
                self.all_moves()
                global position_global
                global origin_pos
                global blue_pieces
                global red_pieces
                if NB==7:
                    if self.player_blue_turn:
                        for piece in blue_pieces:
                            piece2=(piece[0],piece[1])
                            moves=self.possible_moves(piece)
                            moves_total[piece2]=moves
                        for key in moves_total.keys():
                            pieces.append(key)
                        i = r.randint(0,len(pieces)-1)
                        random_piece=pieces[i]
                        moves=moves_total[random_piece]
                        while np.array_equal(moves, []):
                            i = r.randint(0,len(pieces)-1)
                            random_piece=pieces[i]
                            moves=moves_total[random_piece]
                        i=r.randint(0, len(moves)-1)
                        random_move=moves[i]
                        origin_pos=random_piece
                        position_global = random_move
                        self.click2()
                if not self.player_blue_turn:
                    for piece in red_pieces:
                        piece2=(piece[0],piece[1])
                        moves=self.possible_moves(piece)
                        moves_total[piece2]=moves
                    for key in moves_total.keys():
                        pieces.append(key)
                    i = r.randint(0,len(pieces)-1)
                    random_piece=pieces[i]
                    moves=moves_total[random_piece]
                    while np.array_equal(moves, []):
                        i = r.randint(0,len(pieces)-1)
                        random_piece=pieces[i]
                        moves=moves_total[random_piece]
                    i=r.randint(0, len(moves)-1)
                    random_move=moves[i]
                    origin_pos=random_piece
                    position_global = random_move
                    self.click2()

#----------------------- MOUSE -----------------------------------------------------------

    def click(self, event):

        
        if self.game_ended: return
        grid_pos = [event.x, event.y]
        logical_pos = self.convert_grid_to_logical_position(grid_pos)
        global origin_pos
        global possible_moves_global
        origin_pos = logical_pos
        self.random()
        if self.board[logical_pos[0]][logical_pos[1]] == 1 and self.player_blue_turn:
            possible_moves_global = self.possible_moves(logical_pos)
            if not np.array_equal(possible_moves_global, []):
                self.window.bind("<Button-1>", self.second_click)
            self.draw_possible_moves(possible_moves_global)
        elif self.board[logical_pos[0]][logical_pos[1]] == 2 and not self.player_blue_turn:
            possible_moves_global = self.possible_moves(logical_pos)
            if not np.array_equal(possible_moves_global, []):
                self.window.bind("<Button-1>", self.second_click)
            self.draw_possible_moves(possible_moves_global)


    def second_click(self, event):

        

        global bool
        grid_pos = [event.x, event.y]
        logical_pos = self.convert_grid_to_logical_position(grid_pos)
        global possible_moves_global
        possible_moves_global=np.array(possible_moves_global, dtype=int)
        for element in possible_moves_global:
            
            if np.array_equal(logical_pos, element):
                global position_global
                position_global = logical_pos
                bool=True
        bool = True
        self.click2()
        possible_moves_global=[]
        position_global=[]


    def click2(self):

        global bool
        if self.player_blue_turn:
            player=1
        else:
            player=2
        if self.valid_move(position_global):
            if self.second_click_pressed(bool):
                if self.player_blue_turn and self.board[origin_pos[0]][origin_pos[1]] == 1:
                    self.draw_blue(position_global)
                    self.execute_move(position_global, origin_pos, player)
                elif not self.player_blue_turn and self.board[origin_pos[0]][origin_pos[1]] == 2:
                    self.draw_red(position_global)
                    self.execute_move(position_global, origin_pos, player)
        self.clear_possible_moves()
        self.window.bind("<Button-1>", self.click)
        

    def second_click_pressed(self, bool):

        

        if bool:
            return True
        return False
#--------------------------------------------------------------------------------------------------------
    def ai_vs_ai(self):
        while True:
            self.random()





def PvsP():
    game = ataxx()
    game.mainloop()
    start_menu()


def PvsAI():

    print("")
    print("Nivel de dificuldade:")
    print("(1) Facil")
    print("(2) Medio")
    print("(3) Dificil")
    print("(4) Voltar ao menu")
    print("")
    n=int(input("Opção:"))
    while(n!=1 and n!=2 and n!=3 and n!=4):
        print("------------------------------------------------------------")
        print("")
        print("Inválido")
        print("")
        print("Nivel de dificuldade:")
        
        print("(1) Facil")
        print("(2) Medio")
        print("(3) Dificil")
        print("(4) Voltar ao menu")
        print("")
        n=int(input("Opção:"))
        

    if(n==4):
        start_menu()
    game = ataxx()
    game.mode1=n
    game.mainloop()
    start_menu()

def AIvsAI():

    difficulty = {1: 'Fácil', 2: 'Médio', 3: 'Difícil'}

    print("")
    print("Nivel de dificuldade:")
    print("(1) "+difficulty[1])
    print("(2) "+difficulty[2])
    print("(3) "+difficulty[3])
    print("")
    n1=int(input("Opção:"))
    while(n1!=1 and n1!=2 and n1!=3):
        print("------------------------------------------------------------")
        print("")
        print("Inválido")
        print("")
        print("Choose the difficulty:")
        print("(1) "+difficulty[1])
        print("(2) "+difficulty[2])
        print("(3) "+difficulty[3])
        print("")
        n1=int(input("Opção:"))

    print("")
    print("Nível de dificuldade:")
    print("(1) "+difficulty[1])
    print("(2) "+difficulty[2])
    print("(3) "+difficulty[3])
    print("")
    n2=int(input("Opção:"))
    while(n2!=1 and n2!=2 and n2!=3):
        print("------------------------------------------------------------")
        print("")
        print("Inválido")
        print("")
        print("Nível de dificuldade:")
        print("(1) "+difficulty[1])
        print("(2) "+difficulty[2])
        print("(3) "+difficulty[3])
        print("")
        n2=int(input("Opção:"))


    print("Nível dificuldade:")
    print("(1) "+difficulty[n1]+" vs "+difficulty[n2])
    print("(2) Voltar ao menu")
    print("")
    op=input("Opção: ")
    while(op!="1" and op!="2"):
        print("------------------------------------------------------------")
        print("")
        print("Inválido")
        print("")
        print("Nivel dificuldade:")
        print("(1) "+difficulty[n1]+" vs "+difficulty[n2])
        print("(2) Voltar ao menu ")
        print("")
        op=input("Opção: ")

    if(op=="2"):
        start_menu()

    game = ataxx()
    game.mode1=n1
    game.mode2=n2
    game.mainloop()

    start_menu()


def start_menu():
    print("")
    print("")
    print("Modo de Jogo:")
    print("")
    print("(1) Jogador vs Jogador")
    print("(2) Jogador vs Máquina")
    print("(3) Máquina vs Máquina")
    print("(4) Exit")
    print("")
    escolha=input("Modo: ")
    print("")

    while(escolha!="1" or escolha!="2" or escolha!="3" or escolha!="4"):
        if escolha=="1":
            print("--------------------------------------")
            print("")
            print("Jogador vs Jogador")
            print("")
            PvsP()
            break

        elif escolha=="2":
            print("----------------------------------")
            print("")
            print("Jogador vs Máquina")
            print("")
            PvsAI()
            break

        elif escolha=="3":
            print("----------------------------------")
            print("")
            print("Máquina vs Máquina")
            print("")
            AIvsAI()
            break
        elif escolha=="4":
            quit()
        else:
            print("------------------------------------------------------------")
            print("")
            print("Inválido")
            print("")
            print("")
            print("")
            print("Modo de Jogo:")
            print("")
            print("(1) Jogador vs Jogador")
            print("(2) Jogador vs Máquina")
            print("(3) Máquina vs Máquina")
            print("(4) Sair")
            print("")
            escolha=input("Modo: ")
            print("")



start_menu()


# In[ ]:




