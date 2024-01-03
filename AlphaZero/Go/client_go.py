import socket
import random
import time
import numpy as np
import pickle

#Para ja está random
def ai(board):
    valid_moves = [(col, row) for col in range(board.shape[0]) for row in range(board.shape[1]) if board[col, row] == 0]
    if not valid_moves:
        return None  # No valid moves available

    return valid_moves[np.random.choice(len(valid_moves))]

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

                move = ai(board)
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
