import pygame
import numpy as np
import itertools
import sys
import networkx as nx
import collections
from pygame import gfxdraw
import time
import socket
import time
import copy
import random
import pickle

# Define board size
print("Select board size (7 or 9): ")
size = int (input())

# Game constantes
BOARD_BROWN = (141, 104, 75)    # Change color as desired
BOARD_WIDTH = 600           #New size of board
BOARD_BORDER = 75
STONE_RADIUS = int (abs(BOARD_WIDTH/size*20*0.02))      #Ajust stone size to grid size
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURN_POS = (BOARD_BORDER, 20)
SCORE_POS = (BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER + 30)
DOT_RADIUS = 2


def make_grid(size):
    """Return list of (start_point, end_point pairs) defining gridlines

    Args:
        size (int): size of grid

    Returns:
        Tuple[List[Tuple[float, float]]]: start and end points for gridlines
    """
    start_points, end_points = [], []

    # vertical start points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_BORDER)
    start_points += list(zip(xs, ys))

    # horizontal start points (constant x)
    xs = np.full((size), BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    start_points += list(zip(xs, ys))

    # vertical end points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    end_points += list(zip(xs, ys))

    # horizontal end points (constant x)
    xs = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    end_points += list(zip(xs, ys))

    return (start_points, end_points)


def xy_to_colrow(x, y, size):
    """Convert x,y coordinates to column and row number

    Args:
        x (float): x position
        y (float): y position
        size (int): size of grid

    Returns:
        Tuple[int, int]: column and row numbers of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x_dist = x - BOARD_BORDER
    y_dist = y - BOARD_BORDER
    col = int(round(x_dist / inc))
    row = int(round(y_dist / inc))
    return col, row


def colrow_to_xy(col, row, size):
    """Convert column and row numbers to x,y coordinates

    Args:
        col (int): column number (horizontal position)
        row (int): row number (vertical position)
        size (int): size of grid

    Returns:
        Tuple[float, float]: x,y coordinates of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x = int(BOARD_BORDER + col * inc)
    y = int(BOARD_BORDER + row * inc)
    return x, y


def has_no_liberties(board, group):
    """Check if a stone group has any liberties on a given board.

    Args:
        board (object): game board (size * size matrix)
        group (List[Tuple[int, int]]): list of (col,row) pairs defining a stone group

    Returns:
        [boolean]: True if group has any liberties, False otherwise
    """
    for x, y in group:
        if x > 0 and board[x - 1, y] == 0:
            return False
        if y > 0 and board[x, y - 1] == 0:
            return False
        if x < board.shape[0] - 1 and board[x + 1, y] == 0:
            return False
        if y < board.shape[0] - 1 and board[x, y + 1] == 0:
            return False
    return True


def get_stone_groups(board, color):
    """Get stone groups of a given color on a given board

    Args:
        board (object): game board (size * size matrix)
        color (str): name of color to get groups for

    Returns:
        List[List[Tuple[int, int]]]: list of list of (col, row) pairs, each defining a group
    """
    size = board.shape[0]
    color_code = 1 if color == "black" else 2
    xs, ys = np.where(board == color_code)
    graph = nx.grid_graph(dim=[size, size])
    stones = set(zip(xs, ys))
    all_spaces = set(itertools.product(range(size), range(size)))
    stones_to_remove = all_spaces - stones
    graph.remove_nodes_from(stones_to_remove)
    return nx.connected_components(graph)


def is_valid_move(col, row, board):
    """Check if placing a stone at (col, row) is valid on board

    Args:
        col (int): column number
        row (int): row number
        board (object): board grid (size * size matrix)

    Returns:
        boolean: True if move is valid, False otherewise
    """
    # TODO: check for ko situation (infinite back and forth)
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False
    return board[col, row] == 0


class ServerGo:
    def __init__(self, size, player1, player2):
        self.board = np.zeros((size, size))
        self.size = size
        self.black_turn = True
        self.prisoners = collections.defaultdict(int)
        self.start_points, self.end_points = make_grid(self.size)
        self.player1 = player1
        self.player2 = player2
        self.player1_passed = False
        self.player2_passed = False
        self.current_player = self.player1 if self.black_turn else self.player2
        self.human_has_played = False

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        self.screen = screen
        self.ZOINK = pygame.mixer.Sound("wav/zoink.wav")
        self.CLICK = pygame.mixer.Sound("wav/click.wav")
        self.font = pygame.font.SysFont("arial", 30)


    def clear_screen(self):

        # fill board and add gridlines
        self.screen.fill(BOARD_BROWN)
        for start_point, end_point in zip(self.start_points, self.end_points):
            pygame.draw.line(self.screen, BLACK, start_point, end_point)

        # add guide dots
        guide_dots = [3, self.size // 2, self.size - 4]
        for col, row in itertools.product(guide_dots, guide_dots):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, DOT_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, DOT_RADIUS, BLACK)

        pygame.display.flip()


    def check_end_game(self):
        # Check if both players passed or there are no more valid moves
        if self.passed_twice() or not any(is_valid_move(col, row, self.board) for col in range(self.size) for row in range(self.size)):
            print('aqui')
            return True
        return False

    def passed_twice(self):
        # Check if both players passed their turn twice in a row
        return self.player1_passed and self.player2_passed


    def pass_move(self):
        if self.black_turn:
            self.player1_passed = True
        else:
            self.player2_passed = True

        self.black_turn = not self.black_turn
        self.draw()

        # Check for end-of-game condition after a pass
        if self.check_end_game():
            self.print_final_scores()
            pygame.quit()
            sys.exit()

    def print_final_scores(self):
        score_black = self.prisoners['black']
        score_white = self.prisoners['white']
        print("Game Over!")
        print(f"Black's Prisoners: {score_black}")
        print(f"White's Prisoners: {score_white}")
        if score_black > score_white:
            print("Black wins!")
        elif score_black < score_white:
            print("White wins!")
        else:
            print("It's a tie!")

    def print_scores(self):
        score_black = self.prisoners['black']
        score_white = self.prisoners['white']
        print(f"Black's Prisoners: {score_black}")
        print(f"White's Prisoners: {score_white}")
        print("------------------------")

    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_click()
            if event.type == pygame.QUIT:
                self.print_final_scores()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    self.pass_move()

    def handle_click(self):
        # get board position
        x, y = pygame.mouse.get_pos()
        col, row = xy_to_colrow(x, y, self.size)
        if not is_valid_move(col, row, self.board):
            self.ZOINK.play()
            return

        # update board array
        #self.board[col, row] = 1 if self.black_turn else 2
        self.board[col, row] = 1 if self.current_player == self.player1 else 2

        self.handle_captures(col, row, "black" if self.current_player == self.player1 else "white")
        # change turns and draw screen
        self.CLICK.play()
        self.black_turn = not self.black_turn
        self.current_player = self.player1 if self.black_turn else self.player2  # Update current player
        self.draw()
        print(f'Move: ({col}, {row})')
        self.print_scores()
        self.human_has_played = True


    def handle_captures(self, col, row, color):
        # Handle captures for a given move at (col, row) and color
        other_color = "white" if color == "black" else "black"
        capture_happened = False

        for group in list(get_stone_groups(self.board, other_color)):
            if has_no_liberties(self.board, group):
                capture_happened = True
                for i, j in group:
                    self.board[i, j] = 0
                self.prisoners[color] += len(group)

        if not capture_happened:
            group = None
            for group in get_stone_groups(self.board, color):
                if (col, row) in group:
                    break
            if has_no_liberties(self.board, group):
                if not self.current_player_is_human():
                    player_name = "Player 1" if color == "black" else "Player 2"
                    print(f"{player_name} has no liberties.")
                self.ZOINK.play()
                self.board[col, row] = 0
                return


    def draw(self):
        # draw stones - filled circle and antialiased ring
        self.clear_screen()
        for col, row in zip(*np.where(self.board == 1)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, BLACK)
        for col, row in zip(*np.where(self.board == 2)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, WHITE)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, WHITE)

        # text for score and turn info
        score_msg = (
            f"Black's Prisoners: {self.prisoners['black']}"
            + f"     White's Prisoners: {self.prisoners['white']}"
        )
        txt = self.font.render(score_msg, True, BLACK)
        self.screen.blit(txt, SCORE_POS)
        turn_msg = (
            f"{'Black' if self.black_turn else 'White'} to move. "
            + "Click to place stone, press P to pass."
        )
        txt = self.font.render(turn_msg, True, BLACK)
        self.screen.blit(txt, TURN_POS)

        pygame.display.flip()

    def current_player_is_human(self):
        return self.current_player is None or self.current_player==0 or self.current_player==1

Game = "Go"  # type of game

def start_server(host='localhost', port=5000):

    print("Select Player 1 (H for human, A for AI): ")
    player1_type = input().upper()
    print("Select Player 2 (H for human, A for AI): ")
    player2_type = input().upper()

    if player1_type=="H" and player2_type=="H":
        agent1 = 0
        agent2 = 1
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(2)

        if player1_type=="A" and player2_type=="A":
            print("Waiting for two agents to connect...")
            agent1, addr1 = server_socket.accept()
            print("Agent 1 connected from", addr1)
            bs = b'AG1 ' + Game.encode()
            agent1.sendall(bs)
            agent2, addr2 = server_socket.accept()
            print("Agent 2 connected from", addr2)
            bs = b'AG2 ' + Game.encode()
            agent2.sendall(bs)
        if player1_type=="A" and player2_type=="H":
            print("Waiting for one agent to connect...")
            agent1, addr1 = server_socket.accept()
            print("Agent 1 connected from", addr1)
            bs = b'AG1 ' + Game.encode()
            agent1.sendall(bs)
            agent2 = 0
        if player1_type=="H" and player2_type=="A":
            print("Waiting for one agent to connect...")
            agent1 = 0
            agent2, addr2 = server_socket.accept()
            print("Agent 2 connected from", addr2)
            bs = b'AG2 ' + Game.encode()
            agent2.sendall(bs)
            print("Agent 1 : ")

    print("------------------------")
    agents = [agent1, agent2]
    current_agent = 0

    jog = 0
    game = ServerGo(size, agent1, agent2)
    game.init_pygame()
    game.clear_screen()
    game.draw()
    while not game.check_end_game():
        if agents[current_agent]==0 or agents[current_agent]==1:
            game.update()
        if agents[current_agent]!=0 and agents[current_agent]!=1:
            board_byter = pickle.dumps(game.board)
            agents[current_agent].sendall(board_byter)
            try:
                data = agents[current_agent].recv(1024)
                move = pickle.loads(data)
                if not move:
                    break
                time.sleep(1)
                print("Agent", current_agent+1, ": ")
                print(f'Move: {move}')
                # Check if the move is valid
                if move is not None and is_valid_move(*move, game.board):
                    game.board[move[0], move[1]] = 1 if game.current_player == game.player1 else 2
                    game.black_turn = not game.black_turn  # Explicitly update the turn after the human move
                    game.current_player = game.player1 if game.black_turn else game.player2
                    game.handle_captures(move[0], move[1], "black" if game.current_player == game.player2 else "white")
                    game.CLICK.play()
                    game.draw()
                    game.print_scores()

                else:
                    game.pass_move()
                    print("AI couldn't find a valid move.")

                if agents[1-current_agent]==0 or agents[current_agent]==1:
                    print("Agent", 1-current_agent+1, ": ")


                # Switch to the other agent
                current_agent = 1 - current_agent
                jog += 1

            except Exception as e:
                print("Error:", e)
                break
        if game.human_has_played:
            current_agent = 1 - current_agent
            game.human_has_played = False


    print("\n-----------------\nGAME END\n-----------------\n")
    time.sleep(1)
    agent1.close()
    agent2.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
