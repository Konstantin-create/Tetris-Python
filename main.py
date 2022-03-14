import pygame
from copy import deepcopy
from random import choice, randrange

W, H = 10, 20
TILE = 45
GAME_RES = W * TILE, H * TILE
RES = 750, 940
FPS = 30

pygame.init()

sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load("img\\icon.png"))

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]
figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figures_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)

field = [[0 for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 30, 2000
r = 0

bg = pygame.image.load('img\\bg.jpg').convert()
game_bg = pygame.image.load('img\\bg2.jpg').convert()

main_font = pygame.font.Font('font\\font.ttf', 65)
font = pygame.font.Font('font\\font.ttf', 45)

title_tetris = main_font.render('Tetris', True, pygame.Color('darkorange'))
title_score = font.render('Score: ', True, pygame.Color('green'))
title_record = font.render('Record: ', True, pygame.Color('purple'))
title_newrecord = main_font.render('New record', True, pygame.Color('white'))

get_color = lambda: (randrange(30, 255), randrange(30, 255), randrange(30, 255))
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()
score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 4: 1500, 5: 2000, 6: 2500, 7: 2800, 8: 3000,
          9: 3200, 10: 3500, 11: 3700, 12: 3900, 13: 4100, 14: 4300, 15: 4500, 16: 4700,
          17: 4900, 18: 5100, 19: 5300, 20: 5400, 21: 5600, 22: 5800, 23: 6000, 24: 6200,
          25: 6400, 26: 6600, 27: 6800, 28: 6900, 29: 7100, 30: 7200, 31: 7400, 32: 7600
          }

# music
playing = True
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
a1 = pygame.mixer.music.load('sounds\\bg_sound.ogg')
a3 = pygame.mixer.Sound('sounds\\end_game.ogg')
a4 = pygame.mixer.Sound('sounds\\score.ogg')
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.4)


def check_border():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')


def set_record(record, scpre):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))
    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)

    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True

    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_border():
            figure = deepcopy(figure_old)
            break
    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure_old)
        for i in range(4):
            figure[i].y += 1
            if not check_border():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 1000
                break
    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_border():
                figure = deepcopy(figure_old)
                break

    # check lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            lines += 1
            anim_speed += 3
            a4.play()

    # compute score
    score += scores[lines]
    # draw new record title
    if score != 0 and int(score) > int(record) and r == 0:
        sc.blit(title_newrecord, (20, 10))
        pygame.time.delay(300)
        r = 1

    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # draw figures
    for i in range(4):
        figures_rect.x = figure[i].x * TILE
        figures_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figures_rect)

    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figures_rect.x, figures_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figures_rect)

    # draw next figure
    for i in range(4):
        figures_rect.x = next_figure[i].x * TILE + 380
        figures_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figures_rect)
    # draw titles
    sc.blit(title_tetris, (485, -10))
    sc.blit(title_score, (535, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 840))
    sc.blit(title_record, (525, 650))
    sc.blit(font.render(record, True, pygame.Color('gold')), (550, 710))
    # game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            a3.play()
            field = [[0 for i in range(W)] for j in range(H)]
            anim_count, anim_speed, anim_limit = 0, 30, 2000
            score = 0
            r = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.update()
    clock.tick()
