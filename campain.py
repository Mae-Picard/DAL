r = 25

import math
import random
import pyray as pr
import setup as s

in_menu = False
in_world = True
switching_stage = True

campain_stage = 0

maze = {}
N = r * 2
for i in range(-r, r + 1):
    for j in range(-r, r + 1):
        maze[(i, j)] = []
maze[(0, 0)].append((0, 1))  # /
maze[(0, 1)].append((1, 0))  # <  le joueur doit etre dans une de ces coordonées au départ
maze[(1, 0)].append((1, 1))  # \


def is_maze_filled():
    for c in maze:
        if len(maze[c]) == 0:
            return False
    return True


def rdm_walk(path):
    if len(maze[path[-1]]) > 0:
        return path
    prev_x, prev_y = path[-1]
    p = path.copy()  # Use a copy to avoid unintended mutations
    dx, dy = random.choice([(0, 1), (-1, 0), (1, 0), (0, -1)])
    new_pos = (prev_x + dx, prev_y + dy)
    if new_pos in maze:
        if new_pos not in path:
            p.append(new_pos)
        else:
            # Truncate the path to form a loop
            index = path.index(new_pos)
            p = path[:index + 1]
    return rdm_walk(p)


def gen_maze(offset_x, offset_y):
    global maze
    for _ in range(N):
        # Generate a starting cell within a safe inner area
        orig_coord = (random.randint(-r + 2 + offset_x, r - 2 + offset_x),
                      random.randint(-r + 2 + offset_y, r - 2 + offset_y))
        while len(maze[orig_coord]) > 0:
            orig_coord = (random.randint(-r + offset_x, r + offset_x), random.randint(-r + offset_y, r + offset_y))
        dx, dy = random.choice([(0, 1), (-1, 0), (1, 0), (0, -1)])
        line = [orig_coord]
        while len(line) < N // 2:
            tx, ty = line[-1]
            next_cell = (tx + dx, ty + dy)
            if next_cell not in maze:
                break  # Stop if out of bounds
            if len(maze[next_cell]) > 0:
                break  # Stop if cell is already connected
            # Add bidirectional connection
            maze[(tx, ty)].append(next_cell)
            maze[next_cell].append((tx, ty))
            line.append(next_cell)

    # Fill remaining areas
    while not is_maze_filled():
        orig_coord = (
        random.randint(-r + 2 + offset_x, r - 2 + offset_x), random.randint(-r + 2 + offset_y, r - 2 + offset_y))
        while len(maze[orig_coord]) > 0:
            orig_coord = (random.randint(-r + offset_x, r + offset_x), random.randint(-r + offset_y, r + offset_y))
        path = rdm_walk([orig_coord])
        for coord in path[1:]:
            prev_coord = orig_coord
        if coord not in maze[prev_coord]:
            maze[prev_coord].append(coord)
        maze[coord].append(prev_coord)
        orig_coord = coord


def add_maze_part(pos):
    global maze

    # Calculer les limites actuelles du labyrinthe
    coords = list(maze.keys())
    current_min_x = min(x for (x, y) in coords)
    current_max_x = max(x for (x, y) in coords)
    current_min_y = min(y for (x, y) in coords)
    current_max_y = max(y for (x, y) in coords)

    threshold = 10 # Distance pour déclencher l'expansion
    offset = (0, 0)
    x, y = int(pos[0] / s.wall_length), int(pos[1] / s.wall_length)

    # Déterminer la direction d'expansion
    if x >= current_max_x - threshold:
        offset = (current_max_x + r, current_max_y + r if y > 0 else current_min_y - r)
    elif x <= current_min_x + threshold:
        offset = (current_min_x - r, current_max_y + r if y > 0 else current_min_y - r)
    elif y >= current_max_y - threshold:
        offset = (current_max_x + r if x > 0 else current_min_x - r, current_max_y + r)
    elif y <= current_min_y + threshold:
        offset = (current_max_x + r if x > 0 else current_min_x - r, current_min_y - r)
    else:
        return False  # Pas près d'un bord

    # Créer une nouvelle section adjacente
    temp_maze = {}
    for i in range(-r, r + 1):
        for j in range(-r, r + 1):
            new_x = i + offset[0]
            new_y = j + offset[1]
            temp_maze[(new_x, new_y)] = []

    # Fusionner avec le labyrinthe existant
    original_maze = maze.copy()
    maze = temp_maze
    gen_maze(offset[0], offset[1])  # Générer les passages dans la nouvelle section
    maze.update(original_maze)  # Combiner les deux sections

    return True


def wall_pos_for_maze():
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


def create_maze():
    walls = wall_pos_for_maze()
    for pos, orientation in walls:
        # dépendant de la région ??
        model, color, refraction = (s.brickwall_model, s.brickwall_color, s.brickwall_refraction)

        s.Wall((pos[0] * s.wall_length, 1, pos[1] * s.wall_length), orientation,
               model, color, refraction, height=5)


def gen_campain(campain_stage):
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

    if campain_stage == 0:  # Mode labyrinthe
        # Création des murs
        gen_maze(0, 0)
        create_maze()
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
