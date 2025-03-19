import math
import random
from pyray import *
import campain
import setup as s

def shoot():
    global gun_frame, runFrames
    if s.gun.bullets > 0:
        runFrames = 1
        gun_frame = s.gun.frames[1]
        s.gun.bullets -= 1
        s.player.accels[0] -= s.gun.knockback / s.get_fps()
        s.y_player_offset += s.gun.knockback / 18
        s.fade_color = (220 + random.randint(-35, 35), 210 + random.randint(-20, 7), 155 + random.randint(-15, 45), 0)
        if s.gun.type == "main": _ = s.Bullet("main")
        elif s.gun.type == "riffle": _ = s.Bullet("riffle")


def update_fade_color():
    c1, c2, c3, _ = s.fade_color
    s.fade_color = (max(0, int(c1 / 1.06 - 5.1)), max(0, int(c2 / 1.06 - 5)), max(0, int(c3 / 1.06 - 4.9)), 255)


def draw_texture_hotbar():
    draw_texture(s.main_gun_2d_texture, mb_x - 260, mb_y - 100, (200, 210, 200, 255))
    if s.gun_hotbar[0]:
        draw_texture(s.riffle_gun_2d_texture, mb_x - 380, mb_y - 100, (250, 255, 255, 255))
    else:
        draw_texture(s.empty_slot_texture, mb_x - 360, mb_y - 90, (255, 255, 200, 255))
        
    if s.pickable_hotbar[0] == 0:
        draw_texture(s.empty_slot_texture, mb_x - 145, mb_y - 90, (210, 255, 230, 255))
    else:
        draw_texture(s.blocks_2d_texture, mb_x - 145, mb_y - 90, (255, 255, 255, 255))
        draw_text(str(s.pickable_hotbar[0]), mb_x - 140, mb_y - 86, 20, (0, 0, 0, 255))
        draw_text(str(s.pickable_hotbar[0]), mb_x - 140, mb_y - 90, 20, (255, 255, 255, 255))
        draw_text(str(s.pickable_hotbar[0]), mb_x - 140, mb_y - 88, 20, (255, 255, 0, 255))

    if s.pickable_hotbar[1] == 0:
        draw_texture(s.empty_slot_texture, mb_x - 35, mb_y - 90, (220, 255, 255, 255))
    else:
        draw_texture(s.mobs_2d_texture, mb_x - 35, mb_y - 100, (255, 255, 255, 255))
        draw_text(str(s.pickable_hotbar[1]), mb_x - 30, mb_y - 86, 20, (0, 0, 0, 255))
        draw_text(str(s.pickable_hotbar[1]), mb_x - 30, mb_y - 90, 20, (255, 255, 255, 255))
        draw_text(str(s.pickable_hotbar[1]), mb_x - 30, mb_y - 88, 20, (255, 255, 0, 255))

    if s.powerups_hotbar[0]:
        draw_texture(s.powerup_health_texture, mb_x + 70, mb_y - 100, (255, 200, 200, 255))
    else:
        draw_texture(s.empty_slot_texture, mb_x + 70, mb_y - 90, (255, 220, 230, 255))

    if s.powerups_hotbar[1]:
        draw_texture(s.powerup_speed_texture, mb_x + 185, mb_y - 100, (200, 255, 200, 255))
    else:
        draw_texture(s.empty_slot_texture, mb_x + 185, mb_y - 90, (200, 255, 180, 255))

    if s.powerups_hotbar[2]:
        draw_texture(s.powerup_damage_texture, mb_x + 300, mb_y - 100, (200, 200, 255, 255))
    else:
        draw_texture(s.empty_slot_texture, mb_x + 300, mb_y - 90, (200, 220, 255, 255))


def update_maze():
        xp, _, zp = s.player.pos
        # Generates the maze around the player
        if campain.add_chunck_maze(int(xp / s.wall_length), int(zp / s.wall_length)):
            campain.create_maze(campain.maze)
        # Summon monsters based on time spent in level
        l = len(s.mobs)
        if s.mob_strength < 2:
            for i in range(2):
                x = (random.choice([-1, 0, 1, 2]) - 0.5) * s.wall_length
                z = (random.choice([-1, 0, 1, 2]) - 0.5) * s.wall_length
                model, a, b, c = random.choice([(s.mob_model1, 1, 4, 2),
                                                (s.mob_model2, 3, 7, 4)])
                s.Mob((int(xp + x), 2, int(zp + z)), model, a, b, c)
        elif s.mob_strength < 5:
            for i in range(2):
                x = (random.choice([-2, -1, 0, 1 , 2, 3]) - 0.5) * s.wall_length
                z = (random.choice([-2, -1, 0, 1, 2, 3]) - 0.5) * s.wall_length
                model, a, b, c = random.choice([(s.mob_model1, 1, 4, 2),
                                                (s.mob_model2, 3, 7, 4),
                                                (s.mob_model3, 7, 5, 3)])
                s.Mob((int(xp + x), 2, int(zp + z)), model, a, b, c)
        elif s.mob_strength < 15:
            for i in range(3):
                x = (random.choice([-2, -1, 2, 3]) - 0.5) * s.wall_length
                z = (random.choice([-2, -1, 2, 3]) - 0.5) * s.wall_length
                model, a, b, c = random.choice([(s.mob_model1, 2, 5, 3),
                                                (s.mob_model2, 5, 9, 5),
                                                (s.mob_model3, 8, 8, 5),
                                                (s.mob_model4, 9, 10, 4)])
                s.Mob((int(xp + x), 2, int(zp + z)), model, a, b, c)
        elif s.mob_strength < 30:
            for i in range(5):
                x = (random.choice([-1, 2]) - 0.5) * s.wall_length
                z = (random.choice([-1, 2]) - 0.5) * s.wall_length
                model, a, b, c = random.choice([(s.mob_model1, 3, 5, 4),
                                                (s.mob_model2, 4, 9, 5),
                                                (s.mob_model3, 9, 8, 6),
                                                (s.mob_model4, 10, 11, 4),
                                                (s.mob_model5, 20, 5, 5)])
                s.Mob((int(xp + x), 2, int(zp + z)), model, a, b, c)
        else:
            for i in range(6):
                x = (random.choice([-2, -1, 0, 1, 2, 3]) - 0.5) * s.wall_length
                z = (random.choice([-2, -1, 0, 1, 2, 3]) - 0.5) * s.wall_length
                model, a, b, c = random.choice([(s.mob_model1, 3, 5, 4),
                                                (s.mob_model2, 6, 9, 5),
                                                (s.mob_model3, 10, 10, 7),
                                                (s.mob_model4, 10, 11, 5),
                                                (s.mob_model5, 25, 7, 6)])
                s.Mob((int(xp + x), 2, int(zp + z)), model, a, b, c)


runFrames = s.FPS * 2
selected_slot = 0
while not window_should_close():
    # ------------------------------------------------------------------------------------------------------------------
    # Gestion des paramètres liés au temps
    # ------------------------------------------------------------------------------------------------------------------
    if campain.in_world and campain.switching_stage:
        campain.gen_campain(campain.campain_stage)
        gun_frame = s.gun.frames[0]
        campain.switching_stage = False

    fps = abs(round(s.get_fps())) + 1
    runFrames += 1
    if runFrames >= fps * 60: runFrames = 1
    if s.gun.tick_after_shoot > 0: s.gun.tick_after_shoot += 1
    if s.gun.tick_after_shoot > 15: s.gun.tick_after_shoot = 0

    if not campain.in_menu:
        if runFrames % fps == 0:
            s.mob_strength += math.sqrt((1 + fps/1000) - 1 / s.mob_strength) / 16
            s.gun.bullets = min(14, s.gun.bullets + 2) if s.gun.type == "main" else min(26, s.gun.bullets + 5)

        sm = 121 * max([0.02, abs(s.player.movements[0]), abs(s.player.movements[1])])
        s.y_player_offset = math.sin(runFrames / fps * min(3, max(1, sm)) ** 2) / fps * sm / 4
        if campain.campain_stage == 0 and runFrames % (fps // 3 + 1) == 0: update_maze()

        if s.player.is_in_air: s.y_player_offset = 0
        if s.player.shield > 0: s.player.shield -= 1
        if s.player.is_dashing and s.player.dash_tick < (fps // 5 + 1):
            s.player.dash_tick += 1
            s.friction = 1 + (16 / (s.get_fps() // 3) * min(s.get_fps() // 3, s.player.dash_tick * 1.75)) / fps
        else: s.player.is_dashing = False
        update_fade_color()
        # --------------------------------------------------------------------------------------------------------------
        # Gestion des inputs utilisateurs
        # --------------------------------------------------------------------------------------------------------------
        if is_key_down(KeyboardKey.KEY_SPACE) and not s.player.is_in_air:
            s.player.accels[2] = .145
            s.player.movements[2] = -.025
        if is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT) and gun_frame == s.gun.frames[0]: shoot()
        if is_key_down(KeyboardKey.KEY_LEFT_CONTROL): s.player.is_sprinting = True
        elif is_key_released(KeyboardKey.KEY_LEFT_CONTROL): s.player.is_sprinting = False
        if is_key_pressed(KeyboardKey.KEY_LEFT_SHIFT) and not s.player.is_dashing and not s.player.is_in_air:
            s.player.is_dashing = True
            s.player.dash_tick = 0
        if is_key_down(KeyboardKey.KEY_Q) and gun_frame == s.gun.frames[0]:
            s.gun.switch()
            gun_frame = s.gun.frames[1]

    if is_key_pressed(KeyboardKey.KEY_TAB):
        set_mouse_position(0, 0)
        if campain.in_menu: disable_cursor()
        campain.in_menu = not campain.in_menu
        campain.in_world = not campain.in_world

    selected_slot += get_mouse_wheel_move()
    if selected_slot > 6: selected_slot = 4
    if selected_slot < 4: selected_slot = 6
    # ------------------------------------------------------------------------------------------------------------------
    # Affichage du monde
    # ------------------------------------------------------------------------------------------------------------------
    begin_drawing()
    clear_background((0, 0, 0, 255)) # Réinitalise l'écran pour dessiner par dessus
    if campain.in_world:
        s.player.update()
        begin_mode_3d(s.camera) # Début du mode 3D, ce qui y est dessiné est en 3D
        s.build_map()
        for b in s.bullets: b.draw_bullet()
        end_mode_3d() # Fin du monde
        # --------------------------------------------------------------------------------------------------------------
        # Affichage de l'interface utilisateur
        # --------------------------------------------------------------------------------------------------------------
        mb_x, mb_y = (s.sWidth // 2, s.sHeight) # Milieu bas de l'écran
        if runFrames % round(fps / s.gun.speed + 1) == 0:
            for i in range(1, s.gun.nb_frames):
                if gun_frame == s.gun.frames[i]:
                    gun_frame = s.gun.frames[(i + 1) % s.gun.nb_frames]
                    break

        for b in s.bullets: b.animate()
        draw_texture(gun_frame, mb_x + s.gun.offset - int(6 * get_mouse_delta().x + get_mouse_delta().y * 3) + int(70 * s.y_player_offset),
        mb_y - int(400 + 100 * s.y_player_offset) + int(get_mouse_delta().y * 5 + get_mouse_delta().x * 2) + 10,
        (200, 210, 150, 255))
        if s.gun.type == "main":
            drag = int(4 * get_mouse_delta().x) + 8 * (s.gun.tick_after_shoot // 4 - 2) ** 2
            draw_texture(s.flashlight_texture, -10 - drag // 2 + int(120 * s.y_player_offset),
            mb_y - int(400 + 130 * s.y_player_offset) + 3 * int(get_mouse_delta().y) + 250 - int(2 * s.player.roll) - drag,
            (200, 210, 150, 255))
        life = int(s.player.life)
        bullets = int(s.gun.bullets)
        for i in range(-(bullets >> 1), (bullets >> 1) + (bullets % 2)):
            draw_texture(s.UI_bullets_texture, mb_x + i * 32, mb_y - 160, (150 - i * 7, 100 + i * 7, 170 + i * 3, 200))
        for i in range(-(life >> 1), (life >> 1) + (life % 2)):
            draw_texture(s.UI_life_texture, mb_x + i * 32, mb_y - 170, (150 - i * 7, 100 + i * 7, 120 + i * 5, 200))


        draw_texture_hotbar()
        draw_texture(s.UI_base_layer_right, s.sWidth - 500, 0, (255, 210, 150, 255))
        draw_texture(s.UI_slot_texture, mb_x - 650 + int(selected_slot) * 112, mb_y - 215, (200, 210, 150, 255))
        draw_texture(s.UI_hotbar_texture, mb_x - 650, mb_y - 215, (200, 210, 150, 255))
        draw_texture(s.UI_indicators_texture, mb_x - 650, mb_y - 215, (200 * s.player.is_sprinting, 210, 150, 225))
        draw_texture(s.UI_crossair_texture, mb_x - int(get_mouse_delta().x), mb_y // 2, (200, 210, 150, 125))
        draw_text(f"Mob Strength : {int(s.mob_strength * 100) / 100}", s.sWidth - 300, 150, 30, RED)
        draw_text(f"Player Damage : {int(s.gun.dmg * (1 + 3 * math.sqrt(s.mob_strength)) * 10) / 100}", s.sWidth - 320, 120, 30, GREEN)
        draw_text(f"Player Speed : {int(s.player.speed * 800) / 100}", s.sWidth - 300, 90, 30, GREEN)
        draw_text(f"X : {s.player.pos[0]}", s.sWidth - 200, 10, 20, WHITE)
        draw_text(f"Y : {s.player.pos[1]}", s.sWidth - 200, 30, 20, LIGHTGRAY)
        draw_text(f"Z : {s.player.pos[2]}", s.sWidth - 200, 50, 20, WHITE)
        draw_fps(s.sWidth - 300, 10)
        draw_texture(s.FX_shadow_texture, 0, 0, BLACK)
    # --------------------------------------------------------------------------------------------------------------
    # Affichage du menu
    # --------------------------------------------------------------------------------------------------------------
    if campain.in_menu:
        mx, my = s.sWidth // 2, s.sHeight // 2
        for x in range(s.sWidth // 250):
            for y in range(s.sHeight // 250):
                draw_texture(s.menu_background, 750 * x, 750 * y, WHITE)

        mouse_x, mouse_y = get_mouse_position().x, -get_mouse_position().y + my + 128
        mouse_pos = ((int(mouse_x) >> 7) << 7, (int(mouse_y) >> 7) << 7)

        text_boxes = ["-| *quitter", "-| *nouvelle partie"]
        for i in range(2):
            draw_rectangle(50, my - i * 128, s.sWidth - 100, 120, (200, 100, 100, 50))
            draw_rectangle(55, my - i * 128 + 5, s.sWidth - 110, 110, (70, 15, 10, 255))
            draw_text(text_boxes[i], 65, my - i * 128 + 22, 80, DARKGRAY)
            draw_text(text_boxes[i], 65, my - i * 128 + 20, 80, BLACK)
        if mouse_pos[1] < 400 and mouse_pos[1] > -300:
            draw_rectangle(50, my - mouse_pos[1], s.sWidth - 100, 120, (255, 100, 100, 70))

        if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
            print(mouse_pos[1])
            if mouse_pos[1] == 384: pass # ??
            if mouse_pos[1] == 384: pass # !!
    # --------------------------------------------------------------------------------------------------------------
    end_drawing()

close_window()
