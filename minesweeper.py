import pygame # type: ignore
import random
import os
import sys
import time

rows = 12       #  grid size
cols = 18
side = 50
SPC = 3 # spacing
startpos = 0, 70
screen_size = cols*(side+SPC)-SPC, rows*(side+SPC)-SPC + 75 # (951, 708)
screenMode = "big"

bs = 5 + screen_size[0] // 63 # button spacing
ms = screen_size[0] // 6.5 # mid spacing
btwngp = 3*bs #between button gap

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def setMiddle(swapSize, monitor_size):
    x = monitor_size[0]/2 - swapSize[0]/2
    y = monitor_size[1]/2 - swapSize[1]/2
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (x, y)

mystr = os.environ.get('SDL_VIDEO_WINDOW_POS')
print("SDL_VIDEO_WINDOW_POS", mystr)

pygame.init()
monitor_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
setMiddle(screen_size, monitor_size)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("minesweeper")
pygame_icon = pygame.image.load(resource_path("data/mine.png"))
pygame.display.set_icon(pygame_icon)
clock = pygame.time.Clock()

changeScreenSize = False
running = True
gameActive = True
isMainMenu = True

save_path = "data/run.txt"

THEME = "retro"
HIGHSCORES = {}
themes = ["retro", "minimalistic"]

HARD = 7
MEDIUM = 13
EASY = 18
difficulties = ["hard", "easy", "medium"]

gameDifficulty = HARD

# initialize surface images' surfaces and rects

one = pygame.image.load(resource_path("data/1.png")).convert_alpha()
one_rect = one.get_rect(midbottom = (0,0))

two = pygame.image.load(resource_path("data/2.png")).convert_alpha()
two_rect = two.get_rect(midbottom = (0,0))

three = pygame.image.load(resource_path("data/3.png")).convert_alpha()
three_rect = three.get_rect(midbottom = (0,0))

four = pygame.image.load(resource_path("data/4.png")).convert_alpha()
four_rect = four.get_rect(midbottom = (0,0))

five = pygame.image.load(resource_path("data/5.png")).convert_alpha()
five_rect = five.get_rect(midbottom = (0,0))

retro_flag = pygame.image.load(resource_path("data/flag.png")).convert_alpha()
# retro_flag = pygame.transform.scale(retro_flag, (side, side))
retro_flag_rect = retro_flag.get_rect(midbottom = (0,0))

black = pygame.Surface((side, side))
black_rect = black.get_rect()

retro_surfs = [one, two, three, four, five, black, black, black, black]
retro_rects = [one_rect, two_rect, three_rect, four_rect, five_rect, black_rect, black_rect, black_rect, black_rect]

clean_surfs = []
clean_rects = []
for i in range(0, 9):
    clean_surfs.append(pygame.Surface((side, side)))
    clean_rects.append(clean_surfs[i].get_rect())

clean_surfs[0].fill("#03BFFF")
clean_surfs[1].fill("#0311BE")
clean_surfs[2].fill("#000060")
clean_surfs[3].fill("#0C0320")
clean_surfs[4].fill("#40040A")
clean_surfs[5].fill("#AF0205")
clean_surfs[6].fill("#CF0202")
clean_surfs[7].fill("#FF0000")
clean_surfs[8].fill("#FFFF00")

clean_cross = pygame.image.load(resource_path("data/white_cross.png")).convert_alpha()
clean_cross = pygame.transform.scale(clean_cross, (side*.7, side*.7))
clean_cross_rect = clean_cross.get_rect()

white_land_mine = pygame.image.load(resource_path("data/land_mine_white.png")).convert_alpha()
white_land_mine = pygame.transform.scale(white_land_mine, (side*.7, side*.7))
white_land_mine_rect = white_land_mine.get_rect()

clean_red_cross = pygame.image.load(resource_path("data/red_cross.png")).convert_alpha()
clean_red_cross = pygame.transform.scale(clean_red_cross, (side*.7, side*.7))
clean_red_cross_rect = clean_red_cross.get_rect()

fat_red_cross = pygame.image.load(resource_path("data/fatcoss.png")).convert_alpha()
fat_red_cross = pygame.transform.scale(fat_red_cross, (side, side))
fat_red_cross_rect = fat_red_cross.get_rect()

# pygame init for default font

text_font = pygame.font.Font(None, 50)
retro_font = pygame.font.Font(None, 40)
clean_bomb_font = pygame.font.SysFont("yugothic", 50) # yugothic
clean_font = pygame.font.SysFont("simsun", 30, False, True)
clean_time_font = pygame.font.SysFont("yugothic", 31)
retro_big_font = pygame.font.Font(None, screen_size[0] // 15)
clean_big_font = pygame.font.SysFont("simsun", screen_size[0] // 20, False, True)

# default colors
NORMAL      = "#000033"
BACKGROUND  = "#001933"
STEPPED     = "Blue"

# fill entire display surface with background color
screen.fill(BACKGROUND)

# block class
class Block:
    def __init__(self, size, pos, surface, gridpos, difficulty = None): # Draws itself to displaysurface when initialized

        self.color = NORMAL
        self.bomb = 0
        if not difficulty == None:
            if random.randint(0, difficulty) == 0:  # Hard = (0, 3)
                self.bomb = 1         
    
        self.row = gridpos[0]
        self.col = gridpos[1]

        self.surf = pygame.Surface(size)    
        self.surf.fill(self.color)
        self.rect = self.surf.get_rect(topleft = pos)
        surface.blit(self.surf, self.rect)
    
    def change_color(self, color, surface):
        self.color = color
        self.surf.fill(self.color)
        surface.blit(self.surf, self.rect)

    def setbomb(self, randomness):
        if random.randint(0, randomness) == 0:  # hard = (0, 3)
            self.bomb = 1
        else:
            self.bomb = 0

# takes a cell and returns the grid-position of every surrounding as an array of tuples
def get_neighbors(cell):
    neighbors = []
    for x in range(-1,2):
        for y in range(-1,2):
            if cell.row+x >= 0 and cell.row+x<rows and cell.col+y>=0 and cell.col+y<cols and not (x == 0 and y == 0):
                neighbors.append((cell.row+x, cell.col+y))
    return neighbors

def randomize_bombs():
    global bomb_counter
    bomb_counter = 0
    for row in grid:
        for cell in row:
            cell.setbomb(gameDifficulty)
            if cell.bomb == 1:
                bomb_counter += 1

# create grid and draw every block
def create_grid(rows, cols, side, startpos):
    screen.fill(BACKGROUND)

    global grid, bomb_counter, flag_counter, bombs_close, touched, flagged
    grid = []  # array of rows
    bomb_counter = 0
    flag_counter = 0
    bombs_close = {} # (tuple) : (int)
    touched = []
    flagged = []

    for i in range(rows):
        row = [] 
        for j in range(cols):
            row.append(Block((side,side), (j*(side+SPC) + startpos[0], i*(side+SPC) + startpos[1]), screen, (i, j), gameDifficulty)) # (size, pos, surface, gridpos)
            if row[j].bomb == 1:
                bomb_counter += 1
        grid.append(row)

    print("-------------------------------------------------------------------------")
    print((1.0 / gameDifficulty) * cols * rows - 1, bomb_counter, (1 / gameDifficulty) * cols * rows * (3 / 2))
    while bomb_counter < (1.0 / gameDifficulty) * cols * rows - 1 or bomb_counter > (1 / gameDifficulty) * cols * rows * (3 / 2):
        randomize_bombs()
        print((1.0 / gameDifficulty) * cols * rows - 1, bomb_counter, (1 / gameDifficulty) * cols * rows * (3 / 2))

    # fill bombs_close dictionary
    for row in grid: # loop through entire grid
        for cell in row:
            neighbors = get_neighbors(cell) 
            bombs = 0
            
            for n in neighbors: # loop through the cell's neighbors
                if grid[n[0]][n[1]].bomb: # n[0] = row, n[1] = column
                    bombs += 1
            
            bombs_close[(cell.row, cell.col)] = bombs
    
    update_bomb_text()
    displayDif()

    clean = []
    for key in bombs_close.keys():
        if bombs_close[key] == 0 and grid[key[0]][key[1]].bomb == 0:
            clean.append(key)

    start = clean[random.randint(0, len(clean)-1)]
    step(grid[start[0]][start[1]])

def update_bomb_text():
    bombs = bomb_counter - flag_counter
    if bombs < 0:
        bombs = 0

    if THEME == "minimalistic":
        text = clean_bomb_font.render(str(bombs), True, BTEXTCOLOR)
        text_rect = text.get_rect(midbottom = (screen_size[0]/2, startpos[1]))
    else:
        bombtext = "bombs: " + str(bombs)
        text = text_font.render(bombtext, True, BTEXTCOLOR)
        text_rect = text.get_rect(bottomleft = (10, 65))

    textreset = pygame.Surface((text_rect.width*2, text_rect.height))
    textreset_rect = textreset.get_rect(midbottom = text_rect.midbottom) 
    textreset.fill(BACKGROUND)
    screen.blit(textreset, textreset_rect)
    screen.blit(text, text_rect)

def checkHighscore():
    global roundtime
    roundtime = pygame.time.get_ticks() - TIME

    if not hasWon():
        return False

    if gameDifficulty == HARD:
        gdtmp = "hard"
    elif gameDifficulty == MEDIUM:
        gdtmp = "medium"
    elif gameDifficulty == EASY:
        gdtmp = "easy"
    else:
        return False

    if screenMode in HIGHSCORES:
        if gdtmp in HIGHSCORES[screenMode]:
            if roundtime < HIGHSCORES[screenMode][gdtmp]:
                HIGHSCORES[screenMode][gdtmp] = roundtime
                return True
        else:
            empty = {}
            empty[gdtmp] = roundtime
            HIGHSCORES[screenMode] = empty
            return True
    else:
        empty = {}
        empty[gdtmp] = roundtime
        HIGHSCORES[screenMode] = empty
        return True

    return False

def find_cell(pos):
    for row in range(rows):
        for col in range(cols):
            if grid[row][col].rect.collidepoint(pos):
                return row, col
    return None

def step(cell): # return True if stepped on bomb
    r = cell.row
    c = cell.col

    global pushed, steppedTime
    if (r,c) in flagged or (r,c) in touched:
        if pushed and pygame.time.get_ticks() - steppedTime > 500:
            copy = []
            for p in pushed:
                copy.append(p)
            unPush()

            death = []
            died = False
            for d in copy:
                if grid[d[0]][d[1]].bomb:
                    death.append(d)
                    died = True
            if died:
                revealMines(death)
                return True
            else:
                for d in copy:
                    step(grid[d[0]][d[1]])
        else:
            unPush()
            return
    unPush()

    if (r,c) not in touched:
        cell.change_color(STEPPED, screen)
        touched.append((r,c))

    global rects

    if cell.bomb:
        revealMines([(r,c)])
        return True
    elif bombs_close[(r,c)] == 0:
        steppedTime = pygame.time.get_ticks()
        neighbors = get_neighbors(cell)
        for bob in neighbors:
            if not bob in touched:
                step(grid[bob[0]][bob[1]])
    else:
        n = bombs_close[(r,c)] - 1
        rects[n].midbottom = cell.rect.midbottom
        screen.blit(surfs[n], rects[n])

def hasWon():
    # print(len(touched) - len(flagged), rows * cols - bomb_counter)
    if len(touched) - len(flagged) == rows * cols - bomb_counter:
        return True
    else:
        return False

def revealMines(pos):
    global mine_rect, red_cross_rect
    for row in grid:
        for cell in row:
            if cell.bomb:
                c = cell.row, cell.col
                if THEME == "minimalistic":
                    if (cell.row, cell.col) in pos:
                        cell.change_color("Red", screen)
                        mine_rect.center = cell.rect.center
                        screen.blit(mine, mine_rect)
                    elif not c in flagged:
                        cell.change_color(NORMAL, screen)
                        mine_rect.center = cell.rect.center
                        screen.blit(mine, mine_rect)
                elif THEME == "retro":
                    if (cell.row, cell.col) in pos:
                        cell.change_color("Red", screen)
                    else:
                        cell.change_color(NORMAL, screen)
                    mine_rect.center = cell.rect.center
                    screen.blit(mine, mine_rect)
                    if c in flagged:
                        red_cross_rect.center = cell.rect.center
                        screen.blit(red_cross, red_cross_rect)
    
    if THEME == "minimalistic":
        for p in flagged:
            cell = grid[p[0]][p[1]]
            if not cell.bomb:
                cell.change_color(NORMAL, screen)
                red_cross_rect.center = cell.rect.center
                screen.blit(red_cross, red_cross_rect)

def flag(cell):
    r = cell[0]
    c = cell[1]
    global flag_counter

    if not (r,c) in flagged and (r,c) not in touched:
        global flag_rect
        flag_rect.center = grid[r][c].rect.center
        screen.blit(flag_surf, flag_rect)
        flagged.append((r,c))
        touched.append((r,c))
        flag_counter += 1

    elif (r,c) in flagged:
        grid[r][c].change_color(NORMAL, screen)
        flagged.remove((r,c))
        touched.remove((r,c))
        flag_counter -= 1
    
    update_bomb_text()

def loadStats():
    global THEME, HIGHSCORES, gameDifficulty, isMainMenu
    if not os.path.isfile(save_path):
        return

    with open(save_path, "r") as f:
        text = f.read()

    d = {}
    for row in text.split(",\n"):
        if row.count("=") == 1:
            half = row.split("=", 1)
            d[half[0].strip()] = half[1].strip()

    print(d)

    if "difficulty" in d.keys():
        difficulty = d["difficulty"]
    else:
        difficulty = 26
    if "theme" in d.keys() and d["theme"] in themes:
        THEME = d["theme"]
    if "mainmenu" in d.keys():
        if d["mainmenu"] == "True":
            isMainMenu = True
        else:
            isMainMenu = False

    match difficulty:
        case "hard":
            gameDifficulty = HARD
        case "medium":
            gameDifficulty = MEDIUM
        case "easy":
            gameDifficulty = EASY
        case _:
            gameDifficulty = MEDIUM
loadStats()

def saveStats():
    
    if gameDifficulty == EASY:
        dif = "easy"
    elif gameDifficulty == MEDIUM:
        dif = "medium"
    elif gameDifficulty == HARD:
        dif = "hard"

    output = []
    output.append(f"difficulty = {dif}")
    output.append(f"theme = {THEME}")
    output.append(f"mainmenu = {isMainMenu}")
    for window in HIGHSCORES:
        for size in HIGHSCORES[window]:
            output.append(f"highscore {window} {size} = {HIGHSCORES[window][size]}")

    print("out\n", output)

    with open(save_path, "r") as f:
        for line in output:
                f.write(line + ",\n")  


def changeTheme(theme):
    global THEME, BACKGROUND, NORMAL, SPC, STEPPED, surfs, rects, flag_surf, flag_rect, startpos, BUTTONCOLOR, BUTTONTEXT, SELECTCOLOR, SELECTWIDTH, BTEXTCOLOR, FONT, SMALL_FONT, PUSH, mine_rect, mine, red_cross, red_cross_rect, text_font, retro_font, gameDifficulty, clean_bomb_font, clean_font, clean_time_font, clean_small_font, retro_small_font, MMSUBCOL, retro_big_font, clean_big_font, BIG_FONT

    text_font = pygame.font.Font(None, screen_size[1] // 14)
    retro_font = pygame.font.Font(None, screen_size[1] // 17)
    retro_small_font = pygame.font.Font(None, screen_size[1] // 23)
    clean_bomb_font = pygame.font.SysFont("yugothic", screen_size[1] // 14) # yugothic
    clean_time_font = pygame.font.SysFont("yugothic", screen_size[1] // 23 + 1)
    clean_font = pygame.font.SysFont("simsun", screen_size[1] // 23, False, True)
    tmp = screen_size[1] // 30
    if tmp < 24:
        tmp = 24
    clean_small_font = pygame.font.SysFont("simsun", tmp, False, True)

    if theme == "minimalistic":
        surfs       = clean_surfs
        rects       = clean_rects
        flag_surf   = clean_cross
        flag_rect   = clean_cross_rect
        mine        = white_land_mine
        mine_rect   = white_land_mine_rect
        red_cross   = clean_red_cross
        red_cross_rect = clean_red_cross_rect

        BACKGROUND  = "#050820"
        NORMAL      = "#102030"
        SPC         = 0
        STEPPED     = "#CAF7F2"
        BUTTONCOLOR = "#BFDDFF"
        BUTTONTEXT  = "#100642"
        SELECTCOLOR = "#0511FE" # #0511FE
        SELECTWIDTH = screen_size[0] // 115
        BTEXTCOLOR  = "#03BFFF"
        FONT        = clean_font
        SMALL_FONT  = clean_small_font
        MMSUBCOL    = BUTTONCOLOR
        BIG_FONT    = clean_big_font

        startpos = (screen_size[0] - (cols*(side+SPC)-SPC))/2, startpos[1]

    elif theme == "retro":
        NORMAL      = "#000033"
        BACKGROUND  = "#001933"
        STEPPED     = "Blue"
        SPC         = 3
        BUTTONCOLOR = "Black"
        BUTTONTEXT  = "White"
        SELECTCOLOR = "Yellow"
        SELECTWIDTH = screen_size[0] // 200
        BTEXTCOLOR  = "White"
        FONT        = retro_font
        SMALL_FONT  = retro_small_font
        MMSUBCOL    = BTEXTCOLOR
        BIG_FONT    = retro_big_font

        surfs       = retro_surfs
        rects       = retro_rects
        flag_surf   = retro_flag
        flag_rect   = retro_flag_rect
        mine        = white_land_mine
        mine_rect   = white_land_mine_rect
        red_cross       = fat_red_cross
        red_cross_rect  = fat_red_cross_rect

        startpos = 0, 70
    elif theme == "original":
        pass

    col = pygame.Color(STEPPED)
    PUSH = pygame.Color(int(0.5 * col.r), int(0.5 * col.g), int(0.5 * col.b))
changeTheme(THEME)

class Button:
    def __init__(self, text, font = None, color = None, buttonsp = None, row2 = None, cat = None, background = None):
        self.specialfont = font
        self.specialcolor = color
        self.specialbg = background

        if font == None:
            font = FONT
        if cat == "small":
            font = SMALL_FONT
        if color == None:
            color = BUTTONTEXT
            
        self.cat = cat
        self.col = color
        self.id = text
        self.surf = font.render(text, True, color)
        self.rect = self.surf.get_rect()
        self.row2 = row2
        if row2:
            self.surf2 = font.render(row2, True, color)
            if self.surf.get_rect().width > self.surf2.get_rect().width:
                width = self.surf.get_rect().width
            else:
                width = self.surf2.get_rect().width
            self.rect = pygame.Rect(0, 0, width, self.surf.get_rect().height + self.surf2.get_rect().height)
        self.beenOut = True


        if buttonsp == None:
            if cat == "small":
                self.bs = bs // 1.6
            else:
                self.bs = bs
        else:
            self.bs = buttonsp
        
        
        self.font = font
        if isMainMenu:
            all_buttons.append(self)

    def surround(self):
        rect = self.rect
        return pygame.Rect(rect.left - self.bs, rect.top - self.bs, rect.width + 2*self.bs, rect.height + 2*self.bs)

    def draw(self, bgcolor = None, textcolor = None):
        if textcolor != None:
            self.surf = self.font.render(self.id, True, textcolor)
        rect = self.rect
        if bgcolor == None:
            if self.specialbg != None:
                bgcolor = self.specialbg
            else:
                bgcolor = BUTTONCOLOR
        else:
            self.specialbg = bgcolor
            
        bg = pygame.Surface((rect.width + 2*self.bs, rect.height + 2*self.bs))
        bg.fill(bgcolor)
        # print(f"inside: ({self.id}) printing with backgroundcolor: ({color})")
        
        screen.blit(bg, (rect.left - self.bs, rect.top - self.bs))
        if not self.row2: # If button has 2 rows
            screen.blit(self.surf, rect)
        else:
            print(f"inside!!!!! {self.id} !!!!")
            screen.blit(self.surf, (self.rect.left + (self.rect.width - self.surf.get_rect().width)//2, self.rect.top))
            screen.blit(self.surf2, (self.rect.left + (self.rect.width - self.surf2.get_rect().width)//2, self.rect.top + self.surf.get_rect().height))
        if isMainMenu and not self.id in active_buttons:
            active_buttons.append(self.id)

    def hide(self):
        rect = self.rect
        bg = pygame.Surface((rect.width + 2*self.bs, rect.height + 2*self.bs))
        bg.fill(BACKGROUND)
        screen.blit(bg, (rect.left - self.bs, rect.top - self.bs))
        if isMainMenu and self.id in active_buttons:
            active_buttons.remove(self.id)

    def update(self, textcolor = None, background = None):
        self.font = FONT
        if self.specialfont:
            self.font = self.specialfont
        if textcolor:
            self.col = textcolor
        else:
            self.col = BUTTONTEXT
        if self.specialfont:
            self.font = self.specialfont
        if background:
            self.specialbg = background


        if self.cat == "small":
            self.font = SMALL_FONT

        self.surf = self.font.render(self.id, True, self.col)
        self.rect = self.surf.get_rect()
        if self.row2:
            self.surf2 = self.font.render(self.row2, True, self.col)
            if self.surf.get_rect().width > self.surf2.get_rect().width:
                width = self.surf.get_rect().width
            else:
                width = self.surf2.get_rect().width
            self.rect = pygame.Rect(0, 0, width, self.surf.get_rect().height + self.surf2.get_rect().height)


def restartScreen():
    global screen
    highscore = checkHighscore()
    won = hasWon()

    time_sec = roundtime/1000
    
    if won:
        displaycolor = BTEXTCOLOR
    else:
        displaycolor = "Red"

    if THEME == "minimalistic":
        if highscore and won:
            displaycolor = "Yellow"
        text = clean_time_font.render(str(time_sec)+"s", True, displaycolor)
        text_rect = text.get_rect(bottomright = (screen_size[0]-startpos[0], startpos[1] - 5))

    elif THEME == "retro":
        text = text_font.render(str(time_sec)+"s", True, displaycolor)
        text_rect = text.get_rect(bottomright = (screen_size[0]-10, 65))
    screen.blit(text, text_rect)

    mmb = Button("main menu", BIG_FONT, BUTTONTEXT, buttonsp=screen_size[0]//60 + 5)
    mmb.rect.center = (5 * screen_size[0] // 10, 8* screen_size[1] // 10)
    mmb.draw(BUTTONCOLOR)

    if screenMode == "fullscreen":
        qb = Button("exit", BIG_FONT, "White")
        qb.rect.bottomright = (9.5 * screen_size[0] // 10, 9.5* screen_size[1] // 10 - qb.bs) # (screen_size[0] - 40 - qb.bs, screen_size[1] - qb.bs - 30)
        qb.draw("Red")

    global isMainMenu, running, gameActive
    i = 0
    y = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEWHEEL:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    isMainMenu = True
                    gameActive = True
                    return
                else:
                    gameActive = True
                    changeTheme(THEME)
                    create_grid(rows, cols, side, startpos)
                    return
            if event.type == pygame.MOUSEMOTION:
                if mmb.surround().collidepoint(event.pos) and mmb.beenOut == True:
                    pygame.draw.rect(screen, SELECTCOLOR, mmb.surround(), SELECTWIDTH) 
                    mmb.beenOut = False
                elif not mmb.surround().collidepoint(event.pos):
                    pygame.draw.rect(screen, mmb.specialbg, mmb.surround(), SELECTWIDTH) 
                    mmb.beenOut = True
                if screenMode == "fullscreen":
                    if qb.surround().collidepoint(event.pos) and qb.beenOut == True:
                        pygame.draw.rect(screen, SELECTCOLOR, qb.surround(), SELECTWIDTH) 
                        qb.beenOut = False
                    elif not qb.surround().collidepoint(event.pos):
                        pygame.draw.rect(screen, qb.specialbg, qb.surround(), SELECTWIDTH) 
                        qb.beenOut = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if mmb.surround().collidepoint(event.pos):
                    isMainMenu = True
                    gameActive = True
                    return
                if screenMode == "fullscreen" and qb.surround().collidepoint(event.pos):
                    running = False
                    return
            
        if i%20 == 0 and won and highscore == True:
            if y == 0:
                displaycolor = "Yellow"
                y += 1
            else:
                y -= 1
                displaycolor = BTEXTCOLOR
            if THEME == "retro":
                text = text_font.render("highscore! "+str(time_sec)+"s", True, displaycolor)
                text_rect = text.get_rect(bottomright = (screen_size[0]-10, 65))
            screen.blit(text, text_rect)

        i += 1
        pygame.display.update()
        clock.tick(60)

pushed = []
def push(cell):
    global pushed
    pos = cell.row, cell.col

    if not pos in touched:
        if not pos in pushed:
            pushed.append(pos)
            cell.change_color(PUSH, screen)

        temp = pushed
        for p in temp:
            if p != pos:
                pushed.remove(p)
                grid[p[0]][p[1]].change_color(NORMAL, screen)
    elif not pos in flagged: # Cell is in touched but not flagged
        neighbors = get_neighbors(cell)

        for n in neighbors:
            if not n in pushed and not n in touched:
                pushed.append(n)
                grid[n[0]][n[1]].change_color(PUSH, screen)

        temp = pushed
        for p in temp:
            if p not in neighbors:
                pushed.remove(p)
                grid[p[0]][p[1]].change_color(NORMAL, screen)
        
def unPush():
    global pushed
    for p in pushed:
        grid[p[0]][p[1]].change_color(NORMAL, screen)
    pushed.clear()

def minesweeper():
    global gameActive, running, TIME, isMainMenu

    mouse1down = False
    started = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                isMainMenu = True
                gameActive = True
                return

            if started == False and event.type == pygame.MOUSEBUTTONDOWN:
                TIME = pygame.time.get_ticks()
                started = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current = find_cell(event.pos)
                if current != None:
                    push(grid[current[0]][current[1]])
                mouse1down = True

            if event.type == pygame.MOUSEMOTION and mouse1down == True:
                current = find_cell(event.pos)
                if current != None:
                    push(grid[current[0]][current[1]])

            if event.type == pygame.MOUSEBUTTONUP:
                mouse1down = False
                current = find_cell(event.pos)

                if event.button == 1 and current:
                    global curentStart
                    currentStart = current
                    if step(grid[current[0]][current[1]]): # Returns True if cell has bomb
                        gameActive = False
                        return
                    elif hasWon() == True:
                        gameActive = False
                        return

                elif event.button == 3 and current:
                    flag(current)
                else:
                    unPush()
        pygame.display.update()
        clock.tick(60)

def mainMenu():
    global THEME, subtheme_rect, subdif_rect, midofscreen, res_area
    screen.fill(BACKGROUND)

    x = screen_size[0]/2
    y = screen_size[1]/2
    midofscreen = x, y
    
    global active_buttons, all_buttons
    active_buttons = []
    all_buttons = []

    # difficulty menu objects
    dif = Button("difficulty")
    dif.rect.center = (x - ms, y)
    hard = Button("hard")
    easy = Button("easy")
    mid = Button("mid")
    mid.rect.center = dif.rect.center
    hard.rect.midbottom = (mid.rect.centerx, mid.rect.top - btwngp)
    easy.rect.midtop = (mid.rect.centerx, mid.rect.bottom + btwngp)

    # for the submenu
    widest = easy
    for b in easy, mid, hard:
        if b.rect.width > widest.rect.width:
            widest = b
    subdif_rect = pygame.Rect(widest.rect.left - bs, hard.rect.top - bs, widest.rect.width + 2 * bs, easy.rect.bottom - hard.rect.top + 2 * bs)
    subdifbeen = False

    # theme menu objects
    theme = Button("theme")
    theme.rect.center = (x + ms, y)
    clean = Button("minimalistic", clean_font)
    retro = Button("retro", retro_font)
    org = Button("original")

    retro.rect.center = theme.rect.center
    org.rect.midbottom = (retro.rect.centerx, retro.rect.top - btwngp)
    clean.rect.midtop = (retro.rect.centerx, retro.rect.bottom + btwngp)

    # for the submenu
    widest = retro
    for b in retro, org, clean:
        if b.rect.width > widest.rect.width:
            widest = b
    subtheme_rect = pygame.Rect(widest.rect.left - bs, org.rect.top - bs, widest.rect.width + 2 * bs, clean.rect.bottom - org.rect.top + 2 * bs)
    subthemebeen = False

    # Resolution buttons
    res = Button("resolution", cat="small")
    res.rect.topright = (screen_size[0] - 2*res.bs, 2*res.bs)
    res.draw()

    fullscreen = Button("fullscreen", cat="small")
    big = Button("big", cat="small")
    small = Button("small", cat="small")

    fullscreen.rect.midright = (res.surround().left - 2*fullscreen.bs, res.rect.centery)
    big.rect.topright = (fullscreen.rect.left - 3*big.bs, fullscreen.rect.top)
    small.rect.topright = (big.rect.left - 3*big.bs, big.rect.top)

    current = Button(str(screen_size), color=MMSUBCOL, cat="small", background=BACKGROUND)
    current.rect.midtop = (res.rect.centerx, res.rect.bottom + 2*fullscreen.bs)

    # Total area of all resolution-buttons
    h = 0
    for obj in [res, fullscreen, small, big]:
        if obj.surround().height > h:
            h = obj.surround().height
    res_area = pygame.Rect((small.surround().left, 0), (screen_size[0], h))

    scores = Button("highscores", cat="small")
    scores.rect.topleft = (scores.bs*2, scores.bs*2)
    scores.draw()
    isShowingScores = False

    def updateMainMenu():
        global subdif_rect, subtheme_rect, res_area
        screen.fill(BACKGROUND)

        for b in all_buttons:
            b.update()

        current.update(MMSUBCOL, BACKGROUND)

        dif.rect.center = (x - ms, y)
        mid.rect.center = dif.rect.center
        hard.rect.midbottom = (mid.rect.centerx, mid.rect.top - btwngp)
        easy.rect.midtop = (mid.rect.centerx, mid.rect.bottom + btwngp)
        widest = easy
        for b in easy, mid, hard:
            if b.rect.width > widest.rect.width:
                widest = b
        subdif_rect = pygame.Rect(widest.rect.left - bs, hard.rect.top - bs, widest.rect.width + 2 * bs, easy.rect.bottom - hard.rect.top + 2 * bs)
        theme.rect.center = (x + ms, y)
        retro.rect.center = theme.rect.center
        org.rect.midbottom = (retro.rect.centerx, retro.rect.top - btwngp)
        clean.rect.midtop = (retro.rect.centerx, retro.rect.bottom + btwngp)

        widest = retro
        for b in retro, org, clean:
            if b.rect.width > widest.rect.width:
                widest = b
        subtheme_rect = pygame.Rect(widest.rect.left - bs, org.rect.top - bs, widest.rect.width + 2 * bs, clean.rect.bottom - org.rect.top + 2 * bs)

        res.rect.topright = (screen_size[0] - 2*res.bs, 2*res.bs)

        fullscreen.rect.midright = (res.surround().left - 2*fullscreen.bs, res.rect.centery)
        big.rect.topright = (fullscreen.rect.left - 3*big.bs, fullscreen.rect.top)
        small.rect.topright = (big.rect.left - 3*big.bs, big.rect.top)

        h = 0
        for obj in [res, fullscreen, small, big]:
            if obj.surround().height > h:
                h = obj.surround().height
        res_area = pygame.Rect((small.surround().topleft), (res.surround().right - small.surround().left, h))

        current.rect.midtop = (res.rect.centerx, res.rect.bottom + 2*fullscreen.bs)

        for b in all_buttons:
            if b.id in active_buttons:
                b.draw()

    # asigning which theme is selected
    for t in clean, org, retro:
        if t.id == THEME:
            selected = t

    theme.draw()
    dif.draw()
    
    global isMainMenu, running, changeScreenSize, screenMode
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.MOUSEMOTION:
                if res.id in active_buttons and res.surround().collidepoint(event.pos):
                    fullscreen.draw()
                    big.draw()
                    small.draw()
                    current.draw()
                    for G in [small, big, fullscreen]:
                        if G.id == screenMode:
                            pygame.draw.rect(screen, SELECTCOLOR, G.surround(), SELECTWIDTH)
                if small.id in active_buttons and not res_area.collidepoint(event.pos):
                    fullscreen.hide()
                    big.hide()
                    small.hide()     
                    current.hide()
                if theme.id in active_buttons:
                    if theme.surround().collidepoint(event.pos) and theme.beenOut == True:
                        theme.hide()
                        theme.beenOut = False
                        clean.draw()
                        org.draw()
                        retro.draw()
                        pygame.draw.rect(screen, SELECTCOLOR, selected.surround(), SELECTWIDTH)
                    elif not theme.surround().collidepoint(event.pos):
                        theme.beenOut = True
                if org.id in active_buttons:
                    if subtheme_rect.collidepoint(event.pos):
                        subthemebeen = True
                    elif not subtheme_rect.collidepoint(event.pos) and subthemebeen == True or not theme.surround().collidepoint(event.pos):
                        org.hide()
                        clean.hide()
                        retro.hide()
                        subthemebeen = False
                        theme.draw()
                if dif.id in active_buttons:
                    if dif.surround().collidepoint(event.pos) and dif.beenOut == True:
                        dif.hide()
                        dif.beenOut = False
                        hard.draw()
                        mid.draw()
                        easy.draw()
                    elif not dif.surround().collidepoint(event.pos):
                        dif.beenOut = True
                if hard.id in active_buttons:
                    if subdif_rect.collidepoint(event.pos):
                        subdifbeen = True
                    elif not subdif_rect.collidepoint(event.pos) and subdifbeen == True or not dif.surround().collidepoint(event.pos):
                        hard.hide()
                        mid.hide()
                        easy.hide()
                        subdifbeen = False
                        dif.draw()
                if scores.id in active_buttons and isShowingScores == False:
                    if scores.surround().collidepoint(event.pos):
                        pygame.draw.rect(screen, "White", scores.surround(), SELECTWIDTH)
                    else:
                        pygame.draw.rect(screen, BUTTONCOLOR, scores.surround(), SELECTWIDTH)
                elif scores.id in active_buttons and isShowingScores == True:
                    if scores.surround().collidepoint(event.pos) and scores.beenOut == False:
                        print("been out for scores:", scores.beenOut)
                        pygame.draw.rect(screen, "White", scores.surround(), SELECTWIDTH)
                    elif not scores.surround().collidepoint(event.pos):
                        scores.beenOut = False
                        pygame.draw.rect(screen, SELECTCOLOR, scores.surround(), SELECTWIDTH)
            if event.type == pygame.MOUSEBUTTONUP: # On click-event in main menu
                if hard.id in active_buttons:
                    if hard.surround().collidepoint(event.pos) or mid.surround().collidepoint(event.pos) or easy.surround().collidepoint(event.pos):
                        global gameDifficulty
                        if hard.surround().collidepoint(event.pos):
                            gameDifficulty = HARD
                        elif mid.surround().collidepoint(event.pos):
                            gameDifficulty = MEDIUM
                        elif easy.surround().collidepoint(event.pos):
                            gameDifficulty = EASY

                        isMainMenu = False
                        changeTheme(THEME)
                        create_grid(rows, cols, side, startpos)
                        active_buttons.clear()
                        return
                if org.id in active_buttons: # Theme buttons
                    if org.surround().collidepoint(event.pos) or retro.surround().collidepoint(event.pos) or clean.surround().collidepoint(event.pos): # If any of the theme buttons are pressed
                        if clean.surround().collidepoint(event.pos):
                            if selected != clean:
                                pygame.draw.rect(screen, clean.col, selected.surround(), SELECTWIDTH)
                            selected = clean
                        elif retro.surround().collidepoint(event.pos):
                            print("active buttons when in retro: ", active_buttons)
                            if selected != retro:
                                pygame.draw.rect(screen, retro.col, selected.surround(), SELECTWIDTH)
                            selected = retro
                        elif org.surround().collidepoint(event.pos):
                            screen.fill("Yellow")

                        THEME = selected.id
                        subthemebeen = False
                        changeTheme(THEME)
                        updateMainMenu()                        

                        pygame.draw.rect(screen, SELECTCOLOR, selected.surround(), SELECTWIDTH)
                # If any resolution buttons are clicked
                if small.id in active_buttons and (small.surround().collidepoint(event.pos) or big.surround().collidepoint(event.pos) or fullscreen.surround().collidepoint(event.pos)):
                    changeScreenSize = True
                    if fullscreen.surround().collidepoint(event.pos) and screenMode != "fullscreen":
                        screenMode = "fullscreen"
                    elif big.surround().collidepoint(event.pos) and screenMode != "big":
                        screenMode = "big"
                    elif small.surround().collidepoint(event.pos) and screenMode != "small":
                        screenMode = "small"
                    return
                if scores.id in active_buttons and scores.surround().collidepoint(event.pos) and isShowingScores == False:
                    pygame.draw.rect(screen, SELECTCOLOR, scores.surround(), SELECTWIDTH)
                    isShowingScores = True
                    scores.beenOut = True
                    for st in all_buttons:
                        if st.id in active_buttons and st != scores:
                            st.hide()
                elif scores.id in scores.id in active_buttons and scores.surround().collidepoint(event.pos) and isShowingScores == True:
                    res.draw()
                    theme.draw()
                    dif.draw()
                    isShowingScores = False
                        

        pygame.display.update()
        clock.tick(60)

def displayDif():
    if gameDifficulty == EASY:
        dif = "easy"
    elif gameDifficulty == MEDIUM:
        dif = "medium"
    elif gameDifficulty == HARD:
        dif = "hard"
    else:
        dif = str(gameDifficulty)
    
    if not dif in difficulties:
        return

    if THEME == "minimalistic":
        text = clean_font.render(dif, True, BTEXTCOLOR)
        textrect = text.get_rect(bottomleft = (startpos[0], startpos[1] - 10))
    else:
        text = text_font.render(dif, True, BTEXTCOLOR)
        textrect = text.get_rect(midbottom = (screen_size[0]/2, 60))
    

        
    screen.blit(text, textrect)

def newScreen(mode):
    global screen, cols, rows, startpos, screen_size, screenMode, changeScreenSize
    changeScreenSize = False

    if mode not in ["small", "big", "fullscreen"]:
        return

    if mode == "small":
        changeTheme("retro")
        rows = 10
        cols = 10
        screen_size = cols*(side+SPC)-SPC, rows*(side+SPC)-SPC + 60
        screen = pygame.display.set_mode(screen_size)
        setMiddle(screen_size, monitor_size)
    elif mode == "big":
        rows = 12
        cols = 18
        screen_size = 951, 708
        screen = pygame.display.set_mode(screen_size)
        setMiddle(screen_size, monitor_size)
    elif mode == "fullscreen":
        screen_size = monitor_size
        cols = monitor_size[0] // side
        rows = monitor_size[1] // side - 2
        screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)

    startpos = (screen_size[0] - (cols*(side+SPC)-SPC))//2, (screen_size[1] - rows*(side+SPC)-SPC -(screen_size[0] - (cols*(side+SPC)-SPC))//2)
    print("startpos", startpos)
    print("monitor size is ", screen_size)

    global ms, bs, btwngp, text_font, retro_font, clean_bomb_font, clean_font, clean_time_font, clean_big_font, retro_big_font
    bs = 5 + screen_size[0] // 63 # button spacing
    ms = screen_size[0] // 6.5 # mid spacing
    btwngp = 3*bs #between button gap
    print("bs",bs, "ms",ms, "btwngp",btwngp)

    text_font = pygame.font.Font(None, screen_size[0] // 19)
    retro_font = pygame.font.Font(None, screen_size[0] // 23)
    retro_big_font = pygame.font.Font(None, screen_size[0] // 15)
    clean_bomb_font = pygame.font.SysFont("yugothic", screen_size[0] // 19) # yugothic
    clean_font = pygame.font.SysFont("simsun", screen_size[0] // 31, False, True)
    clean_time_font = pygame.font.SysFont("yugothic", screen_size[0] // 30)
    clean_big_font = pygame.font.SysFont("simsun", screen_size[0] // 20, False, True)

    changeTheme(THEME)

# loadStats()
changeTheme(THEME)
if not isMainMenu:
    screen.fill(BACKGROUND)
    create_grid(rows, cols, side, startpos)

def main():
    global running, gameActive, changeScreenSize
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if isMainMenu == True:
            mainMenu()
            if changeScreenSize == True:
                newScreen(screenMode)
        else:
            if gameActive == True:
                minesweeper()
            else:
                restartScreen()
        clock.tick(60)

main()
# saveStats()
