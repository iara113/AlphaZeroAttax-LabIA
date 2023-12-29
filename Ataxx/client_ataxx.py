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

def connect_to_server(host='localhost', port=8080):
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
                received_all_pos = pickle.loads(received_data)
                print(f"Posicoes: {received_all_pos}")

                move, origin = ai(received_all_pos)

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
