import socket
import random
import time
import numpy as np
import pickle

#Para ja está random
def ai(received_all_pos):
    #Get all objects from the dictionary
    all_objects = [obj for objects_list in received_all_pos.values() for obj in objects_list]

    # Choose a random object
    selected_object = random.choice(all_objects)

    # Find the key associated with the selected object
    selected_key = next(key for key, objects_list in received_all_pos.items() if selected_object in objects_list)
    return selected_object, selected_key

def get_positions(board, player):
    pos = np.argwhere(board == player)
    return pos.tolist()

def get_all_possible_moves(positions, board):
    all_moves = {}

    for pos in positions:
        moves = possible_moves(pos, board)
        all_moves[tuple(pos)] = moves

    return all_moves

def possible_moves(move, board):
    NB = board.shape[0]
    possible_moves=[]
    for i in range(max(0,move[0]-2), min(NB, move[0]+3)):
        for j in range(max(0,move[1]-2), min(NB, move[1]+3)):

            if is_square_clear([i,j], board):
                possible_moves.append([i,j])

    return possible_moves

def is_square_clear(pos, board):
    if not np.array_equal(pos, []):
        return board[pos[0]][pos[1]] == 0

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
                received_data = client_socket.recv(4096)  # Adjust buffer size as needed
                # Deserialize the data back into a list
                board = pickle.loads(received_data)
                posicoes = get_positions(board, ag)
                all_pos = get_all_possible_moves(posicoes, board)
                print(f"Positions: {all_pos}")
                move, origin = ai(all_pos)

                print(f"Origin: {origin}")
                print(f"Move: {move}")

                # Serialize the selected key-value pair to bytes
                selected_data = pickle.dumps((origin, move))

                # Send the serialized data
                client_socket.sendall(selected_data)

            first = False

        client_socket.close()

    except BlockingIOError as e:
        print(f"Error: {e}")
        client_socket.close()

if __name__ == "__main__":
    connect_to_server()
