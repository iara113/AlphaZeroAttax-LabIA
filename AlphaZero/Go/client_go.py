import socket
import random
import time
import numpy as np
import pickle
import networkx as nx
import pygame
import itertools
import sys
import collections
from pygame import gfxdraw
import copy

#random
class AI:
    def __init__(self, color):
        self.color = color

    def make_move(self, board, n):
        valid_moves = [(col, row) for col in range(board.shape[0]) for row in range(board.shape[1]) if board[col, row] == 0]

        valid_moves_without_autocapture = [move for move in valid_moves if not autocapture(board, self.color, *move, n)]

        valid_moves_without_invalid = [move for move in valid_moves_without_autocapture if is_valid_move(*move, board)]
        if not valid_moves_without_invalid:
            return None  # No valid moves available

        return valid_moves_without_invalid[np.random.choice(len(valid_moves_without_invalid))]

def has_no_liberties(board, group):
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
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False
    return board[col, row] == 0

def autocapture(b, color, col, row, n):
    board = b.copy()
    board[col, row] = n
    group = None
    for group in get_stone_groups(board, color):
        if (col, row) in group:
            break
    if group==None:
        return False
    if has_no_liberties(board, group):
        return True

    return False

def connect_to_server(host='localhost', port=5000):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        response = client_socket.recv(1024).decode()
        print(f"Server Response INIT: {response}")

        Game = response[-5:]
        print("Playing:", Game)

        if "1" in response:
            ag = 1
        else:
            ag = 2

        first = True

        while True:
            if ag == 1 or not first:
                # Receive the serialized board data
                board_data = client_socket.recv(4096)
                # Deserialize the data using pickle
                board = pickle.loads(board_data)

                if ag==1:
                    player = AI(color="black")
                if ag==2:
                    player = AI(color="white")
                move = player.make_move(board, ag)
                print(f"Move: {move}")
                # Serialize the move using pickle
                move_data = pickle.dumps(move)
                # Send the serialized move data
                client_socket.sendall(move_data)

            first = False

        client_socket.close()

    except BlockingIOError as e:
        print(f"Error: {e}")
        client_socket.close()

if __name__ == "__main__":
    connect_to_server()
