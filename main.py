from pygame import *
import threading # import packages

init() # initialize pygame

screen = display.set_mode((1200, 800)) # create display and clock
clock = time.Clock()

small_font = font.Font("freesansbold.ttf", 30) # create fonts
big_font = font.Font("freesansbold.ttf", 100)

icon = image.load("images/crate.png") # set window icon and caption
display.set_icon(icon)
display.set_caption("superfighters")

sound = mixer.Sound("sounds/gun-sound.mp3") # create sound

class Player: # class that creates players

    def __init__(self, x, color):

        self.x = x
        self.y = 100
        self.color = color

        self.gravity = True
        self.start = 0
        self.ascension = False
        self.falling = False

        self.fired = False
        self.fired_x = 0
        self.fired_y = 0
        self.firing_direction = "right"

        self.health = 100

plr1 = Player(1100, "green") # create instances of players
plr2 = Player(50, "red")

plrs = [plr1, plr2]
floor_array = []
game_running = True
PLAYER_LENGTH = 50

def map(): # function draws map and enters it into an array

    global floor_array
    FLOOR_DEPTH = 5

    screen.fill("gray")
    ground = draw.rect(screen, "black", Rect(0, 650, 1200, 200))
    floora = draw.rect(screen, "black", Rect(100, 550, 300, FLOOR_DEPTH))
    floorb = draw.rect(screen, "black", Rect(800, 550, 300, FLOOR_DEPTH))
    floorc = draw.rect(screen, "black", Rect(400, 450, 400, FLOOR_DEPTH))
    floord = draw.rect(screen, "black", Rect(0, 350, 300, FLOOR_DEPTH))
    floore = draw.rect(screen, "black", Rect(900, 350, 300, FLOOR_DEPTH))
    floorf = draw.rect(screen, "black", Rect(0, 150, 200, FLOOR_DEPTH))
    floorg = draw.rect(screen, "black", Rect(1000, 150, 200, FLOOR_DEPTH))
    floorh = draw.rect(screen, "black", Rect(200, 250, 800, FLOOR_DEPTH))

    floor_array = [ground, floora, floorb, floorc, floord, floore, floorf, floorg, floorh]

def boundaries(): # function stops players from exiting map boundaries

    for i in plrs:
        if i.x > 1200 - PLAYER_LENGTH:
            i.x = 1200 - PLAYER_LENGTH
        if i.x < 0:
            i.x = 0

def players(): # function draws players every frame

    for i in plrs:
        draw.rect(screen, i.color, Rect(i.x, i.y, PLAYER_LENGTH, PLAYER_LENGTH))

def gravity(): # function that handles gravity and when it is acceptable

    GRAVITY_INCREMENT = 5

    def check(rect, plr):

        for i in floor_array: # if their downward motion causes a floor collision, then reverse the downward motion
            if Rect.colliderect(rect, i):
                plr.y -= GRAVITY_INCREMENT
                plr.falling = False # also set falling false if gravity is valid (for later use)
                return
        plr.falling = True

    for i in plrs:

        if i.gravity: # first each player goes downward
            i.y += GRAVITY_INCREMENT
            rect = Rect(i.x, i.y, PLAYER_LENGTH, PLAYER_LENGTH)
            check(rect, i) # then players are checked to see if their downward motion is valid

def horizontal(): # function that handles horizontal movement

    HORIZONTAL_INCREMENT = 10

    if holdd and not holda: # designed such that holding down conflicting keys results in no motion

        plr2.x += HORIZONTAL_INCREMENT # first players are moved
        rect = Rect(plr2.x, plr2.y, PLAYER_LENGTH, PLAYER_LENGTH) # if their movement causes a floor collision, movement is reversed
        for i in floor_array:
            if Rect.colliderect(rect, i):
                plr2.x -= HORIZONTAL_INCREMENT

    if holda and not holdd:

        plr2.x -= HORIZONTAL_INCREMENT
        rect = Rect(plr2.x, plr2.y, PLAYER_LENGTH, PLAYER_LENGTH)
        for i in floor_array:
            if Rect.colliderect(rect, i):
                plr2.x += HORIZONTAL_INCREMENT

    if holdright and not holdleft:

        plr1.x += HORIZONTAL_INCREMENT
        rect = Rect(plr1.x, plr1.y, PLAYER_LENGTH, PLAYER_LENGTH)
        for i in floor_array:
            if Rect.colliderect(rect, i):
                plr1.x -= HORIZONTAL_INCREMENT

    if holdleft and not holdright:

        plr1.x -= HORIZONTAL_INCREMENT
        rect = Rect(plr1.x, plr1.y, PLAYER_LENGTH, PLAYER_LENGTH)
        for i in floor_array:
            if Rect.colliderect(rect, i):
                plr1.x += HORIZONTAL_INCREMENT

def jump_start(plr): # function that starts the jump state

    if not plr.ascension and not plr.falling: # makes sure players are on the ground
        plr.gravity = False # gravity disabled, start position noted, and player begins to ascend
        plr.start = plr.y
        plr.ascension = True

def jump_handle(): # function that handles jump movement

    JUMP_HEIGHT = 100
    JUMP_INCREMENT = 5

    for i in plrs:
        if i.ascension: # if ascension is true, players ascend
            i.y -= JUMP_INCREMENT

            if i.y <= i.start - JUMP_HEIGHT: # if players exceed a certain height denoted by their start position, ascension ends
                i.ascension = False
                i.gravity = True # and gravity begins
                i.falling = True # falling variable used to sure player can't jump while falling

def fire_start(plr): # function that initiates gunfire and handles damage

    if not plr.fired: # function only runs if player isn't still in a fire state

        def hit(): # runs with bullet collides with target
            target.health -= 30 # deduct target health
            if target.health <= 0: # make sure target health doesn't become negative
                target.health = 0
                game_over_animation(target) # start player falling animation when they die
                global game_running
                game_running = False # game no longer running

        plr.fired = True # fire state begins and fire coords noted
        plr.fired_x = plr.x
        plr.fired_y = plr.y

        mixer.Sound.play(sound) # sniper sound plays

        if plr == plr1:
            shooter, target = plr1, plr2 # determine the shooter and the target
        else:
            shooter, target = plr2, plr1

        if shooter.x < target.x: # determine which direction shooter will shoot
            shooter.firing_direction = "right"

            bullet_path_hitbox = Rect(plr.fired_x + PLAYER_LENGTH/2, plr.fired_y + 22, 1200, 6) # get hitboxes for bullet path and target
            target_hitbox = Rect(target.x, target.y, PLAYER_LENGTH, PLAYER_LENGTH)

            if Rect.colliderect(bullet_path_hitbox, target_hitbox): # if bullet collides with target, run hit function
                hit()

        else:
            shooter.firing_direction = "left"

            bullet_path_hitbox = Rect(0, plr.fired_y + 22, plr.fired_x + PLAYER_LENGTH/2, 6) # get hitboxes for bullet path and target
            target_hitbox = Rect(target.x, target.y, PLAYER_LENGTH, PLAYER_LENGTH)

            if Rect.colliderect(bullet_path_hitbox, target_hitbox): # if bullet collides with target, run hit function
                hit()

        def fire_end(): # function ends fire state
            plr.fired = False

        time = threading.Timer(0.5, fire_end) # fire state ends after half a second
        time.start()

def fire_handle(): # function that handles drawing the bullet

    for i in plrs:

        if i == plr1: # determine color of bullet depending on who shot it
            color = (150, 200, 150)
        else:
            color = (200, 150, 150)

        if i.fired: # if fire state is true
            if i.firing_direction == "right":
                bullet_rect = Rect(i.fired_x + PLAYER_LENGTH/2, i.fired_y + 22, 1200, 6)
                draw.rect(screen, color, bullet_rect) # draw bullet going to the right
            else:
                bullet_rect = Rect(0, i.fired_y + 22, i.fired_x + PLAYER_LENGTH/2, 6)
                draw.rect(screen, color, bullet_rect) # or draw bullet going to the left

def health(): # function that displays health

    plr2_health = small_font.render("health: "+str(plr2.health), True, "red") # render player health
    screen.blit(plr2_health, (60, 720)) # add player health render to screen

    plr1_health = small_font.render("health: "+str(plr1.health), True, "green")
    screen.blit(plr1_health, (980, 720))

def game_over_animation(loser): # function that runs when game is over

    loser.gravity = False # disable loser's gravity so they can actually fall out

    def fall_animation(): # function calls itself until the loser's y value is large enough
        if window_running: # this line exists so window doesn't hang
            loser.y += 20
            time = threading.Timer(0.02, fall_animation)
            time.start()

            if loser.y > 700:
                return

    fall_animation()

def game_over_announcement(): # function displays the game over announcement

    if not game_running: # if game is officially over

        if plr1.health == 0: # if player one lost
            ending_message = big_font.render("red wins!", True, "red") # display player two's victory
            screen.blit(ending_message, (370, 50))

        else: # else if player two lost
            ending_message = big_font.render("green wins!", True, "green") # display player one's victory
            screen.blit(ending_message, (300, 50))

map() # draw the map once so other functions can reference the floor array when the game starts

holdright, holdleft, holdd, holda = False, False, False, False

window_running = True
while window_running: # the main game loop

    for e in event.get(): # get game events

        if e.type == QUIT: # if quit event, close the window
            window_running = False

        if e.type == KEYDOWN: # if key down event...

            if e.key == K_d: # remember what keys are being held down
                holdd = True
            if e.key == K_a:
                holda = True
            if e.key == K_RIGHT:
                holdright = True
            if e.key == K_LEFT:
                holdleft = True

            if e.key == K_UP: # run jump function if up or w is pressed
                jump_start(plr1)
            if e.key == K_w:
                jump_start(plr2)

            if e.key == K_SLASH: # run gunfire function if slash or e is pressed
                fire_start(plr1)
            if e.key == K_e:
                fire_start(plr2)

        if e.type == KEYUP: # if key up event...

            if e.key == K_d: # remember what keys are being held down
                holdd = False
            if e.key == K_a:
                holda = False
            if e.key == K_RIGHT:
                holdright = False
            if e.key == K_LEFT:
                holdleft = False

    horizontal()

    gravity()

    boundaries()

    jump_handle()

    map()

    fire_handle()

    game_over_announcement()

    health()

    players()

    clock.tick(60) # caps game to 60 fps
    display.update() # update the display