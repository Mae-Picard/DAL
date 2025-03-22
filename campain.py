render_distance = 16
campain_stage = 0
maze = {}

import setup as s
import math
import random
import pyray as pr
import noise

in_menu = True
in_world = False
switching_stage = True
first_time = True


def initialize_maze():
    maze = {}
    for x, y in [(0, 0), (-16, 0), (0, -16), (-16, -16)]:
        maze = gen_empty_chunk(maze, x, y)
        maze = gen_maze_chunck(maze, x, y)
    return maze


def is_maze_filled(maze):
    for c in maze:
        if len(maze[c]) == 0:
            return False
    return True


def gen_lines_maze(maze, less_x, less_y):
    updated_maze = maze
    for _ in range(8):
        dx, dy = random.choice([(0, 1), (-1, 0), (1, 0), (0, -1)])
        t = 0
        flag = True
        orig_coord = (random.randrange(less_x + 2, less_x + 14), random.randrange(less_y + 2, less_y + 14))
        while flag and ((orig_coord not in updated_maze) or len(updated_maze[orig_coord]) > 0):
            orig_coord = (random.randrange(less_x, less_x + 16), random.randrange(less_y, less_y + 16))
            if t > 32: flag = False
            t += 1
        if flag:
            previous_cell = orig_coord
            ox, oy = orig_coord
            for i in range(1, 9):
                next_cell = (ox + dx * i, oy + dy * i)
                if next_cell not in updated_maze: break  # Stop if out of bounds
                updated_maze = connect_cells(updated_maze, previous_cell, next_cell)
                if len(updated_maze[next_cell]) > 0: break  # Stop if cell is already connected
                previous_cell = next_cell
    return updated_maze


def rdm_walk(maze, path):
    if len(maze[path[-1]]) > 0: return path
    x, y = path[-1]
    p = path.copy()  # Use a copy to avoid unintended mutations
    dx, dy = random.choice([(0, 1), (-1, 0), (1, 0), (0, -1)])
    new_pos = (x + dx, y + dy)
    if new_pos in maze:
        if new_pos not in path:
            p.append(new_pos)
        else:
            p = path[:path.index(new_pos) + 1]  # Truncate the path to form a loop
    return rdm_walk(maze, p)


def gen_paths_maze(maze, less_x, less_y):
    updated_maze = maze
    t2 = 0
    while not is_maze_filled(updated_maze) and t2 < 128:
        t = 0
        t2 += 1
        flag = True
        orig_coord = (random.randrange(less_x + 2, less_x + 14), random.randrange(less_y + 2, less_y + 14))
        while flag and ((orig_coord not in updated_maze) or len(updated_maze[orig_coord]) > 0):
            orig_coord = (random.randrange(less_x, less_x + 16), random.randrange(less_y, less_y + 16))
            if t > 32: flag = False
            t += 1
        if flag:
            path = rdm_walk(updated_maze, [orig_coord])
            previous_coord = orig_coord
            for coord in path[1:]:
                updated_maze = connect_cells(updated_maze, previous_coord, coord)
                previous_coord = coord
    return updated_maze


def gen_empty_chunk(maze, less_x, less_y):
    for x in range(16):
        for y in range(16):
            coords = (x + less_x, y + less_y)
            if not coords in maze:
                maze[(x + less_x, y + less_y)] = []
    return maze


def gen_maze_chunck(maze, less_x, less_y):
    # Fill the chunck
    updated_maze = maze
    updated_maze = gen_lines_maze(updated_maze, less_x, less_y)
    updated_maze = gen_paths_maze(updated_maze, less_x, less_y)
    return updated_maze


def connect_cells(maze, a, b):
    if a in maze and b in maze:
        if b not in maze[a]: maze[a].append(b)
        if a not in maze[b]: maze[b].append(a)
    return maze


def add_chunck_maze(player_x, player_y):
    global maze
    threshold = 20
    flag = True
    if (player_x + threshold, player_y) not in maze:
        new_less_x = (player_x + threshold >> 4) << 4
        new_less_y = (player_y >> 4) << 4
        flag = False
    elif (player_x - threshold, player_y) not in maze:
        new_less_x = (player_x - threshold >> 4) << 4
        new_less_y = (player_y >> 4) << 4
        flag = False
    if (player_x, player_y + threshold) not in maze:
        new_less_x = (player_x >> 4) << 4
        new_less_y = (player_y + threshold >> 4) << 4
        flag = False
    elif (player_x, player_y - threshold) not in maze:
        new_less_x = (player_x >> 4) << 4
        new_less_y = (player_y - threshold >> 4) << 4
        flag = False
    if flag: return False
    maze = gen_empty_chunk(maze, new_less_x, new_less_y)
    maze = gen_maze_chunck(maze, new_less_x, new_less_y)
    return True


def wall_pos_for_maze(maze):
    wall_pos = []
    for coord in maze:
        x, y = coord
        connections = maze[coord]
        if random.choice([True, False]):
            if (x, y + 1) not in connections:
                wall_pos.append((coord, "West"))
            elif (x - 1, y) not in connections:
                wall_pos.append((coord, "North"))
        else:
            if (x - 1, y) not in connections:
                wall_pos.append((coord, "North"))
            elif (x, y + 1) not in connections:
                wall_pos.append((coord, "West"))
    return wall_pos


def create_maze(maze):
    for pos in s.blocks.copy():
        x, _, z = pos
        px, _, pz = s.player.pos
        if (abs(x - px) // s.wall_length) * s.wall_length + \
                (abs(z - pz) // s.wall_length) * s.wall_length > 3 * render_distance:
            del s.blocks[pos]
    for pos in s.paintings.copy():
        x, _, z = pos
        px, _, pz = s.player.pos
        if (abs(x - px) // s.wall_length) * s.wall_length + \
                (abs(z - pz) // s.wall_length) * s.wall_length > 3 * render_distance:
            del s.paintings[pos]
    walls = wall_pos_for_maze(maze)

    # Paramètres pour le bruit de Perlin
    scale = 0.01  # Le facteur d'échelle du bruit
    octaves = 4  # Le nombre d'octaves du bruit de Perlin
    persistence = 0.5  # La persistance du bruit
    lacunarity = 2.0  # La lacunarity du bruit

    for pos, orientation in walls:
        x, y = pos[0], pos[1]
        # Calcul du bruit de Perlin à partir des coordonnées (x, y)
        perlin_noise_value = noise.pnoise2(x * scale, y * scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
        # Définir la couleur du mur en fonction de la valeur du bruit
        if perlin_noise_value < -0.2:
            model, color, refraction = (s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        elif perlin_noise_value < 0.0:
            model, color, refraction = (s.white_wall_model, s.white_wall_color, s.white_wall_refraction)
        elif perlin_noise_value < 0.1:
            model, color, refraction = (s.red_wall_model, s.red_wall_color, s.red_wall_refraction)
        else:
            model, color, refraction = (s.brickwall_model, s.brickwall_color, s.brickwall_refraction)
        # Création du mur avec la couleur déterminée
        s.Wall((x * s.wall_length, 1, y * s.wall_length), orientation, model, color, refraction, height=5)


def gen_campain(campain_stage):
    global maze
    if campain_stage == -1:  # Mode test
        # Création des murs
        s.Wall((1, 1, 0), "North", s.white_wall_model, s.white_wall_color, s.white_wall_refraction)
        s.Wall((6, 1, 0), "North", s.brickwall_model, s.brickwall_color, s.brickwall_refraction)
        # Création des platformes
        s.Floor((10, 3, 7), 3, 4, s.brickwall_model, s.brickwall_color, s.brickwall_refraction)
        s.Floor((3, 1, 5), 3, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # Pose des blocs
        s.Block((8, 1, 6), s.red_wall_model, s.red_wall_color, s.red_wall_refraction)
        # Ajout des monstres monstrueux
        s.Mob((10, 2, 2), s.mob_model1, 3, 4, 3)
        s.Mob((12, 2, 5), s.mob_model2, 4, 8, 6)
        s.Mob((15, 2, 10), s.mob_model3, 8, 5, 5)
        # Ajout des items
        s.Item((5, 2, 8), s.woodenwall_model, "Block")
        # Séléction de l'arme
        s.gun = s.Gun(s.main_gun_frames, 12, 7, -100, "main")  # arme principale
        s.gun_hotbar = [True, True]

    if campain_stage == 0:  # Mode labyrinthe
        # Création des murs
        maze = initialize_maze()
        create_maze(maze)
        # Séléction de l'arme
        s.gun = s.Gun(s.main_gun_frames, 12, 7, -100, "main")  # arme principale

    if campain_stage == 1:
        # Weapon
        s.gun = s.Gun(s.main_gun_frames, 12, 7, -100, "main")  # arme principale

        # 1st Room Walls
        s.Wall((11, 1, -11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=23)
        s.Wall((-11, 1, -11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=23)
        s.Wall((-11, 1, -11), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=23)
        s.Wall((3, 1, 11), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-10, 1, 11), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        # 1st Room Ground
        s.Floor((0, 0, 0), 21, 21, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 1st Corridor
        s.Wall((-3, 1, 11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=10)
        s.Wall((3, 1, 11), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=10)
        s.Floor((0, 0, 16), 5, 10, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # 2nd Room Walls
        s.Wall((8, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=19)
        s.Wall((-33, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=19)
        s.Wall((3, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=5)
        s.Wall((-33, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=31)
        s.Wall((-25, 1, 38), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=33)
        s.Wall((-32, 1, 38), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=2)
        # 2nd Room Ground
        s.Floor((-13, 0, 29), 41, 17, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 2nd Corridor
        s.Wall((-31, 1, 39), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=6)
        s.Wall((-25, 1, 39), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=11)
        s.Wall((-43, 1, 50), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=19)
        s.Wall((-43, 1, 44), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=13)
        s.Floor((-28, 0, 44), 5, 12, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-36, 0, 47), 15, 5, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # 3rd Room
        s.Wall((-59, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=17)
        s.Wall((-59, 1, 60), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=17)
        s.Wall((-43, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=25)
        s.Wall((-43, 1, 51), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=9)
        s.Wall((-59, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-59, 1, 33), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=28)
        # 3rd Room Ground
        s.Floor((-51, 0, 41), 17, 40, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 3rd Corridor
        s.Wall((-66, 1, 27), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-66, 1, 33), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Floor((-62, 0, 30), 8, 5, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # 4th Room Walls
        s.Wall((-66, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=8)
        s.Wall((-66, 1, 33), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=28)
        s.Wall((-107, 1, 20), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=41)
        s.Wall((-107, 1, 61), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=41)
        s.Wall((-107, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=15)
        s.Wall((-87, 1, 20), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=21)
        # 4th Room Ground
        s.Floor((-87, 0, 41), 41, 41, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        # 4th Corridor (with stairs)
        s.Floor((-90, 0, 19), 5, 4, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 1, 15), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 2, 12), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 3, 9), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Wall((-87, 1, 8), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=12, length=12)
        s.Wall((-93, 1, 8), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=12, length=12)
        # stairs roof
        s.Floor((-90, 8, 19), 5, 4, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 9, 15), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 10, 12), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)
        s.Floor((-90, 11, 9), 5, 3, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # Final Room
        s.Wall((-87, 3, 8), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=60)
        s.Wall((-107, 3, 8), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=15)
        s.Wall((-107, 3, -30), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=80)
        s.Wall((-107, 3, -30), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=38)
        s.Wall((-27, 3, -30), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=8, length=38)
        # Final Room Ground
        s.Floor((-67, 3, -11), 80, 38, s.woodenwall_model, s.woodenwall_color, s.woodenwall_refraction)

        # Maze 1st Room
        s.Wall((-8, 1, -8), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-8, 1, -2), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=4)
        s.Wall((-5, 1, 0), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((0, 1, -5), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((2, 1, -3), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=4)
        s.Wall((4, 1, 0), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-2, 1, 5), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-6, 1, 2), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((5, 1, -6), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((6, 1, -2), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((2, 1, 0), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((4, 1, 1), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-2, 1, 4), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-6, 1, 3), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((5, 1, -4), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((6, 1, -1), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)

        # Maze 2nd Room
        s.Wall((-30, 1, 24), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-25, 1, 26), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-20, 1, 30), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-10, 1, 34), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((0, 1, 36), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-10, 1, 28), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-5, 1, 31), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-15, 1, 38), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=7)
        s.Wall((-28, 1, 32), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((-10, 1, 24), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((0, 1, 26), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-5, 1, 21), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-15, 1, 28), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=7)
        s.Wall((-28, 1, 22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)

        # Maze 3rd Room
        s.Wall((-58, 1, 45), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-55, 1, 48), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-50, 1, 40), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-48, 1, 55), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=7)
        s.Wall((-46, 1, 58), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((-52, 1, 62), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-55, 1, 70), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-47, 1, 66), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((-45, 1, 72), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((-58, 1, 40), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=1, length=4)
        s.Wall((-58, 1, 34), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=3, length=4)
        s.Wall((-55, 1, 38), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-50, 1, 40), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-48, 1, 45), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=7)
        s.Wall((-58, 1, 30), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-55, 1, 28), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-50, 1, 40), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-48, 1, 35), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=7)
        s.Wall((-46, 1, 38), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((-52, 1, 32), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-55, 1, 40), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-47, 1, 36), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)
        s.Wall((-45, 1, 42), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=5)

        # Maze 4th Room
        s.Wall((-100, 1, 35), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-93, 1, 38), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-85, 1, 44), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=18)
        s.Wall((-75, 1, 48), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-90, 1, 52), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-97, 1, 57), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-83, 1, 64), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-87, 1, 66), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-85, 1, 34), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=18)
        s.Wall((-75, 1, 38), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-90, 1, 42), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-97, 1, 47), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-83, 1, 54), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-87, 1, 56), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-75, 1, 38), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-90, 1, 32), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-97, 1, 37), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=8)
        s.Wall((-83, 1, 54), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-87, 1, 36), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=6)
        s.Wall((-85, 1, 24), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=25)
        s.Wall((-90, 1, 22), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-75, 1, 22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=2, length=10)
        s.Wall((-95, 1, 22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=2, length=10)
        s.Wall((-68, 1, 25), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=2, length=10)

        # Maze Final Room
        s.Wall((-100, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=25)
        s.Wall((-75, 4, -15), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-85, 4, -5), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=20)
        s.Wall((-65, 4, -10), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-55, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-45, 4, -5), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-90, 4, -18), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-70, 4, -22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-70, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=25)
        s.Wall((-45, 4, -15), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-55, 4, -5), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=20)
        s.Wall((-35, 4, -10), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-25, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-15, 4, -5), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-60, 4, -18), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-40, 4, -22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)

        s.Wall((-50, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=25)
        s.Wall((-25, 4, -15), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-35, 4, -5), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=20)
        s.Wall((-15, 4, -10), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-25, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-15, 4, -5), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-40, 4, -18), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-20, 4, -22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-85, 4, -10), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=15)
        s.Wall((-95, 4, -25), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-90, 4, -5), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=12)
        s.Wall((-100, 4, -18), "North", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        s.Wall((-93, 4, -22), "West", s.red_wall_model, s.red_wall_color, s.red_wall_refraction, height=5, length=10)
        # Mobs 1st Room
        s.Mob((-5, 2, 5), s.mob_model1, 1, 1, 3)
        s.Mob((5, 2, -5), s.mob_model3, 1, 1, 4)
        s.Mob((-8, 2, 8), s.mob_model2, 2, 2, 4)
        s.Mob((8, 2, -8), s.mob_model1, 1, 2, 3)
        s.Mob((-3, 2, -3), s.mob_model3, 2, 3, 4)
        s.Mob((3, 2, 3), s.mob_model2, 2, 2, 4)
        s.Mob((-6, 2, -6), s.mob_model1, 1, 2, 3)
        s.Mob((6, 2, 6), s.mob_model3, 2, 3, 4)
        s.Mob((0, 2, -8), s.mob_model2, 2, 2, 4)

        # Mobs 2nd Room
        s.Mob((-10, 2, 20), s.mob_model1, 3, 4, 3)
        s.Mob((-15, 2, 25), s.mob_model3, 3, 5, 4)
        s.Mob((-5, 2, 30), s.mob_model2, 4, 6, 4)
        s.Mob((-20, 2, 35), s.mob_model1, 3, 4, 3)
        s.Mob((-8, 2, 28), s.mob_model3, 3, 5, 4)
        s.Mob((-12, 2, 32), s.mob_model2, 4, 6, 4)
        s.Mob((-18, 2, 24), s.mob_model1, 3, 4, 3)
        s.Mob((-3, 2, 22), s.mob_model2, 3, 6, 4)
        s.Mob((-25, 2, 29), s.mob_model3, 4, 5, 4)
        s.Mob((-13, 2, 37), s.mob_model2, 3, 6, 4)
        s.Mob((-7, 2, 35), s.mob_model5, 4, 6, 2)
        s.Mob((-29, 2, 23), s.mob_model5, 4, 6, 2)

        # Mobs 3rd Room
        s.Mob((-50, 2, 40), s.mob_model3, 8, 5, 4)
        s.Mob((-55, 2, 45), s.mob_model1, 3, 4, 3)
        s.Mob((-48, 2, 50), s.mob_model2, 4, 8, 6)
        s.Mob((-52, 2, 55), s.mob_model1, 3, 4, 3)
        s.Mob((-46, 2, 58), s.mob_model3, 8, 5, 4)
        s.Mob((-53, 2, 62), s.mob_model2, 4, 8, 4)
        s.Mob((-49, 2, 66), s.mob_model1, 3, 4, 3)
        s.Mob((-56, 2, 70), s.mob_model2, 4, 8, 4)
        s.Mob((-51, 2, 74), s.mob_model3, 8, 5, 4)
        s.Mob((-47, 2, 78), s.mob_model2, 4, 8, 4)
        s.Mob((-57, 2, 59), s.mob_model5, 4, 8, 2)
        s.Mob((-43, 2, 37), s.mob_model5, 4, 8, 2)

        # Mobs 4th Room
        s.Mob((-85, 2, 43), s.mob_model1, 3, 4, 3)
        s.Mob((-80, 2, 47), s.mob_model2, 4, 8, 4)
        s.Mob((-75, 2, 51), s.mob_model3, 8, 5, 2)
        s.Mob((-70, 2, 55), s.mob_model5, 4, 8, 3)
        s.Mob((-65, 2, 59), s.mob_model1, 3, 4, 2)
        s.Mob((-60, 2, 63), s.mob_model5, 4, 8, 2)
        s.Mob((-55, 2, 67), s.mob_model3, 8, 5, 4)
        s.Mob((-50, 2, 71), s.mob_model5, 4, 8, 2)
        s.Mob((-70, 2, 77), s.mob_model1, 3, 4, 3)
        s.Mob((-60, 2, 79), s.mob_model2, 4, 8, 4)
        s.Mob((-80, 2, 41), s.mob_model5, 4, 8, 2)
        s.Mob((-104, 2, 54), s.mob_model5, 4, 8, 2)
        s.Mob((-92, 2, 58), s.mob_model5, 4, 8, 2)
        s.Mob((-88, 2, 39), s.mob_model5, 4, 8, 2)
        s.Mob((-96, 2, 25), s.mob_model5, 4, 8, 2)
        s.Mob((-106, 2, 26), s.mob_model5, 4, 8, 2)

        # Mobs Final Room
        s.Mob((-88, 5, -8), s.mob_model1, 3, 4, 3)
        s.Mob((-104, 5, 1), s.mob_model2, 4, 8, 4)
        s.Mob((-92, 5, -9), s.mob_model3, 8, 5, 2)
        s.Mob((-96, 5, -21), s.mob_model5, 4, 8, 3)
        s.Mob((-103, 5, -27), s.mob_model1, 3, 4, 2)
        s.Mob((-29, 5, -26), s.mob_model5, 4, 8, 2)
        s.Mob((-29, 5, -27), s.mob_model5, 4, 8, 2)
        s.Mob((-67, 5, -6), s.mob_model5, 4, 8, 2)
        s.Mob((-62, 5, -1), s.mob_model3, 8, 5, 4)
        s.Mob((-48, 5, 1), s.mob_model5, 4, 8, 2)
        s.Mob((-39, 5, -1), s.mob_model1, 3, 4, 3)
        s.Mob((-28, 5, -2), s.mob_model2, 4, 8, 4)
        s.Mob((-32, 5, -2), s.mob_model5, 4, 8, 2)
        s.Mob((-32, 5, 1), s.mob_model5, 4, 8, 2)
        s.Mob((-29, 5, 1), s.mob_model5, 4, 8, 2)

        # Final Boss Spawn
        s.Mob((-33, 7, -11), s.mob_model4, 3, 50, 4)