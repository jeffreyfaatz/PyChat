import socket
import threading

clients = []
names = []

def client_thread(client_socket):
    flag = True
    while True:
        try:
            message = client_socket.recv(1024).decode('utf8')
            if flag:
                names.append(message)
                print(message, 'connected')
                client_socket.send(("Other users:" + ','.join(names)).encode('utf8'))
                flag = False
            for c in clients:
                if c != client_socket:
                    index = clients.index(client_socket)
                    name = names[index]
                    if name == message:
                        c.send(("new_client-"+name).encode('utf8'))
                    else:
                        c.send((name + '--' + message).encode('utf8'))
        except:
            index = clients.index(client_socket)
            clients.remove(client_socket)
            name = names[index]
            names.remove(name)
            for c in clients:
                c.send(("exit_client-" + name).encode('utf8'))
            print(name + ' exit')
            break

def run_server():
    
    # TCP connection info
    HOST = '127.0.0.1' # '127.0.0.1' is localhost - change to private IP for internet usage
    PORT = 5005
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT)) # bind socket to host and port
        server.listen() # listen for client connections
        print(f"Server is listening on {HOST}:{PORT}")

        while True:
            client, address = server.accept()
            clients.append(client)
            print('Server connected..', address[0] + ':' + str(address[1]))
            thread = threading.Thread(target=client_thread, args=(client,))
            thread.start()

    except Exception as e:
        print(f"Error:{e}")
    finally:
        server.close()

run_server()