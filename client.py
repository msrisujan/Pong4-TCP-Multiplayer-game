import socket
import threading
import os
import re
from getmac import get_mac_address
import pygame
from pong4 import *
import tkinter as tk
from tkinter import messagebox

IP = socket.gethostbyname(socket.gethostname())
# IP = '192.168.117.23'
PORT = 53531
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT!"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
player = 0
player_pos = {
    1: "Left",
    2: "Right",
    3: "Top",
    4: "Bottom"
}

def game_entry():
    def register():
        # try:
        mac = get_mac_entry()
        # except ValueError as e:
        #     print(f"Registration Failed: {e}")
        #     messagebox.showerror("Registration Failed", e)
        #     return  
        client.send(f"REGISTER/{mac};".encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        if msg == "OK":
            print(f"Registered MAC Address: {mac}")
            messagebox.showinfo("Registration Successful", f"Registered MAC Address: {mac}")
        else:
            print(f"Registration Failed: {msg}")
            messagebox.showerror("Registration Failed", f"Registration Failed: {msg}")
    
    def login():
        try:
            mac = get_mac_entry()
        except ValueError as e:
            print(f"Login Failed: {e}")
            messagebox.showerror("Login Failed", e)
            return
        client.send(f"LOGIN/{mac};".encode(FORMAT))
        print(f"Sent LOGIN/{mac};")
        msg = client.recv(SIZE).decode(FORMAT)
        if msg == "OK":
            print(f"Logged in with MAC Address: {mac}")
            start_tk.destroy()
        else:
            print(f"Login Failed: {msg}")
            messagebox.showerror("Login Failed", f"Login Failed: {msg}")
    
    def pay():
        try:
            mac = get_mac_entry()
            amount = get_amount_entry()
        except ValueError as e:
            print(f"Payment Failed: {e}")
            messagebox.showerror("Payment Failed", e)
            return 
        client.send(f"PAY/{mac}/{amount};".encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        if msg == "OK":
            print(f"Paid {amount} for MAC Address: {mac}")
            messagebox.showinfo("Payment Successful", f"Paid {amount} for MAC Address: {mac}")
        else:
            print(f"Payment Failed: {msg}")
            messagebox.showerror("Payment Failed", f"Payment Failed: {msg}")
    
    def balance():
        try:
            mac = get_mac_entry()
        except ValueError as e:
            print(f"Balance Check Failed: {e}")
            messagebox.showerror("Balance Check Failed", e)
            return
        client.send(f"BALANCE/{mac};".encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        if "OK" in msg:
            _, time_left = msg.split("/")
            print(f"Time left for MAC Address: {mac} is {time_left} sec")
            messagebox.showinfo("Balance Check Successful", f"Time left for MAC Address: {mac} is {time_left} sec")
        else:
            print(f"Balance Check Failed: {msg}")
            messagebox.showerror("Balance Check Failed", f"Balance Check Failed: {msg}")

    def get_mac_entry():
        mac = mac_entry.get()
        # regex for mac
        mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if re.match(mac_regex, mac):
            return mac.replace("-", ":")
        else:
            raise ValueError(f"Invalid MAC Address: {mac}")
    
    def get_amount_entry():
        amount = amount_entry.get()
        # regex for amount
        amount_regex = r"^[1-9]\d*$"
        if re.match(amount_regex, amount):
            return amount
        else:
            raise ValueError(f"Invalid Amount: {amount}")

    def end_tk():
        start_tk.destroy()
        disconnect(client)
        

    start_tk = tk.Tk()
    start_tk.title("Game Registration/Login")

    # Create a label and entry widget for MAC Address
    mac_label = tk.Label(start_tk, text="MAC Address:")
    mac_label.grid(row=0, column=0)
    mac_entry = tk.Entry(start_tk)
    mac_entry.grid(row=0, column=1)

    mac_entry.insert(0, get_mac_address())
    # mac_entry.config(state="readonly")

    # Create a label and entry widget for payment amount
    amount_label = tk.Label(start_tk, text="Amount (100/min):")
    amount_label.grid(row=2, column=0)
    amount_entry = tk.Entry(start_tk)
    amount_entry.grid(row=2, column=1)

    amount_entry.insert(0, "100")

    # Create Pay button
    pay_button = tk.Button(start_tk, text="Pay", command=pay)
    balance_button = tk.Button(start_tk, text="Check Balance", command=balance)

    # Create Register and Login buttons
    register_button = tk.Button(start_tk, text="Register", command=register)
    login_button = tk.Button(start_tk, text="Login", command=login)

    register_button.grid(row=1, column=0, columnspan=2)
    balance_button.grid(row=3, column=0)
    pay_button.grid(row=3, column=1)
    login_button.grid(row=4, column=0, columnspan=2)

    start_tk.protocol("WM_DELETE_WINDOW", end_tk)

    start_tk.mainloop()

    

def disconnect(conn):
    conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
    print(f"[DISCONNECTED] Disconnected from {ADDR}")
    conn.close()

def update_game_state(conn):
    global player,player_pos, gs
    while True:
        conn.send("GET;".encode(FORMAT))
        msg = conn.recv(SIZE).decode(FORMAT)
        msg = msg.split("}")[0] + "}"
        gs.from_json(msg)


        if gs.paused and abs(gs.winner) != player:
            screen.blit(
                font.render("Waiting for game to start...", True, WHITE), 
                (gs.W//2-150,gs.H//2)
            )
            if gs.winner < 0:
                screen.blit(
                    font.render("Other player timeout", True, WHITE), 
                    (gs.W//2-110,gs.H//2-50)
                )
            pygame.display.flip()
            continue



        screen.fill(BLACK)

        tag_pos = 50 if gs.FourPlayers else 5
        screen.blit(
            font.render(f"{pl[player]} Player", True, WHITE), 
            (gs.W//2-65,tag_pos)
        )

        drawscore(screen, font, gs.H, gs.FourPlayers, gs)
        drawtimer(screen, font, gs.H, gs.FourPlayers, gs)
        drawball(screen, gs.bx, gs.by, gs.bw)

        drawpaddle(screen,
                   gs.p1x, gs.p1y, 
                   gs.paddle_width_v, gs.paddle_height_v, 
                   py1_Color
        ) 
        drawpaddle(screen,
                   gs.p2x, gs.p2y, 
                   gs.paddle_width_v, gs.paddle_height_v, 
                   py2_Color
        )

        if gs.FourPlayers:
            drawpaddle(screen,
                       gs.p3x, gs.p3y, 
                       gs.paddle_width_h, gs.paddle_height_h, 
                       py3_Color
            )
            drawpaddle(screen,
                       gs.p4x, gs.p4y, 
                       gs.paddle_width_h, gs.paddle_height_h, 
                       py4_Color
            )
        
        pygame.display.flip()

        if gs.winner != 0:
            screen.blit(
                font.render(f"{pl[gs.winner]} Player Wins!", True, WHITE), 
                (gs.W//2-100,gs.H//2)
            )
            winner_msg = ""
            winner_msg_offset = 0 
            if gs.winner == -5:
                winner_msg = "Players Disconnected"
                winner_msg_offset = 120
            elif gs.winner == -player:
                winner_msg = "Time Out"
                winner_msg_offset = 50
            elif gs.winner < 0:
                continue
            elif gs.winner == player:
                winner_msg = "You Win!"
                winner_msg_offset = 50
            else:
                winner_msg = "You Lose!"
                winner_msg_offset = 50
            screen.blit(
                font.render(winner_msg, True, WHITE), 
                (gs.W//2-winner_msg_offset,gs.H//2-50)
            )
            pygame.display.flip()
            break
    disconnect(conn)




def main():
    global player
    client.connect(ADDR)
    print(f"[CONNECTED] Connected to {ADDR}")
    game_entry()

    while True:
        msg = client.recv(SIZE).decode(FORMAT)
        player = int(msg)
        print(f"[PLAYER] Player {player}")

        screen.fill(BLACK)
        pygame.display.flip()
        if player == -1:
            print("[SERVER] Server full.")
            screen.blit(
                font.render("Server full.. Wait...", True, WHITE), 
                (gs.W//2-80,gs.H//2)
            )
            pygame.display.flip()
        else:
            break

    
    game_thread = threading.Thread(target=update_game_state, args=(client,))
    game_thread.start()
    
    connected = True
    while connected:
        key_map = {
            pygame.K_w: "up",
            pygame.K_s: "down",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_a: "left",
            pygame.K_d: "right",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right"
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                connected = False
                # pygame.quit()
                disconnect(client)
                break
            if event.type == pygame.KEYDOWN:
                if event.key in key_map:
                    msg = f"KEYDOWN:{key_map[event.key]};"
                    client.send(msg.encode(FORMAT))
            if event.type == pygame.KEYUP:
                if event.key in key_map:
                    msg = f"KEYUP:{key_map[event.key]};"
                    client.send(msg.encode(FORMAT))
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        disconnect(client)
    finally:
        pygame.quit()
        os._exit(0)