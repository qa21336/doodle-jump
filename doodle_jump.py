import pygame
import random
from PIL import Image
from typing import Tuple, Union

pygame.init()
pygame.font.init()

display_width: int = 500
display_height: int = 700

with Image.open('sprite1.png') as image:
    player_width, player_height = image.size

#initial player coordinates
player1_x: float = display_width * 0.5 + 30
player2_x: float = display_width * 0.5 - 60

#initial block coordinates
n_blocks: int = int(display_height / 50 +1)
block_y0: list = [0] * n_blocks #list of initial y coordinates of the blocks
block_x: list = [0] * n_blocks
block_y: list = [0] * n_blocks #list of update y coordinates
for block in range(n_blocks):
    block_x[block] = random.randint(0,460)
    block_y0[block] = block_y0[block-1] + random.randint(50,120)
max_y: int = block_y0[-1] #the y coordinate of the highest block (used for seemless respawning of blocks)

def three_blocks(x_block,y_block0):
    #spawn first three blocks in the centre of the screen for a fair start
    filtered_lst = [x for x in y_block0 if x <= display_height]
    x_block[len(filtered_lst)-3:len(filtered_lst)] =  [display_width/2 - 20] *3
    return x_block

block_x = three_blocks(block_x,block_y0)

#initialise variables
player1_xchange: int = 0
player2_xchange: int = 0
start_tick: float = 0 #tick for bouncing icon on start screen
player1_tick: int = 0 #for player movements
player2_tick: int = 0
player_compensate: float = 0 #for when player collides with block
player_compensate2: float = 0
above_block1: list = [0] * n_blocks #is player above each block?
above_block2: list = [0] * n_blocks
game_speed: int = 0 # speed of game
background_y: float = 0 
tracking_height: float = 1/3 #the propotion from the top of the display the player can reach
background_speed: float = 0.5 #speed of the clouds
horizontal_player_speed: int = 0
player1_direction: int = 0 #which way is the sprite facing
player2_direction: int = 0

def player(x: float,y: float, direction: int, playerImg):
    #display players with correct orientation
    if direction ==0:
        gameDisplay.blit(playerImg,(x,y))  
    else:
        gameDisplay.blit(pygame.transform.flip( playerImg, True, False),(x,y)) 

def movement(player_y: float,block_y: float,player_x: float,block_x: float,player_tick: int,above_block: int,player_compensate: float) -> Tuple[int, int, float]:
    #this function handles to player collding with blocks
    if int(player_y) < int(block_y) - player_height:
        above_block =1
    if above_block == 1 and  int(player_y) > int(block_y) - player_height and int(block_x) -player_width < int(player_x) <int(block_x)  + 40:
        player_tick = 0
        player_compensate = block_y-display_height
        above_block = 0
    if int(player_y) > int(block_y) -player_height:
        above_block = 0
    return player_tick,above_block,player_compensate

def block_position(block_x, block_y0,player1_aboveBlock,player2_aboveBlock,block_y) -> Tuple[float, float, int, int]:
    #reset position of block when it disappears
    if block_y > display_height: 
        block_x = random.randint(0,460) #0 460
        #x_block = 200 #for testing
        block_y0+= -max_y +60 #-100
        player1_aboveBlock = 0
        player2_aboveBlock= 0
    return(block_x,block_y0,player1_aboveBlock,player2_aboveBlock)

def player_tracker(player1_tick, display_height, player_compensate, player1_y, player2_y, block_y0, player_compensate2, player2_tick, block_y,
                   tracking_height, background_y, background_speed) -> Tuple[float, float, float, float]:
    #track the player and adjust the view
    if (player1_tick -12) **2 + display_height - 12**2 - 20 + player_compensate < tracking_height*display_height and int(player1_y) < int(player2_y):
        block_y = [x - player1_y + tracking_height*display_height  for x in block_y0]
        player2_y = (player2_tick -12) **2 + display_height - 12**2 - 20  + player_compensate2 - player1_y + tracking_height*display_height
        background_y =  background_speed*(- player1_y + tracking_height*display_height)
        player1_y = tracking_height*display_height
    return(block_y, player1_y, player2_y, background_y)
    
def death_dection(player_y, block_y, display_height, background_y, player_tick, player_compensate, crashed) -> Tuple[int, float, str]:
    #detect death conditions
    if crashed == 'True':
        return(player_tick, player_compensate, crashed) 
    elif player_y > max(block_y)+200 or player_y > display_height: 
        if background_y == 0: #bounce if touch bottom
            player_tick = player_compensate = 0
        else:
            crashed = 'End' 
    return(player_tick, player_compensate, crashed) 

def draw_start_menu(start_tick) -> int:
    start_tick += 0.3
    jump_hieght = 8
    if start_tick > jump_hieght*2:
        start_tick = 0
    text_yChange = (start_tick -jump_hieght) **2 - jump_hieght**2
    title = font.render('Doodle Jump', True, (255, 0, 0))
    start_button = font.render('Press space to start', True, (255, 0, 0))
    gameDisplay.blit(title, (display_width/2 - title.get_width()/2, display_height/2 - title.get_height()/2 + text_yChange))
    gameDisplay.blit(start_button, (display_width/2 - start_button.get_width()/2, display_height/2 + start_button.get_height()/2+text_yChange))
    pygame.display.update()
    return start_tick

#setup display
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Doodle jump')
clock = pygame.time.Clock()
crashed = 'Start' #game state

#load sprite images
playerImg = pygame.image.load('sprite1.png').convert_alpha()
playerImg.set_colorkey((0, 0, 0)) #to remove background of png
playerImg2 = pygame.image.load('sprite2.png')
playerImg2.set_colorkey((0, 0, 0))
blockImg = pygame.image.load('block.jpg')
background = pygame.image.load('Background.jpg')

#setup font
font = pygame.font.Font("PressStart2P-vaV7.ttf", 24)

#game loop
while  crashed != 'True':
    keys = pygame.key.get_pressed()
    if crashed == 'Start':
        start_tick = draw_start_menu(start_tick)
        if keys[pygame.K_SPACE]:
           crashed = 'False'
           game_speed=0.3
           horizontal_player_speed = 6
    
    elif crashed == 'End': #display end screen with winner and score
        game_speed=0
        player1_xchange = player2_xchange = 0
        horizontal_player_speed = 0
        if player1_y > player2_y:
           winner_text = font.render('Left player wins', True, (255,0,0),)      
        elif player1_y < player2_y:
            winner_text = font.render('Right player wins', True, (255,0,0))
        else:
            winner_text = font.render('Draw', True, (255,0,0))
        score_text = font.render(f'Score: {int((background_y / background_speed + tracking_height*display_height)/100)}m', True, (255,0,0))
        options_text = font.render(f'Reset: R Quit: Q', True, (255,0,0))
        winner_rect = winner_text.get_rect(center=(display_width/2, display_height/2))
        score_rect = score_text.get_rect(center=(display_width/2, display_height/2))
        options_rect = options_text.get_rect(center=(display_width/2, display_height/2))
        gameDisplay.blit(winner_text, winner_rect)
        gameDisplay.blit(score_text, (score_rect.left, winner_rect.top+winner_rect.height))
        gameDisplay.blit(options_text, (options_rect.left, winner_rect.top+2*winner_rect.height))
        if keys[pygame.K_r]:
            player1_x = display_width * 0.5 + 30
            player2_x = display_width * 0.5 - 60
            above_block1 = [0] * n_blocks #is player above each block?
            above_block2 = [0] * n_blocks
            background_y = 0
            player1_tick = 0 #for player movements
            player2_tick = 0
            player_compensate = 0 #for when player collides with block
            player_compensate2 = 0
            for block in range(n_blocks):
                block_x[block] = random.randint(0,460)
                block_y0[block] = block_y0[block-1] + random.randint(50,120)
            max_y = block_y0[-1]
            block_x = three_blocks(block_x,block_y0)
            crashed = 'Start'

    pygame.display.flip() #update display

    #detect user inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = 'True'
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_LEFT:
               player1_xchange += - horizontal_player_speed
            if event.key == pygame.K_RIGHT:
               player1_xchange += horizontal_player_speed
            if event.key == pygame.K_a:
               player2_xchange += -horizontal_player_speed
            if event.key == pygame.K_d:
               player2_xchange += horizontal_player_speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
               player1_xchange += -horizontal_player_speed
            if event.key == pygame.K_LEFT:
                player1_xchange+= horizontal_player_speed
            if event.key == pygame.K_d:
               player2_xchange += -horizontal_player_speed
            if event.key == pygame.K_a:
                player2_xchange += horizontal_player_speed

    player1_x += player1_xchange
    player2_x += player2_xchange

    #projectilbe motion of player: 12^2 is jump height
    player1_y: float = (player1_tick -12) **2 + display_height - 12**2 - player_height + player_compensate
    player2_y: float = (player2_tick -12) **2 + display_height - 12**2 - player_height  + player_compensate2

    #handle player collision with blocks
    block_y = block_y0   
    for block in range(n_blocks): 
        #i dont think map can be used here since recursion is necessary
        player1_tick,above_block1[block],player_compensate = movement(
            player1_y,block_y[block],player1_x,block_x[block],player1_tick,above_block1[block],player_compensate) #detect collisions player 1
        player2_tick,above_block2[block],player_compensate2 = movement(
            player2_y,block_y[block],player2_x,block_x[block],player2_tick,above_block2[block],player_compensate2) #detect collisions player 2      
    
    #adjust view if necessary
    if player1_y < tracking_height* display_height  and int(player1_y) == int(player2_y):
        block_y = [x - player1_y + tracking_height*display_height for x in block_y0]
        background_y =  background_speed*(- player1_y + tracking_height*display_height)
        player1_y = player2_y =tracking_height*display_height        
    block_y, player1_y, player2_y, background_y = player_tracker(
        player1_tick, display_height, player_compensate, player1_y, player2_y, block_y0, player_compensate2, player2_tick, block_y, tracking_height, background_y, background_speed)
    block_y, player2_y, player1_y, background_y = player_tracker(
        player2_tick, display_height, player_compensate2, player2_y, player1_y, block_y0, player_compensate, player1_tick, block_y, tracking_height, background_y, background_speed)

    #reset block position and background if it falls out of the display
    block_x, block_y0 , above_block1, above_block2 = [list(row) for row in zip(*map(block_position, block_x, block_y0, above_block1, above_block2, block_y))]

    #death conditions if a player passed 2/3 of the screen, players can die
    player1_tick, player_compensate, crashed = death_dection(player1_y, block_y, display_height, background_y, player1_tick, player_compensate, crashed) #y_background=0 for testing
    player2_tick, player_compensate2, crashed = death_dection(player2_y, block_y, display_height, background_y, player2_tick, player_compensate2, crashed)

    #update ticks
    player1_tick += game_speed
    player2_tick += game_speed

    #render the game
    gameDisplay.blit(background,(0,background_y % 1000))
    gameDisplay.blit(background,(0,background_y % 1000-1000))
    for x,y in zip(block_x,block_y):
        gameDisplay.blit(blockImg, (x, y))
    player(player1_x,player1_y, player1_direction, playerImg)
    player(player2_x,player2_y, player2_direction, playerImg2)

    if keys[pygame.K_q]:
        crashed = 'True'

    clock.tick(60) #60 fps
pygame.quit()
 
#ideas: menu, spring/trampoline, different difficulties?, collect coins
#monsters, movine platforms, breakbale platforms?