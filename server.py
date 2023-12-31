import socket
import threading
import os
import time
import pygame
from pong4 import *

# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 53531
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"

registered = {}
logged_in = []

players = []
queue = []

clients = []

max_players = 4 if gs.FourPlayers else 2
game_price = 60/100 # 60 seconds for 100 rupees


def assign_player():
    if is_players_full():
        return -1
    all_players = sorted([c["player"] for c in players])
    num = 1
    for player in all_players:
        if player != num:
            return num
        num += 1
    return num

def disconnect_client(client):
    global gs
    print(f"[DISCONNECT CLIENT] {client['addr']} disconnected.")

    client["connected"] = False

    clients.remove(client)
    print(f"[ACTIVE CLIENTS] {len(clients)}")

    if client in players:
        gs.paused = True
        gs.winner = -5
        players.remove(client)
    elif client in queue:
        queue.remove(client)
    try:
        logged_in.remove(client.mac)
        client["conn"].close()
    except:
        pass


def is_players_full():
    return len(players) >= max_players

def find_client(conn, addr):
    for client in clients:
        if client["addr"] == addr and client["conn"] == conn:
            return client
    return None


def start_next_game():
    global gs
    screen.fill(BLACK)
    screen.blit(
        font.render("Starting next game...", True, WHITE), 
        (gs.W//2-100,gs.H//2)
    )
    pygame.display.flip()

    # gs.paused = True
    time.sleep(0.1)

    gs.reset()
    gs.paused = True 

    while len(queue) > 0 and not is_players_full():
        c = queue.pop(0)
        c["player"] = assign_player()
        players.append(c)
        timer_thread = threading.Thread(target=player_timer, args=(c,))
        timer_thread.start()
        c["conn"].send(f'{c["player"]}'.encode(FORMAT))
    
    if is_players_full():
        gs.paused = False

def player_timer(client):
    global gs
    while client["connected"]:
        if gs.paused and client["time"] > 0:
            time.sleep(0.1)
            continue
        client["time"] -= 1
        if client["time"] < 0:
            gs.paused = True
            gs.winner = -client["player"]
            client["time"] = 0
        else:
            time.sleep(1)

def login_player(client):
    global gs
    logged_in.append(client)
    if is_players_full():
        client["player"] = -1
        queue.append(client)
    else:
        client["player"] = assign_player()
        players.append(client)
        timer_thread = threading.Thread(target=player_timer, args=(client,))
        timer_thread.start()
    client["conn"].send(f'{client["player"]}'.encode(FORMAT))
    time.sleep(0.1)
    if is_players_full():
        print("Starting game...")
        gs.paused = False

def handle_msg(msg, client):
    # print(f"[{client['addr']}] {msg}")
    if msg == "GET":
        global gs
        gs.set_ptime(client["player"], client["time"])
        client["conn"].send(gs.to_json().encode(FORMAT))
    elif "REGISTER" in msg:
        _, mac = msg.split("/")
        if mac in registered:
            client["conn"].send("MAC ALREADY REGISTERED".encode(FORMAT))
        else:
            registered[mac] = client
            client["mac"] = mac
            client["conn"].send("OK".encode(FORMAT))
    elif "LOGIN" in msg:
        _, mac = msg.split("/")
        if mac in logged_in:
            client["conn"].send("ALREADY LOGGED IN".encode(FORMAT))
        elif mac in registered:
            client["mac"] = mac
            client["time"] = registered[mac]["time"]
            if client["time"] <= 0:
                client["conn"].send("No time left, Please pay to continue".encode(FORMAT))
                return
            registered[mac] = client
            client["conn"].send("OK".encode(FORMAT))
            time.sleep(0.1)
            login_player(client)
        else:
            client["conn"].send("MAC NOT REGISTERED".encode(FORMAT))
    elif "PAY" in msg:
        _, mac, amount = msg.split("/")
        if mac in registered:
            registered[mac]["time"] += round(int(amount) * game_price, 2)
            client["conn"].send("OK".encode(FORMAT))
        else:
            client["conn"].send("MAC NOT REGISTERED".encode(FORMAT))
    elif "BALANCE" in msg:
        _, mac = msg.split("/")
        if mac in registered:
            client["conn"].send(f'OK/{registered[mac]["time"]}'.encode(FORMAT))
        else:
            client["conn"].send("MAC NOT REGISTERED".encode(FORMAT))
    else:
        event_type, event_key = msg.split(":")
        player_map = {
            1: {
                "up": pygame.K_w,
                "down": pygame.K_s
            },
            2: {
                "up": pygame.K_UP,
                "down": pygame.K_DOWN
            },
            3: {
                "left": pygame.K_a,
                "right": pygame.K_d
            },
            4: {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT
            }
        }
        key_map = {
            "KEYDOWN": pygame.KEYDOWN,
            "KEYUP": pygame.KEYUP
        }
        # pygame.event.post(pygame.event.Event( key_map[event_type], key = player_map[player_num][event_key]))
        handle_movement(key_map[event_type], player_map[client["player"]][event_key])



def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    client = find_client(conn, addr)
    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
            print(f"[DISCONNECT] {addr} disconnected.")
            disconnect_client(client)        
            break
        while ";" in msg:
            msg2, msg = msg.split(";",1)
            handle_msg(msg2, client)
    
    
            


    conn.close()



def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
    while True:
        conn, addr = server.accept()

        clients.append({"addr":addr,
                        "conn":conn,
                        "player": 0, 
                        "mac": None, 
                        "time": 0.0, 
                        "connected": True})
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

        # if not game_started:
        #     if ((len(clients)==4 and gs.FourPlayers) or (len(clients)==2 and not gs.FourPlayers)):
        #         game_started = True
        #         for client in clients:
        #             client["conn"].send("START".encode())

def start_server():
    server_thread = threading.Thread(target=main)
    server_thread.start()
    global gs, screen
    gs.paused = True

    while True:
        game_loop()
        start_next_game()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:   
        print("Closing server...")
        for client in clients:
            client["conn"].send(DISCONNECT_MESSAGE.encode(FORMAT))
            client["conn"].close()
        os._exit(0)