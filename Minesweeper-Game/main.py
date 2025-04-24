import pygame
from pygame import Vector2
import random

pygame.init()

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
DARK_YELLOW = (189,108,8)
YELLOW = (247,204,46)
GRAY = (245,245,245)
background = (41, 40, 57)
menu_clr = (76, 82, 122)
cell_clr = (90, 180, 240)
cell_shadow = (28, 80, 135)
text_clr = {
    1: (42, 193, 227),
    2: (76, 175, 80),
    3: (255, 87, 51),
    4: (138, 43, 226),
    5: (255, 165, 0),
    6: (72, 61, 139),
    7: (169, 169, 169),
    8: (255, 0, 0)
}

cell_size = 50
n_cell = 8
menu_size = 50
margin = 40
gap = 5
bombs = 10

size = Vector2(n_cell*cell_size+2*margin+gap*(n_cell-1),n_cell*cell_size+2*margin+gap*(n_cell-1)+menu_size)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Minesweeper")

font = pygame.font.Font("freesansbold.ttf", 30)
flag = pygame.transform.smoothscale(pygame.image.load("assets/flag.png"),(cell_size-cell_size//2.5,cell_size-cell_size//2.5))
mine = pygame.transform.smoothscale(pygame.image.load("assets/mine.png"),(cell_size-cell_size//10,cell_size-cell_size//10))

class Game():
    def __init__(self):
        self.grid = [[self.Cell(x,y) for x in range(n_cell)] for y in range(n_cell)]
        self.won = False
        self.lost = False
        self.first_click = True
        self.num_bombs = bombs
        self.flag_count = 0

    def draw(self):
        # background
        screen.fill(background)
        # menu
        screen.fill(menu_clr, (0,0,size.x,menu_size))
        # squares
        for row in self.grid:
            for cell in row:
                x_pos = cell.x*(cell_size+gap)+margin
                y_pos = cell.y*(cell_size+gap)+margin+menu_size
                rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)
                shadow_rect = pygame.Rect(rect.x,rect.y,rect.w,rect.h-rect.h//10)
                if cell.is_open:
                    color = GRAY
                else:
                    color = DARK_YELLOW if cell.is_flag else cell_shadow
                # shadow square
                pygame.draw.rect(screen, color, rect, border_radius=4)
                if not cell.is_open:
                    # square
                    if cell.is_flag:
                        pygame.draw.rect(screen, YELLOW, shadow_rect, border_radius=4)
                    else:
                        pygame.draw.rect(screen, cell_clr, shadow_rect, border_radius=4)
                # outline
                pygame.draw.rect(screen, BLACK, rect, 1, border_radius=4)
                cell.show_text()
                cell.put_flag() 
                cell.show_mine()

    def place_bombs(self, row, col):
        positions = [(y,x) for x in range(n_cell) for y in range(n_cell) if (x,y) != (row,col)]
        random.shuffle(positions)
        for i in range(self.num_bombs):
            y,x = positions[i]
            self.grid[x][y].has_bomb = True
        self.set_nearby_bombs()
        if self.grid[row][col].nearby_bombs != 0:
            self.reset_game()
            self.place_bombs(row,col)

    def set_nearby_bombs(self):
        for row in self.grid:
            for cell in row:
                if cell.has_bomb:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            nx, ny = cell.x-i, cell.y-j
                            if (0 <= nx < n_cell and 0 <= ny < n_cell):
                                if not self.grid[ny][nx].has_bomb:
                                    self.grid[ny][nx].nearby_bombs += 1

    def reset_game(self):
        for i in self.grid:
            for j in i:
                j.has_bomb = False
                j.nearby_bombs = 0
                if not self.first_click:
                    j.is_flag = False
                j.is_open = False
        self.num_bombs = bombs
        self.flag_count = 0
        self.first_click = True

    def game_over(self):
        for i in self.grid:
            for j in i:
                if j.has_bomb:
                    j.is_open = True
                    j.is_flag = False

    def check_victory(self):
        non_bomb_cells_open = 0
        total_cell = n_cell*n_cell

        for row in self.grid:
            for cell in row:
                if cell.is_open and not cell.has_bomb:
                    non_bomb_cells_open += 1

        if non_bomb_cells_open == total_cell-self.num_bombs:
            self.won = True
            for row in self.grid:
                for cell in row:
                    if cell.has_bomb:
                        cell.is_flag = True

    def handle_click(self, r, c, button):
        if self.won or self.lost:
            if button == 1:
                self.won = False
                self.lost = False
                self.reset_game()
        elif not self.grid[r][c].is_open:
            if button == 3:
                if self.grid[r][c].is_flag:
                    self.grid[r][c].is_flag = False
                    self.flag_count -= 1
                else:
                    if self.flag_count<self.num_bombs:
                        self.grid[r][c].is_flag = True
                        self.flag_count += 1
            elif button == 1 and not self.grid[r][c].is_flag:
                if self.first_click:
                    self.place_bombs(r,c)
                    self.first_click = False
                self.grid[r][c].is_open = True
                if self.grid[r][c].has_bomb:
                    self.lost = True
                    self.game_over()
                elif self.grid[r][c].nearby_bombs == 0:
                    self.grid[r][c].open_neighbours(r,c)
                self.check_victory()

    class Cell():
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.is_open = False
            self.is_flag = False
            self.has_bomb = False
            self.nearby_bombs = 0
            self.text = None
            
        def show_text(self):
            if self.is_open and self.nearby_bombs>0:
                text = font.render(str(self.nearby_bombs), True, text_clr[self.nearby_bombs])
                screen.blit(text,text.get_rect(center = pygame.Rect(self.x*(cell_size+gap)+margin,
                                                                    self.y*(cell_size+gap)+margin+menu_size,cell_size,cell_size).center))
        def put_flag(self):
            if self.is_flag:
                screen.blit(flag,flag.get_rect(center = pygame.Rect(self.x*(cell_size+gap)+margin,
                                                                    self.y*(cell_size+gap)+margin+menu_size,cell_size,cell_size).center))
        def show_mine(self):
            if self.is_open and self.has_bomb:
                screen.blit(mine,mine.get_rect(center = pygame.Rect(self.x*(cell_size+gap)+margin,
                                                                    self.y*(cell_size+gap)+margin+menu_size,cell_size,cell_size).center))
        def open_neighbours(self,row,col):
            for i in range(-1,2):
                for j in range(-1,2):
                    nr, nc = row-i, col-j
                    if (0 <= nr < n_cell and 0 <= nc < n_cell):
                        if not game.grid[nr][nc].is_open and not game.grid[nr][nc].has_bomb:
                            game.grid[nr][nc].is_open = True
                            game.grid[nr][nc].is_flag = False
                            if game.grid[nr][nc].nearby_bombs == 0:
                                self.open_neighbours(nr,nc)

class Menu():
    def __init__(self):
        self.font = pygame.font.SysFont("Algerian",20) 
        pass

    def draw(self):
        if game.won:
            text = self.font.render("You won!", True, WHITE)
        elif game.lost:
            text = self.font.render("You lose!", True, WHITE)
        else:
            text = self.font.render("", True, WHITE)
        screen.blit(text,text.get_rect(center = pygame.Rect(0,0,size.x,menu_size).center))
        flag_text = self.font.render(str(game.num_bombs-game.flag_count), True, WHITE)
        screen.blit(flag_text,flag_text.get_rect(center = pygame.Rect(size.x-240,0,240,menu_size).center))
        small_flag = pygame.transform.smoothscale(pygame.image.load("assets/flag.png"),(25,23))
        screen.blit(small_flag, small_flag.get_rect(center = pygame.Rect(size.x-300,0,300,menu_size).center))

game = Game()
menu = Menu()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            row = (pos[1]-margin-menu_size)//(cell_size+gap)
            col = (pos[0]-margin)//(cell_size+gap)
            row = row if (pos[1]-margin-menu_size)%(cell_size+gap) < cell_size else -1
            col = col if (pos[0]-margin)%(cell_size+gap) < cell_size else -1
            if (row>=0 and row<n_cell) and (col>=0 and col<n_cell):
                game.handle_click(row,col,event.button)

    game.draw()
    menu.draw()

    pygame.display.update()
