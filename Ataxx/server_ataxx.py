import socket
import time
import numpy as np
from tkinter import *
import numpy as np
import copy
import random as r
import pickle


b_w="BLUE WINS!!"
r_w="RED WINS!!"
t = "IT'S A TIE!!"

print("Escolha número de linhas/colunas (4 ou 6):")
NB = int(input())  # Board number of rows/columns
size_of_board = 600
size_of_square = size_of_board/NB
symbol_size = (size_of_square*0.75-10)/2
symbol_thickness = 20
blue_color = '#496BAB'
red_color = '#F33E30'

possible_moves_global=[]
position_global=[]
origin_pos=[]
moves_blue_global=[]
moves_red_global=[]
blue_pieces=[]
red_pieces=[]
board2=[]

class ServerAtaxx():
    def __init__(self):
        self.window = Tk()
        self.window.title('Ataxx')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board, background="white")
        self.canvas.pack()
        self.board = np.zeros(shape=(NB, NB))
        self.board[0][0]=2
        self.board[0][NB-1]=1
        self.board[NB-1][NB-1]=1
        self.board[NB-1][0]=2
        self.player_blue_turn = True
        self.game_ended = False
        self.init_draw_board()

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
        if self.game_ended: return
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
        if self.game_ended: return
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
        if not np.array_equal(pos, []):
            return self.board[pos[0]][pos[1]] == 0

    def valid_move(self, logical_pos):
        return self.is_square_clear(logical_pos)

    #dado a peça selecionada, devolve uma lista
    #com todos os movimentos possiveis da mesma
    def possible_moves(self, move):
        possible_moves=[]
        for i in range(max(0,move[0]-2), min(NB, move[0]+3)):
            for j in range(max(0,move[1]-2), min(NB, move[1]+3)):

                if self.is_square_clear([i,j]):
                    possible_moves.append([i,j])

        return possible_moves

    def get_positions(self, player):
        pos = np.argwhere(self.board == player)
        return pos.tolist()

    def get_all_possible_moves(self, positions):
        all_moves = {}

        for pos in positions:
            moves = self.possible_moves(pos)
            all_moves[tuple(pos)] = moves

        return all_moves


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
        print()
        if blue>red:
            print(b_w)
        elif blue<red:
            print(r_w)
        else:
            print(t)
        self.game_ended = True

#----------------------TRANSFORMAR EM MATRIZ PARA APLICAR REGRAS---------------

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


#----------------------------------- Verificaçao movimentos e jogadas ------------------------------------

    # desenha no tabuleiro as jogadas possiveis da bola selecionada
    def draw_possible_moves(self, possible_moves):
        time.sleep(1)
        moves=[0]*len(possible_moves)
        for i in range(len(possible_moves)):
            moves[i]=self.convert_logical_to_grid_position(possible_moves[i])
            self.canvas.create_oval(moves[i][0]-symbol_size, moves[i][1] - symbol_size,
                                    moves[i][0]+symbol_size, moves[i][1]+ symbol_size,
                                    width=symbol_thickness, outline="gray", fill="gray", tags="possible")
        self.window.update()
        time.sleep(1)




    def clear_possible_moves(self):
        self.canvas.delete("possible")

#----------------------- MOUSE -----------------------------------------------------------

    def handle_client(self, origin, logical_pos):
        if self.game_ended: return
        if self.board[origin[0]][origin[1]] == 1 and self.player_blue_turn:
            possible_moves_global = self.possible_moves(origin)
            self.draw_possible_moves(possible_moves_global)
            if not np.array_equal(possible_moves_global, []):
                self.handle_client2(origin, logical_pos)

        elif self.board[origin[0]][origin[1]] == 2 and not self.player_blue_turn:
            possible_moves_global = self.possible_moves(origin)
            self.draw_possible_moves(possible_moves_global)
            if not np.array_equal(possible_moves_global, []):
                self.handle_client2(origin, logical_pos)


    def handle_client2(self, origin_pos, position_global):
        if self.game_ended: return
        if self.player_blue_turn:
            player=1
        else:
            player=2
        if self.valid_move(position_global):
            if self.player_blue_turn and self.board[origin_pos[0]][origin_pos[1]] == 1:
                self.draw_blue(position_global)
                self.execute_move(position_global, origin_pos, player)

            elif not self.player_blue_turn and self.board[origin_pos[0]][origin_pos[1]] == 2:
                self.draw_red(position_global)
                self.execute_move(position_global, origin_pos, player)
        self.clear_possible_moves()


Game = "Ataxx"  # type of game

def start_server(host='localhost', port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)

    print("Waiting for two agents to connect...")
    agent1, addr1 = server_socket.accept()
    print("Agent 1 connected from", addr1)
    bs = b'AG1 ' + Game.encode()
    agent1.sendall(bs)

    agent2, addr2 = server_socket.accept()
    print("Agent 2 connected from", addr2)
    bs = b'AG2 ' + Game.encode()
    agent2.sendall(bs)

    print("------------------------")
    agents = [agent1, agent2]
    current_agent = 0

    jog = 0

    game = ServerAtaxx()

    while not game.game_ended:
        game.window.update()
        posicoes = game.get_positions(current_agent+1)
        all_pos = game.get_all_possible_moves(posicoes)
        all_pos_bytes = pickle.dumps(all_pos)
        agents[current_agent].sendall(all_pos_bytes)
        try:
            data = agents[current_agent].recv(1024)
            selected_key, selected_object = pickle.loads(data)
            origin = np.array(selected_key)
            move = np.array(selected_object)
            if not data:
                break

            # Process the move
            print("Agent", current_agent+1, ": ")
            print(f"Origin: {origin}")
            print(f'Move: {move}')
            game.handle_client(origin, move)

            # Switch to the other agent
            current_agent = 1 - current_agent
            jog += 1
            if game.game_ended:
                break
            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            break

    print("\n-----------------\nGAME END\n-----------------\n")
    time.sleep(1)
    agent1.close()
    agent2.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
