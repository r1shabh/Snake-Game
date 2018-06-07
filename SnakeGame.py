'''
Created on Mar 15, 2014

@author: rishabh anand
'''
import pygame
import os,time,sys
from random import randint
from pygame.locals import *

#define basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DIRECTIONS = ["Right", "Left", "Up", "Down"]
CellWidth = 20
WindowSize = 600
RefreshRateFPS = 15
hungry_splash_img = "hungry_snake.jpg"

dirty_rectangles = []

class Snake:
    global dirty_rectangles
    movement = {'Right':[1, 0], 'Down':[0, 1], 'Left':[-1, 0], 'Up':[0, -1]}
    num_of_cells = WindowSize / CellWidth
    score = 0
    
    """sets the initial location of fruits and snake and sets the sound effect when food is picked up"""
    def __init__(self, position, display_surface): # position is the beginning position
        self.pieces = []
        self.fruits = []
        self.pieces_on_window = []
        self.prize = 10 # prize of eating the fruit
        self.pieces.append(position)
        self.fruit_locations = []
        self.initialize_fruits()
        self.display_snake_and_fruits(display_surface)
        self.pickUpSound = pygame.mixer.Sound('pickup.wav')
    
    '''
    initializes the three fruits. a fruit data structure contains
    the fruit location, point value, and color
    '''
    def initialize_fruits(self):
        location = self.get_safe_fruit_location()
        self.fruits.append((location, 10, GREEN))
        location = self.get_safe_fruit_location()
        self.fruits.append((location, 0, WHITE))
        location = self.get_safe_fruit_location()
        self.fruits.append((location, -10, RED))

    '''
    checks to see if snake has reached a fruit,
    and if so, returns the fruit that it has reached
    '''        
    def can_it_eat_fruit(self):
        next2food = False
        head = self.pieces[0]
        for fruit in self.fruits:
            if fruit[0] == head:
                next2food = True
                break
        return next2food, fruit
    
    '''
    grows the snake by one square when it has eaten the right fruit
    '''
    def grow_snake(self, direction):
        self.add_head(direction)
    
    '''
    mechanism used in both growing an moving the snake. works by
    adding a piece to the front of the snake, or the beginning
    of the self.pieces list
    '''
    def add_head(self, direction):
        head = self.pieces[0]
        nx = head[0] + self.movement[direction][0]
        ny = head[1] + self.movement[direction][1]
        self.pieces.insert(0, (nx, ny))
        rect = pygame.Rect(nx * CellWidth, ny * CellWidth, CellWidth, CellWidth)
        dirty_rectangles.append(rect)

    '''
    other mechanism used for moving the snake. removes piece from the end of
    self.pieces
    '''    
    def remove_tail(self):
        (x, y) = self.pieces.pop()
        rect = pygame.Rect(x * CellWidth, y * CellWidth, CellWidth, CellWidth)
        dirty_rectangles.append(rect)
    
    '''
    figures out the new location for snake's head based on previous location
    for its head and what direction it's going
    '''
    def get_new_location(self, direction):
        head = self.pieces[0]
        nx = head[0] + self.movement[direction][0]
        ny = head[1] + self.movement[direction][1]
        return (nx, ny)
    
    '''
    moves the snake. mechanism derives from the idea that when a snake moves one
    space, it occupies almost all the same squares it did previously. The only ones
    that change are the head and tail.
    '''
    def moveSnake(self, direction):
        self.add_head(direction)
        self.remove_tail()
    
    '''
    the game ends if one of two things happens. Either the snake runs into a wall, or
    itself. this method checks both those conditions
    '''
    def is_it_dead(self, location):
        (x, y) = location
        ateitself = False
        hitwall =  x == -1 or y == -1 or x > self.num_of_cells or y > self.num_of_cells
        if len(self.pieces) >= 3:
            ateitself = location in self.pieces[3:] 
        return hitwall or ateitself
    
    '''
    replaces a fruit that has been eaten. 
    '''
    def replace_fruit(self, fruit):
        new_location = self.get_safe_fruit_location()
        (location, score, color) = fruit
        self.fruits.remove(fruit)
        self.fruits.append((new_location, score, color))
        rect1 = pygame.Rect(location[0] * CellWidth, location[1] * CellWidth, CellWidth, CellWidth)
        rect2 = pygame.Rect(new_location[0] * CellWidth, new_location[1] * CellWidth, CellWidth, CellWidth)
        dirty_rectangles.append(rect1)
        dirty_rectangles.append(rect2)
    
    '''
    method to draw the snake and three fruits
    '''
    def display_snake_and_fruits(self, display_surface):
        display_surface.fill(BLACK)
        for piece in self.pieces:
            wx = piece[0] * CellWidth
            wy = piece[1] * CellWidth
            rect = pygame.Rect(wx, wy, CellWidth, CellWidth)
            pygame.draw.rect(display_surface, BLUE, rect)
        for fruit in self.fruits:
            self.display_fruit(display_surface, fruit)
        self.display_score(display_surface)

    '''
    called in display_snake_and_fruits method. used for drawing
    the fruits
    '''
    def display_fruit(self, display_surface, fruit):
        ((x, y), score, color) = fruit 
        (wx, wy) = (x * CellWidth, y * CellWidth)
        rect = pygame.Rect(wx, wy, CellWidth, CellWidth)
        pygame.draw.rect(display_surface, color, rect)

    '''
    method to show the player's score on the top right
    corner of the screen
    '''
    def display_score(self, display_surface):
        color = GREEN if self.score > 0 else RED   
        font = pygame.font.Font('freesansbold.ttf', 15)
        msg = 'Score: %s' % (self.score)
        surface = font.render(msg, True, color)
        rect = surface.get_rect()
        rect.topleft = (WindowSize - 120, 10)
        dirty_rectangles.append(rect)
        display_surface.blit(surface, rect)

    '''
    method for updating the frame. First, it moves the snake,
    then checks if snake has eaten a fruit and updates score accordingly.
    '''       
    def play_next(self, display_surface, direction):
        location = self.get_new_location(direction)
        it_is_dead = self.is_it_dead(location)
        if it_is_dead == False:
            (eat_fruit, fruit) = self.can_it_eat_fruit()
            if eat_fruit == True:
                self.pickUpSound.play()
                old_score = self.score
                self.score += fruit[1]
                if self.score >= old_score:
                    self.grow_snake(direction)
                self.replace_fruit(fruit)
            self.moveSnake(direction)
            self.display_snake_and_fruits(display_surface)
        return it_is_dead
    
    '''
    after a fruit has been eaten, this method is called to figure out a new location.
    it works by getting a random x, y coordinate and checks to make sure that coordinate
    does not already have another fruit or snake piece on it. 
    '''
    def get_safe_fruit_location(self):
        found = False
        while not found:
            nx = randint(0, self.num_of_cells-1)
            ny = randint(0, self.num_of_cells-1)
            for piece in self.pieces:
                if (nx, ny) == piece:
                    collision = True
            for fruit in self.fruits:
                (loc, score, color) = fruit
                if (nx, ny) == loc:
                    collision = True
            collision = False
            found = not collision
        return (nx, ny)
      
        
    
class HungryGame:
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.font.init()
        self.show_splash_screen()
        print "returned"
        self.DisplaySurface = pygame.display.set_mode((WindowSize, WindowSize))
        pygame.mouse.set_visible(False)            #the game will not need the mouse
        pygame.display.set_caption("Hungry Snake", "Hungry Snake")
        self.RefreshClock = pygame.time.Clock()    #get the clock to set frame per second
        pygame.display.update()
        elapsed_ms = self.RefreshClock.tick(RefreshRateFPS)
        print elapsed_ms
        pygame.mixer.music.load('background.mid')
        self.gameOver = pygame.mixer.Sound('gameover.wav')
        self.show_rules()

    '''
    figures out the direction of the snake based on what arrow or wasd key
    the player pressed
    '''  
    def process_event_for_direction(self, event):
        if event.type == KEYDOWN:
            if (event.key == K_LEFT or event.key == K_a) and self.Direction != "Right":
                self.Direction = "Left"
            elif (event.key == K_RIGHT or event.key == K_d) and self.Direction != "Left":
                self.Direction = "Right"
            elif (event.key == K_UP or event.key == K_w) and self.Direction != "Down":
                self.Direction = "Up"
            elif (event.key == K_DOWN or event.key == K_s) and self.Direction != "Up":
                self.Direction = "Down"
        return 
    
    '''
    the driver program that gets the ball rolling
    the event loop terminates when user closes the window
    or the game is over because of snake's death
    player can again start the game by pressing a key 
    '''
    def play(self):
        global dirty_rectangles
        pygame.mixer.music.play(-1, 0.0)
        self.Direction = DIRECTIONS[randint(0, 3)] #choose a random direction to start
        initial_position = ((WindowSize/2)//CellWidth, (WindowSize/2)//CellWidth)
        self.snake = Snake(initial_position, self.DisplaySurface)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate_game()
                    
                self.process_event_for_direction(event)
            snake_dead = self.snake.play_next(self.DisplaySurface, self.Direction)
            if (snake_dead == True):
                return
            else:
                self.redisplay_board()
                #pygame.display.update()
                
                if dirty_rectangles == []:
                    pygame.display.update()
                else:
                    pygame.display.update(dirty_rectangles)
                    dirty_rectangles = []
                
                elapsed_ms = self.RefreshClock.tick(RefreshRateFPS) #elapsed_ms/1000 = how many seconds elapsed
                print "Update time: ", elapsed_ms
    
    '''                
    initial splash screen
    vanishes in 3 seconds
    '''   
    def show_splash_screen(self):
        SplashSize = 500
        screen = pygame.display.set_mode((SplashSize,SplashSize), pygame.NOFRAME) 
        print 'splash...'     
        img = pygame.image.load("rishabh_snake.jpg")
        screen.blit(img, (0,0)) 
        pygame.display.flip()
        time.sleep(3)
        print "done with splash"
        return screen

    '''
    display the rules of the game
    player can press any key to play the game
    '''
    def show_rules(self):
        font = pygame.font.Font("VAG-HandWritten.otf", 20)
        
        surf = font.render('1. Press arrow keys or WASD keys to change direction', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/10, WindowSize/5)
        self.DisplaySurface.blit(surf, rect)
        
        surf = font.render('2. Green fruit increases score by 10 points.', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/10, WindowSize/5 + 45)
        self.DisplaySurface.blit(surf, rect)
        
        surf = font.render('3. Red fruit decreases score by 10 points.', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/10, WindowSize/5 + 90)
        self.DisplaySurface.blit(surf, rect)
        
        surf = font.render('4. White fruit grows the snake and leaves the score unchanged.', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/10, WindowSize/5 + 135)
        self.DisplaySurface.blit(surf, rect)
        
        surf = font.render('5. Snake dies by running into itself or off the screen', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/10, WindowSize/5 + 170)
        self.DisplaySurface.blit(surf, rect)
        
        font = pygame.font.Font("freesansbold.ttf", 15)
        surf = font.render('Press a key to play. Or escape to quit', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/2, WindowSize - 30)
        self.DisplaySurface.blit(surf, rect)
        
        pygame.display.flip()
        
        self.check_key_pressed_event()
        
        while True:
            if self.check_key_pressed_event():
                pygame.event.get()
                return True

    '''
    allows the game to update based on user key presses
    '''
    def redisplay_board(self):
        return True
        
    
    #the snake died
    #display game over screen and ask if player
    #wants to continue    
    """displays the game over screen"""
    def show_game_over(self):
        self.DisplaySurface.fill(BLACK)
        msg = 'Final Score'
        font = pygame.font.Font("SF_Wonder_Comic_Bold.ttf", 75)
        surface = font.render(msg, True, WHITE)
        rect = surface.get_rect()
        rect.midtop = (WindowSize/2, 100)
        self.DisplaySurface.blit(surface, rect)
        
        msg = str((self.snake.score))
        surface = font.render(msg, True, WHITE)
        rect = surface.get_rect()
        rect.midtop = (WindowSize/2, 200)
        self.DisplaySurface.blit(surface, rect)
        
        surface = font.render("Play Again?", True, WHITE)
        rect = surface.get_rect()
        rect.midtop = (WindowSize/2, WindowSize/2 + 50)
        self.DisplaySurface.blit(surface, rect)
        
        font = pygame.font.Font("freesansbold.ttf", 15)
        surf = font.render('Press a key to play. Or escape to quit', True, WHITE)
        rect = surf.get_rect()
        rect.topleft = (WindowSize/2, WindowSize - 30)
        self.DisplaySurface.blit(surf, rect)
        
        pygame.display.update()
        
        self.check_key_pressed_event()
        
        while True:
            if self.check_key_pressed_event():
                pygame.event.get()
                return True
     
    #check if user had already pressed the close button of window
    #one or more times. If so, then close the game.
    #Otherwise check if any top-row keys were pressed and if ESC was one
    #of them. ESC key will exit the game as well.
    #clear the key-press event queue 
    '''method that checks what key user presses'''
    def check_key_pressed_event(self): 
        if len(pygame.event.get(QUIT)) > 0:
            self.terminate_game()

        key_up_events = pygame.event.get(KEYUP)
        if len(key_up_events) == 0:
            return None
        if key_up_events[0].key == K_ESCAPE:
            self.terminate_game()
        
        return key_up_events[0].key

    """exits the game"""        
    def terminate_game(self):
        sys.exit() 

'''the code that starts the game'''
if __name__ == "__main__":
    keep_playing = True
    hungryGame = HungryGame()
    while keep_playing:
        hungryGame.play()
        pygame.mixer.music.stop()
        hungryGame.gameOver.play()
        hungryGame.show_game_over()
