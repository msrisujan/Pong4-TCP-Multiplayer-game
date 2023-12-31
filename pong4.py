import pygame
import json
import os
from collections import defaultdict

class GameState(object):
    def __init__(self, **kwargs):
        self.H = 600
        self.W = self.H
        self.FourPlayers = False
        self.p1x = self.W/30
        self.p1y = self.H/2 - ((self.W/60)**2)/2
        self.p2x = self.W-(self.W/30)
        self.p2y = self.H/2 - ((self.W/60)**2)/2
        self.p3x = self.W/2 - ((self.H/60)**2)/2
        self.p3y = self.H/30
        self.p4x = self.W/2 - ((self.H/60)**2)/2
        self.p4y = self.H-(self.H/30)
        self.ball_thrower = 0
        self.p1score = 0
        self.p2score = 0
        self.p3score = 0
        self.p4score = 0
        self.p1time = 0.0
        self.p2time = 0.0
        self.p3time = 0.0
        self.p4time = 0.0
        self.paused = False
        self.winner = 0
        self.dmH = self.H/70
        self.dmW = self.W/70
        self.paddle_width_v = self.W/60
        self.paddle_width_h = self.H/60
        self.paddle_height_v = self.paddle_width_v**2
        self.paddle_height_h = self.paddle_width_h**2
        self.bx = self.W/2
        self.by = self.H/2
        self.bw = self.W/65
        self.velocity_raito = 240
        self.bxv = -self.H/self.velocity_raito
        self.byv = 0
        self.__dict__.update(kwargs)

    def reset(self):
        self.__init__()
    
    def set_ptime(self, player, time):
        match player:
            case 1:
                self.p1time = time
            case 2:
                self.p2time = time
            case 3:
                self.p3time = time
            case 4:
                self.p4time = time

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)

    def from_json(self, json_str):
        json_dict = json.loads(json_str)
        self.__init__(**json_dict)

gs = GameState()

### Colors
WHITE = (205, 214, 244)
RED = (243, 139, 168)
GREEN = (166, 227, 161)
BLUE = (137, 180, 250)
YELLOW = (249, 226, 175)
BLACK = (17, 17, 27)

#Colors of players
py1_Color = RED
py2_Color = GREEN
py3_Color = BLUE
py4_Color = YELLOW
pl = defaultdict(lambda: "NO", {1: "Left", 2: "Right", 3: "Top", 4: "Bottom"})

### Constants
screen = pygame.display.set_mode((gs.W, gs.H)) # Screen

winscore = 3

### PY GAME FONT
pygame.font.init()
font = pygame.font.SysFont('JetBrainsMono Nerd Font', 20)

### Variables
wt = 10 #thread update wait time 



# W-S Key Params
w_p = False
s_p = False
wsr = False
# Up-Down Key Params
up_p = False
down_p = False
udr = False

if gs.FourPlayers:
    # A-D Key Params
    a_p = False
    d_p = False
    adr = False
    # Left-Right Key Params
    left_p = False
    right_p = False
    lrr = False

### Functions
def drawpaddle(screen, x, y, w, h, color=WHITE):
    pygame.draw.rect(screen, color, (x, y, w, h))

def drawball(screen, x, y, bw):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(bw))


def uploc(): 
    ''' 
    Updates Player Locations
    ''' 
    global gs

    if w_p:
        if gs.p1y-gs.dmH < 0:
            gs.py1 = 0
        else:
            gs.p1y -= gs.dmH
    elif s_p:
        if gs.p1y+gs.dmH+gs.paddle_height_v > gs.H:
            gs.p1y = gs.H-gs.paddle_height_v
        else:
            gs.p1y += gs.dmH

    if up_p:
        if gs.p2y-gs.dmH < 0:
            gs.p2y = 0
        else:
            gs.p2y -= gs.dmH
    elif down_p:
        if gs.p2y+gs.dmH+gs.paddle_height_v > gs.H:
            gs.p2y = gs.H-gs.paddle_height_v
        else:
            gs.p2y += gs.dmH

    if gs.FourPlayers:
        if a_p:
            if gs.p3x-gs.dmW<0:
                gs.p3x = 0
            else:
                gs.p3x -=gs.dmW
        elif d_p:
            if gs.p3x+gs.dmW+gs.paddle_width_h>gs.W:
                gs.p3x = gs.W-gs.paddle_width_h
            else:
                gs.p3x += gs.dmW

        if left_p:
            if gs.p4x-gs.dmW<0:
                gs.p4x = 0
            else:
                gs.p4x -=gs.dmW
        elif right_p:
            if gs.p4x+gs.dmW+gs.paddle_width_h>gs.W:
                gs.p4x = gs.W-gs.paddle_width_h
            else:
                gs.p4x += gs.dmW


def upscr():
    '''
    Updates Score according to the last ball thrower
    '''
    global gs
    if gs.ball_thrower == 1:
        gs.p1score += 1
    elif gs.ball_thrower == 2:
        gs.p2score += 1
    elif gs.FourPlayers:
        if gs.ball_thrower == 3:
            gs.p3score += 1
        elif gs.ball_thrower == 4:
            gs.p4score += 1

    gs.ball_thrower = 0 #Set Ball thrower 0 to be fair, when the corresponding player throws then begin to score it.
 

def upblnv():
    ''' 
    Updates Ball
    ''' 
    global gs
    
    if (gs.bx+gs.bxv < gs.p1x+gs.paddle_width_v) and ((gs.p1y < gs.by+gs.byv+gs.bw) and (gs.by+gs.byv-gs.bw < gs.p1y+gs.paddle_height_v)):
        gs.bxv = -gs.bxv
        gs.byv = ((gs.p1y+(gs.p1y+gs.paddle_height_v))/2)-gs.by
        gs.byv = -gs.byv/((5*gs.bw)/7)
        gs.ball_thrower = 1
    elif gs.bx+gs.bxv < 0:
        upscr()
        gs.bx = gs.W/2
        gs.bxv = gs.H/gs.velocity_raito
        gs.by = gs.H/2
        gs.byv = 0

    if (gs.bx+gs.bxv > gs.p2x) and ((gs.p2y < gs.by+gs.byv+gs.bw) and (gs.by+gs.byv-gs.bw < gs.p2y+gs.paddle_height_v)):
        gs.bxv = -gs.bxv
        gs.byv = ((gs.p2y+(gs.p2y+gs.paddle_height_v))/2)-gs.by
        gs.byv = -gs.byv/((5*gs.bw)/7)
        gs.ball_thrower = 2
    elif gs.bx+gs.bxv > gs.W:
        upscr()
        gs.bx = gs.W/2
        gs.bxv = -gs.H/gs.velocity_raito
        gs.by = gs.H/2
        gs.byv = 0

    
    if gs.FourPlayers:##4 Player Mode        
        if (gs.by+gs.byv < gs.p3y+gs.paddle_height_h) and ((gs.p3x < gs.bx+gs.bxv+gs.bw) and (gs.bx+gs.bxv-gs.bw < gs.p3x+gs.paddle_width_h)):
            gs.byv = -gs.byv
            gs.bxv = ((gs.p3x+(gs.p3x+gs.paddle_width_h))/2)-gs.bx
            gs.bxv = -gs.bxv/((5*gs.bw)/7)
            gs.ball_thrower = 3
        elif gs.by+gs.byv < 0:
            upscr()
            gs.by = gs.H/2
            gs.byv = gs.W/gs.velocity_raito
            gs.bx = gs.W/2
            gs.bxv = 0

        if (gs.by+gs.byv > gs.p4y) and ((gs.p4x < gs.bx+gs.bxv+gs.bw) and (gs.bx+gs.bxv-gs.bw < gs.p4x+gs.paddle_width_h)):
            gs.byv = -gs.byv
            gs.bxv = ((gs.p4x+(gs.p4x+gs.paddle_width_h))/2)-gs.bx
            gs.bxv = -gs.bxv/((5*gs.bw)/7)
            gs.ball_thrower = 4
        elif gs.by+gs.byv > gs.H:
            upscr()
            gs.by = gs.H/2
            gs.byv = -gs.W/gs.velocity_raito
            gs.bx = gs.W/2
            gs.bxv = 0
    else:##2 Player Mode    
        if gs.by+gs.byv > gs.H or gs.by+gs.byv < 0:
            gs.byv = -gs.byv
        
    gs.bx += gs.bxv
    gs.by += gs.byv

def drawscore(screen, font, H, FourPlayers, gs):
    screen.blit(font.render("Score", True, WHITE), (30,30))
    
    screen.blit(font.render(f"{gs.p1score}",True,py1_Color),(H/5,30))
    screen.blit(font.render(f"{gs.p2score}",True,py2_Color),(2*H/5,30))
    
    if FourPlayers:
        screen.blit(font.render(f"{gs.p3score}",True,py3_Color),(3*H/5,30))
        screen.blit(font.render(f"{gs.p4score}",True,py4_Color),(4*H/5,30))

def drawtimer(screen, font, H, FourPlayers, gs):
    screen.blit(font.render("Timer", True, WHITE), (30,50))
    
    screen.blit(font.render(f"{gs.p1time}",True,py1_Color),(H/5,50))
    screen.blit(font.render(f"{gs.p2time}",True,py2_Color),(2*H/5,50))
    
    if FourPlayers:
        screen.blit(font.render(f"{gs.p3time}",True,py3_Color),(3*H/5,50))
        screen.blit(font.render(f"{gs.p4time}",True,py4_Color),(4*H/5,50))

def winner():
    '''
    Returns the winner of the game
    '''
    global gs
    if gs.p1score == winscore:
        return 1
    elif gs.p2score == winscore:
        return 2
    elif gs.FourPlayers:
        if gs.p3score == winscore:
            return 3
        elif gs.p4score == winscore:
            return 4
    return 0

def handle_movement(type,key):
    global w_p, s_p, wsr, up_p, down_p, udr, a_p, d_p, adr, left_p, right_p, lrr
    
    if type == pygame.KEYDOWN:
        if key == pygame.K_w:
            w_p = True
            if s_p == True:
                s_p = False
                wsr = True
        if key == pygame.K_s:
            s_p = True
            if w_p == True:
                w_p = False
                wsr = True
        if key == pygame.K_UP:
            up_p = True
            if down_p == True:
                down_p = False
                udr = True
        if key == pygame.K_DOWN:
            down_p = True
            if up_p == True:
                up_p = False
                udr = True

        if gs.FourPlayers:
            if key == pygame.K_a:
                a_p = True
                if d_p == True:
                    a_p = False
                    adr = True
            if key == pygame.K_d:
                d_p = True
                if a_p == True:
                    d_p = False
                    adr = True
            if key == pygame.K_LEFT:
                left_p = True
                if right_p == True:
                    left_p = False
                    lrr = True
            if key == pygame.K_RIGHT:
                right_p = True
                if left_p == True:
                    right_p = False
                    lrr = True

        # uploc()
        # upblnv()

    if type == pygame.KEYUP:
        if key == pygame.K_w:
            w_p = False
            if wsr == True:
                s_p = True
                wsr = False
        if key == pygame.K_s:
            s_p = False
            if wsr == True:
                w_p = True
                wsr = False
        if key == pygame.K_UP:
            up_p = False
            if udr == True:
                down_p = True
                udr = False
        if key == pygame.K_DOWN:
            down_p = False
            if udr == True:
                up_p = True
                udr = False

        if gs.FourPlayers:
            if key == pygame.K_a:
                a_p = False
                if adr == True:
                    d_p = True
                    adr = False
            if key == pygame.K_d:
                d_p = False
                if adr == True:
                    a_p = True
                    adr = False
            if key == pygame.K_LEFT:
                left_p = False
                if lrr == True:
                    right_p = True
                    lrr = False
            if key == pygame.K_RIGHT:
                right_p = False
                if lrr == True:
                    left_p = True
                    lrr = False



def game_loop():
    global w_p, s_p, wsr, up_p, down_p, udr, a_p, d_p, adr, left_p, right_p, lrr
    global gs

    playerCount = 2
    if gs.FourPlayers:
        playerCount = 4   
    pygame.display.set_caption(f'Pong for {playerCount} Players')

    screen.fill(BLACK)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gs.winner = -5
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gs.winner = -5
                    running = False
        
        if gs.paused and gs.winner == 0:
            screen.blit(
                font.render("Waiting for game to start...", True, WHITE), 
                (gs.W//2-150,gs.H//2)
            )
            pygame.display.flip()
            prev_paused = True
            continue

        screen.fill(BLACK)
        uploc()
        upblnv()
        drawscore(screen, font, gs.H, gs.FourPlayers, gs)
        drawtimer(screen, font, gs.H, gs.FourPlayers, gs)

        tag_pos = 50 if gs.FourPlayers else 5
        screen.blit(font.render(f"SERVER", True, WHITE), (gs.W//2-35,tag_pos))
        drawball(screen, gs.bx, gs.by, gs.bw)

        drawpaddle(screen, gs.p1x, gs.p1y, gs.paddle_width_v, gs.paddle_height_v, py1_Color) 
        drawpaddle(screen, gs.p2x, gs.p2y, gs.paddle_width_v, gs.paddle_height_v, py2_Color)

        if gs.FourPlayers:
            drawpaddle(screen, gs.p3x, gs.p3y, gs.paddle_width_h, gs.paddle_height_h, py3_Color)
            drawpaddle(screen, gs.p4x, gs.p4y, gs.paddle_width_h, gs.paddle_height_h, py4_Color)

        pygame.display.flip()
        pygame.time.wait(wt)
        # print("gameloop p1score: ", gs.p1score)
        if gs.winner >= 0:
            gs.winner = winner()
        if gs.winner != 0:
            running = False

        
    
    screen.blit(font.render(f"Winner is {pl[gs.winner]} Player", True, WHITE), (gs.W//2-150,gs.H//2))
    pygame.display.flip()

    # while True:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             os._exit(0 )
    #     pygame.time.wait(wt)


### Initialize
if __name__ == "__main__":
    game_loop()