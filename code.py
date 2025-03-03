import pygame
import random
from PIL import Image
from typing import Tuple

pygame.init()
pygame.font.init()

class DoodleJumpGame:
    def __init__(self):
        # Display dimensions
        self.display_width: int = 500
        self.display_height: int = 700

        # Load player sprite dimensions
        with Image.open('sprite1.png') as image:
            self.player_width, self.player_height = image.size
        
        # Initial player coordinates
        self.player1_x: float = self.display_width * 0.5 + 30
        self.player2_x: float = self.display_width * 0.5 - 60

        # Initialize block coordinates
        self.n_blocks: int = int(self.display_height / 50 + 1)
        self.block_y0: list = [0] * self.n_blocks
        self.block_x: list = [0] * self.n_blocks
        self.block_y: list = [0] * self.n_blocks

        # Randomise block coordinates
        for block in range(self.n_blocks):
            self.block_x[block] = random.randint(0, 460)
            self.block_y0[block] = (self.block_y0[block-1] +
                                     random.randint(50, 120))
        
        #To respawn blocks after disappearing from screen
        self.max_y = self.block_y0[-1]

        # Set first three block to the middle for a fair start
        self.three_blocks()

        # Initialize variables
        self.player1_xchange: int = 0 #control player's horizontal movement
        self.player2_xchange: int = 0
        self.start_tick: int = 0 #control bouncing text on start screen
        self.player1_tick: int = 0 #control bouncing player
        self.player2_tick: int = 0
        self.player_compensate: float = 0 #for when player collides with block
        self.player_compensate2: float = 0
        self.above_block1: list = [0] * self.n_blocks #is player above block?
        self.above_block2: list = [0] * self.n_blocks 
        self.game_speed: int = 0
        self.background_y: float = 0
        self.tracking_height: float = 1 / 3 #tracking threshold
        self.background_speed: float = 0.5
        self.horizontal_player_speed = 0
        self.player1_direction: int = 0
        self.player2_direction: int = 0

        # Setup display
        self.gameDisplay = pygame.display.set_mode(
            (self.display_width, self.display_height))
        pygame.display.set_caption('Doodle jump')
        self.clock = pygame.time.Clock()
        self.crashed = 'Start'

        # Load images
        self.playerImg = pygame.image.load('sprite1.png').convert_alpha()
        self.playerImg.set_colorkey((0, 0, 0))
        self.playerImg2 = pygame.image.load('sprite2.png')
        self.playerImg2.set_colorkey((0, 0, 0))
        self.blockImg = pygame.image.load('block.jpg')
        self.background = pygame.image.load('Background.jpg')

        # Setup font
        self.font = pygame.font.Font("PressStart2P-vaV7.ttf", 24)

    def three_blocks(self):
        # Spawn first three blocks in the center of the screen for a fair start
        filtered_lst = [x for x in self.block_y0 if x <= self.display_height]
        self.block_x[len(filtered_lst)-3:len(filtered_lst)] = (
            [self.display_width / 2 - 20] * 3)

    def display_player(self, x, y, direction, playerImg):
        # Display players with correct orientation
        if direction == 0:
            self.gameDisplay.blit(playerImg, (x, y))
        else:
            self.gameDisplay.blit(
                pygame.transform.flip(playerImg, True, False), (x, y))

    def player_collision(self, player_y, block_y, player_x, block_x, 
            player_tick, above_block, player_compensate) -> Tuple[int, int, 
                                                                  float]:
        # Handle player colliding with blocks
        if player_y < block_y - self.player_height:
            above_block = 1
        if above_block == 1 and player_y > block_y - self.player_height and (
            block_x - self.player_width < player_x < block_x + 40):
                player_tick = 0
                player_compensate = block_y - self.display_height
                above_block = 0
        if player_y > block_y - self.player_height:
            above_block = 0
        return player_tick, above_block, player_compensate

    def block_position(self, block_x, block_y0, player1_aboveBlock, 
                player2_aboveBlock, block_y) -> Tuple[float, float, int, int]:
        
        # Reset position of block when it disappears
        if block_y > self.display_height:
            block_x = random.randint(0, 460)
            #x_block = 200 #for testing
            block_y0 += -self.max_y + 60
            player1_aboveBlock = 0
            player2_aboveBlock = 0
        return block_x, block_y0, player1_aboveBlock, player2_aboveBlock


    def player_tracker(self, player1_tick, display_height, player_compensate, 
                player1_y, player2_y, block_y0, player_compensate2, 
                player2_tick, block_y, tracking_height, background_y, 
                background_speed) -> Tuple[float, float, float, float]:
        
        # Track the player and adjust the view
        if (player1_tick - 12) ** 2 + display_height - 12 ** 2 - 20 + (
            player_compensate) < tracking_height * self.display_height and (
            player1_y < player2_y):
            
            block_y = [
                x - player1_y + tracking_height * self.display_height 
                for x in block_y0]

            player2_y = (player2_tick - 12) ** 2 + display_height - 12 ** 2 + (
                - 20 + player_compensate2 - player1_y + tracking_height * (
                    self.display_height))
                                                                               
            background_y = background_speed * (
                -player1_y + tracking_height * self.display_height)
            player1_y = tracking_height * self.display_height
        return block_y, player1_y, player2_y, background_y

    def death_detection(self, player_y, block_y, display_height, 
                            background_y, player_tick, player_compensate,
                              crashed) -> Tuple[int, float, str]:
        # Detect death conditions
        if crashed == 'True':
            return player_tick, player_compensate, crashed
        elif player_y > max(block_y) + 200 or player_y > display_height:
            if background_y == 0:
                player_tick = player_compensate = 0
            else:
                crashed = 'End'
        return player_tick, player_compensate, crashed

    def draw_start_menu(self, start_tick) -> int:
        #for the bouncing text upon running 
        start_tick += 0.3
        jump_height = 8
        if start_tick > jump_height * 2:
            start_tick = 0
        text_yChange = (start_tick - jump_height) ** 2 - jump_height ** 2
        title = self.font.render('Doodle Jump', True, (255, 0, 0))
        start_button = self.font.render('Press space to start', True, 
                                        (255, 0, 0))
        self.gameDisplay.blit(title, 
            ((self.display_width - title.get_width()) / 2,
             (self.display_height - title.get_height()) / 2 + text_yChange))
        self.gameDisplay.blit(start_button, 
            ((self.display_width - start_button.get_width()) / 2,
             (self.display_height + start_button.get_height()) / 2 + (
                 text_yChange)))
        
        pygame.display.update()
        return start_tick

    def run(self):
        #game loop
        while self.crashed != 'True':
            keys = pygame.key.get_pressed()
            if self.crashed == 'Start':
                self.start_tick = self.draw_start_menu(self.start_tick)
                if keys[pygame.K_SPACE]:
                    self.crashed = 'False'
                    self.game_speed = 0.3
                    self.horizontal_player_speed = 6

            elif self.crashed == 'End': #display end screen: winner and score
                self.game_speed = 0
                self.player1_xchange = self.player2_xchange = 0
                self.horizontal_player_speed = 0
                if self.player1_y > self.player2_y:
                    winner_text = self.font.render('Left player wins', True, 
                                                   (255, 0, 0))
                elif self.player1_y < self.player2_y:
                    winner_text = self.font.render('Right player wins', True, 
                                                   (255, 0, 0))
                else:
                    winner_text = self.font.render('Draw', True, (255, 0, 0))

                score_value: int = int((self.background_y / 
                    self.background_speed + 
                    (self.tracking_height * self.display_height)) / 100)
                
                score_text = self.font.render(f'Score: {score_value}m', True, 
                                              (255, 0, 0))
                options_text = self.font.render(f'Reset: R Quit: Q', True, 
                                                (255, 0, 0))
                winner_rect = winner_text.get_rect(center=(
                    self.display_width / 2, self.display_height / 2))
                score_rect = score_text.get_rect(center=(
                    self.display_width / 2, self.display_height / 2))
                options_rect = options_text.get_rect(center=(
                    self.display_width / 2, self.display_height / 2))
                self.gameDisplay.blit(winner_text, winner_rect)
                self.gameDisplay.blit(score_text, (
                    score_rect.left, winner_rect.top + winner_rect.height))
                self.gameDisplay.blit(options_text, (
                    options_rect.left, 
                    winner_rect.top + 2 * winner_rect.height))
                if keys[pygame.K_r]:
                    self.__init__()
                    self.crashed = 'Start'

            pygame.display.flip() # update display

            #detect user input and convert to a value
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.crashed = 'True'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player1_xchange += -self.horizontal_player_speed
                        self.player1_direction = 0
                    if event.key == pygame.K_RIGHT:
                        self.player1_xchange += self.horizontal_player_speed
                        self.player1_direction = 1
                    if event.key == pygame.K_a:
                        self.player2_xchange += -self.horizontal_player_speed
                        self.player2_direction = 0
                    if event.key == pygame.K_d:
                        self.player2_xchange += self.horizontal_player_speed
                        self.player2_direction = 1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.player1_xchange += -self.horizontal_player_speed
                    if event.key == pygame.K_LEFT:
                        self.player1_xchange += self.horizontal_player_speed
                    if event.key == pygame.K_d:
                        self.player2_xchange += -self.horizontal_player_speed
                    if event.key == pygame.K_a:
                        self.player2_xchange += self.horizontal_player_speed

            self.player1_x += self.player1_xchange
            self.player2_x += self.player2_xchange

            #projectile motion of player where 12^2 is the height of the jump
            self.player1_y = (self.player1_tick - 12) ** 2 + (
                self.display_height - 12 ** 2 - self.player_height + (
                self.player_compensate))
            self.player2_y = (self.player2_tick - 12) ** 2 + (
                self.display_height - 12 ** 2 - self.player_height + (
                    self.player_compensate2))

            #handle player collision 
            # (i dont think a map can be used since recursion is necessary)
            block_y = self.block_y0
            for block in range(self.n_blocks):
                (self.player1_tick, self.above_block1[block], 
                    self.player_compensate) = self.player_collision(
                     self.player1_y, block_y[block], self.player1_x, 
                     self.block_x[block], self.player1_tick, 
                     self.above_block1[block], self.player_compensate)
                
                (self.player2_tick, self.above_block2[block], 
                    self.player_compensate2) = self.player_collision(
                    self.player2_y, block_y[block], self.player2_x, 
                    self.block_x[block], self.player2_tick, 
                    self.above_block2[block], self.player_compensate2)

            #adjust view if necessary 
            if (self.player1_y < self.tracking_height * self.display_height and
                int(self.player1_y) == int(self.player2_y)):

                block_y = [
                    x - self.player1_y + self.tracking_height 
                    * self.display_height for x in self.block_y0]

                self.background_y = self.background_speed * (
                    -self.player1_y + self.tracking_height * 
                    self.display_height)
                
                self.player1_y = self.player2_y = self.tracking_height * (
                    self.display_height)

            block_y, self.player1_y, self.player2_y, self.background_y = (
                self.player_tracker(self.player1_tick, self.display_height, 
                self.player_compensate, self.player1_y, self.player2_y, 
                self.block_y0, self.player_compensate2, self.player2_tick, 
                block_y, self.tracking_height, self.background_y, 
                self.background_speed))
            
            block_y, self.player2_y, self.player1_y, self.background_y = (
                self.player_tracker(self.player2_tick, self.display_height, 
                self.player_compensate2, self.player2_y, self.player1_y, 
                self.block_y0, self.player_compensate, self.player1_tick,
                  block_y, self.tracking_height, self.background_y, 
                  self.background_speed))


            #reset block position and background if it falls out of the display
            (self.block_x, self.block_y0, self.above_block1, self.above_block2
             )= [list(row) for row in zip(*map(self.block_position, 
                self.block_x, self.block_y0, self.above_block1, 
                self.above_block2, block_y))]

            #death conditions if a player passed 2/3 of the screen,
            self.player1_tick, self.player_compensate, self.crashed = (
                self.death_detection(self.player1_y, block_y, 
                self.display_height, self.background_y, self.player1_tick, 
                self.player_compensate, self.crashed))
            self.player2_tick, self.player_compensate2, self.crashed = (
                self.death_detection(self.player2_y, block_y, 
                self.display_height, self.background_y, self.player2_tick, 
                self.player_compensate2, self.crashed))

            # Update player ticks
            self.player1_tick += self.game_speed
            self.player2_tick += self.game_speed

            #Render game 
            self.gameDisplay.blit(self.background,
                                   (0, self.background_y % 1000))
            self.gameDisplay.blit(self.background, 
                                  (0, self.background_y % 1000 - 1000))
            for x, y in zip(self.block_x, block_y):
                self.gameDisplay.blit(self.blockImg, (x, y))
            self.display_player(self.player1_x, self.player1_y, 
                                self.player1_direction, self.playerImg)
            self.display_player(self.player2_x, self.player2_y, 
                                self.player2_direction, self.playerImg2)

            if keys[pygame.K_q]:
                self.crashed = 'True'

            self.clock.tick(60)  # 60 fps

        pygame.quit()

# To run the game
if __name__ == "__main__":
    game = DoodleJumpGame()
    game.run()

##ideas: menu, spring/trampoline, different difficulties?, collect coins
#monsters, movine platforms, breakbale platforms? combat?