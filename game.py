#   NAME:           Alex van Weezendonk
#   COMPUTING ID:   txs5rd
#   NAME:           Andy Thepvongs
#   COMPUTING ID:   htf6dp

#Description of your game
'''
A 2-player "Asteroids" style game in which both players control their own ship and shoot at asteroids while floating in space.

Each player must score as many points as possible within a designated time limit. Hitting asteroids that drift across the screen as well as other targets will earn the player points.

When asteroids are hit, they will break into smaller chunks, each of which provides an additional obstacle to the player, but also a potential to score more points by shooting them.

Player death (hitting an asteroid or being shot by the other player) shall be penalized via a respawn timer, during which the other player will be able to continue playing and score additional points.

At the end of the time interval, the game ends, with the point totals of both players being finalized and compared to determine the winner. The final score of the winner is then compared to the high score record saved in a separate file. If the winner
s score is higher than the high score record, the high score record is updated.
'''

#List of the 3 basic features and how you will incorporate each one
'''
User Input - The red ship is controlled using the "WAD" keys and shoots using the "1" key, while the blue ship is controlled using the "up/left/right" keys and shoots using the "," key.

Game Over - A game over screen is displayed at the end of the time interval, with the point totals of both players being finalized and compared to determine the winner. After reacbing the end screen, users can restart the game by pressing the "R" key.

Graphics and Images - Graphics and images will be used to display game information, asteroids, ships, bullets.
'''
#List of 4 additional features and how you will incorporate each one
''' 
Restart from Game Over - When "Game Over" is displayed, users can restart the game by pressing the "R" key. 

Sprite Animation - Player ships have thruster animations that display when they are moving, and an explosion animation when they come into contact with an asteroid or bullet.

Enemies - Asteroids work as the "enemies" and obstruct player ships. If an asteroid hits a player, they are penalized with a respawn timer, which prevents the player from continuing play and scoring additional points until after they have respawned. However, once they respawn, they are given a short period of spawn protection.

Timer - A 60 second countdown is displayed at the top of the screen, and will display the time remaining until the game ends and player scores are finalized and compared.

Two players simultaneously - Two players can control an individual red or blue ship, with different movement and fire controls that are suited to their spawn/respawn location.
'''

import uvage
import math

import random

# resets highscore when game is run, commented out to prevent highscore overwrite
'''highscore = open("highscore.txt", "w")
highscore.write("0")
highscore.close()'''

camera_width = 800
camera_height = 600
camera = uvage.Camera(camera_width, camera_height)
game_on = True
game_reset_time = 1800
game_length = game_reset_time

# setup for asteroids
asteroid_count = 5
med_asteroid_multi = 2
small_asteroid_multi = 2

large_asteroids_list = []
med_asteroids_list = []
small_asteroids_list = []
asteroids = [large_asteroids_list, med_asteroids_list, small_asteroids_list]

asteroid_respawn_available = False

# creates large asteroid objects
for asteroid in range(asteroid_count):
    large_asteroids_list.append(uvage.from_image(500, 500, 'assets/large_asteroid.png'))
    large_asteroids_list[asteroid].scale_by(0.15)

    large_asteroids_list[asteroid].rotation = 0
    while abs(large_asteroids_list[asteroid].rotation) < 1:
        large_asteroids_list[asteroid].rotation = (random.random() * 1.5) * random.randrange(-1, 2, 2)

    large_asteroids_list[asteroid].speedx = (random.random() * 2) * random.randrange(-1, 2, 2)
    large_asteroids_list[asteroid].speedy = (random.random() * 2) * random.randrange(-1, 2, 2)
    large_asteroids_list[asteroid].x = random.randint(0, camera_width)
    large_asteroids_list[asteroid].y = random.randint(0, camera_height)

    large_asteroids_list[asteroid].isalive = True
    large_asteroids_list[asteroid].justgotshot = False

# creates medium asteroid objects
for item in range(med_asteroid_multi * asteroid_count):

    med_asteroids_list.append(uvage.from_image(500, -500, 'assets/med_asteroid.png'))
    med_asteroids_list[item].scale_by(0.15)

    med_asteroids_list[item].rotation = 0
    while abs(med_asteroids_list[item].rotation) < 1:
        med_asteroids_list[item].rotation = (random.random() * 3) * random.randrange(-1, 2, 2)

    med_asteroids_list[item].isalive = False
    med_asteroids_list[item].justgotshot = False

# creates small asteroid objects
for rock in range(small_asteroid_multi * med_asteroid_multi * asteroid_count):

    small_asteroids_list.append(uvage.from_image(500, -500, 'assets/small_asteroid.png'))
    small_asteroids_list[rock].scale_by(0.03)

    small_asteroids_list[rock].rotation = 0
    while abs(small_asteroids_list[rock].rotation) < 1.5:
        small_asteroids_list[rock].rotation = (random.random() * 4) * random.randrange(-1, 2, 2)

    small_asteroids_list[rock].isalive = False
    small_asteroids_list[rock].justgotshot = False

#   setup for team red
red_images = uvage.load_sprite_sheet("assets/team red.png", 1, 18)
red = uvage.from_image(225, camera_height / 2, red_images[0])
red_rotation = 0

red.total_speed = 0
red.speedx = 0
red.speedy = 0
red_frame = 0
red.scale_by(0.5)
red_isalive = True
red_invincible = True
red_invincible_counter = 0
red_points = 0

# setup for team blue
blue_images = uvage.load_sprite_sheet("assets/team blue.png", 1, 18)
blue = uvage.from_image(camera_width - 225, camera_height / 2, blue_images[0])
blue_rotation = 180
blue.total_speed = 0
blue.speedx = 0
blue.speedy = 0
blue_frame = 0
blue.scale_by(0.5)
blue_isalive = True
blue_invincible = True
blue_invincible_counter = 0
blue_points = 0

speed_modifier = 0.55
max_speed = 600

#   setup for bullets
bullet_lifetime = 30
bullet_speed = 20
bullet_max = 4

red_shooting = False
blue_shooting = False
red_bullets = []
blue_bullets = []

for i in range(bullet_max):
    red_bullets.append(uvage.from_color(-500, 0, 'white', 5, 5))
    red_bullets[i].lifetime = bullet_lifetime
    red_bullets[i].isalive = False

    blue_bullets.append(uvage.from_color(-500, 0, 'white', 5, 5))
    blue_bullets[i].lifetime = bullet_lifetime
    blue_bullets[i].isalive = False


# setup for game restart when "R" is selected during end game screen
def reset():
    global game_length, red_isalive, red_invincible, red_invincible_counter, red_points, red_frame, blue_isalive, blue_invincible, blue_invincible_counter, blue_points, blue_frame
    # game length = seconds*frames per second = seconds*30
    game_length = game_reset_time

    red_isalive = True
    red_invincible = True
    red_invincible_counter = 0
    red_points = 0
    red_frame = 0
    red.x = 225
    red.y = camera_height / 2
    red.speedx = 0
    red.speedy = 0

    blue_isalive = True
    blue_invincible = True
    blue_invincible_counter = 0
    blue_points = 0
    blue_frame = 0
    blue.x = camera_width - 225
    blue.y = camera_height / 2
    blue.total_speed = 0
    blue.speedx = 0
    blue.speedy = 0

    for item in asteroids:
        for rock in item:
            rock.isalive = False
    for rock in small_asteroids_list:
        rock.x = 500
        rock.y = -500
    for rock in med_asteroids_list:
        rock.x = 500
        rock.y = -500


#setup for red's controls
def red_movement():
    global red_rotation, red_frame, speed_modifier, max_speed
    red_boosters_on = False
    if red_isalive:
        #   right turning input
        if uvage.is_pressing("d"):
            current_rotation = -8
            red_rotation += -8
        #   left turning input
        elif uvage.is_pressing("a"):
            current_rotation = 8
            red_rotation += 8
        #   sets current_rotation = 0 if player has no rotation input for the tick
        else:
            current_rotation = 0

        #   thruster input
        if uvage.is_pressing("w"):
            #  checks red speed to prevent it going above max_speed
            if ((red.speedx * red.speedx) + (red.speedy * red.speedy)) < max_speed:
                #   adds the components of speed_modifier in the x and y directions to red speed
                red.speedx += speed_modifier * math.cos((red_rotation * math.pi) / 180)
                red.speedy -= speed_modifier * math.sin((red_rotation * math.pi) / 180)

            red_boosters_on = True

        #   reduces the speed every tick by 2%
        red.speedx *= 0.98
        red.speedy *= 0.98
        #   sets speed to 0 if below a very small value (0.001)
        if ((red.speedx * red.speedx) + (red.speedy * red.speedy)) < 0.001:
            red.speedx = 0
            red.speedy = 0

        #   moves through the sprites for the thrust flames when boosters on
        if red_boosters_on:
            red_frame += 1
            if red_frame >= 8:
                red.image = red_images[1]
            if red_frame >= 16:
                red_frame = 1
                red.image = red_images[2]
        #   changes the sprite back to the one without flames when boosters off
        else:
            red.image = red_images[0]
        camera.draw(red)

        #   moves and rotates the player based on inputs during this tick
        red.move_speed()
        red.rotate(current_rotation)

        #   movement across edges in x
        if red.x < -15:
            red.x = camera_width + 15
        elif red.x > camera_width + 15:
            red.x = -15

        #   movement across edges in y
        if red.y < -15:
            red.y = camera_height + 15
        elif red.y > camera_height + 15:
            red.y = -15


def blue_movement():
    global blue_rotation, blue_frame, speed_modifier, max_speed
    blue_boosters_on = False

    if blue_isalive:
        #   right turning input
        if uvage.is_pressing("right arrow"):
            current_rotation = -8
            blue_rotation += -8
        #   left turning input
        elif uvage.is_pressing("left arrow"):
            current_rotation = 8
            blue_rotation += 8
        #   sets current_rotation = 0 if player has no rotation input for the tick
        else:
            current_rotation = 0

        #   thruster input
        if uvage.is_pressing("up arrow"):
            #  checks blue speed to prevent it going above max_speed
            if ((blue.speedx * blue.speedx) + (blue.speedy * blue.speedy)) < max_speed:
                #   adds the components of speed_modifier in the x and y directions to blue speed
                blue.speedx += speed_modifier * math.cos(
                    (blue_rotation * math.pi) / 180)
                blue.speedy -= speed_modifier * math.sin(
                    (blue_rotation * math.pi) / 180)

            blue_boosters_on = True

        #   reduces the speed every tick by 2%
        blue.speedx *= 0.98
        blue.speedy *= 0.98
        #   sets speed to 0 if below a very small value (0.001)
        if ((blue.speedx * blue.speedx) + (blue.speedy * blue.speedy)) < 0.001:
            blue.speedx = 0
            blue.speedy = 0

        #   moves through the sprites for the thrust flames when boosters on
        if blue_boosters_on:
            blue_frame += 1
            if blue_frame >= 8:
                blue.image = blue_images[1]
            if blue_frame >= 16:
                blue_frame = 1
                blue.image = blue_images[2]
        #   changes the sprite back to the one without flames when boosters off
        else:
            blue.image = blue_images[0]
        camera.draw(blue)

        #   moves and rotates the player based on inputs during this tick
        blue.move_speed()
        blue.rotate(current_rotation)

        #   movement across edges in x
        if blue.x < -15:
            blue.x = camera_width + 15
        elif blue.x > camera_width + 15:
            blue.x = -15

        #   movement across edges in y
        if blue.y < -15:
            blue.y = camera_height + 15
        elif blue.y > camera_height + 15:
            blue.y = -15


def red_projectiles():
    global red_shooting

    #   fires when player is not holding space and presses space
    if uvage.is_pressing('1') and not red_shooting:
        red_shooting = True

        for item in range(len(red_bullets)):
            if not red_bullets[item].isalive:
                red_bullets[item].x = red.x
                red_bullets[item].y = red.y
                red_bullets[item].speedx = red.speedx + bullet_speed * math.cos((red_rotation * math.pi) / 180)
                red_bullets[item].speedy = red.speedy - bullet_speed * math.sin((red_rotation * math.pi) / 180)
                red_bullets[item].isalive = True
                red_bullets[item].lifetime = bullet_lifetime
                break

    #   tests to prevent holding space for rapid fire
    elif not uvage.is_pressing('1'):
        red_shooting = False

    #   decreases bullet.lifetime for each tick bullet is alive
    for item in red_bullets:
        if item.lifetime > 0:
            item.lifetime -= 1
        else:
            item.isalive = False

    #   bullet despawning at end of lifetime
    for item in red_bullets:
        if item.isalive:
            item.move_speed()

            if item.x < -15:
                item.x = camera_width + 15
            elif item.x > camera_width + 15:
                item.x = -15

            #   movement across edges in y
            if item.y < -15:
                item.y = camera_height + 15
            elif item.y > camera_height + 15:
                item.y = -15

        else:
            item.x = -500
            item.y = 0


def blue_projectiles():
    global blue_shooting
    if uvage.is_pressing('comma') and not blue_shooting:
        blue_shooting = True

        for item in range(len(blue_bullets)):
            if not blue_bullets[item].isalive:
                blue_bullets[item].x = blue.x
                blue_bullets[item].y = blue.y
                blue_bullets[item].speedx = blue.speedx + bullet_speed * math.cos((blue_rotation * math.pi) / 180)
                blue_bullets[item].speedy = blue.speedy - bullet_speed * math.sin((blue_rotation * math.pi) / 180)
                blue_bullets[item].isalive = True
                blue_bullets[item].lifetime = bullet_lifetime
                break

    #   tests to prevent holding space for rapid fire
    elif not uvage.is_pressing('comma'):
        blue_shooting = False

    #   decreases bullet.lifetime for each tick bullet is alive
    for item in blue_bullets:
        if item.lifetime > 0:
            item.lifetime -= 1
        else:
            item.isalive = False

    #   bullet despawning at end of lifetime
    for item in blue_bullets:
        if item.isalive:
            item.move_speed()

            if item.x < -15:
                item.x = camera_width + 15
            elif item.x > camera_width + 15:
                item.x = -15

            #   movement across edges in y
            if item.y < -15:
                item.y = camera_height + 15
            elif item.y > camera_height + 15:
                item.y = -15

        else:
            item.x = -500
            item.y = 0


def asteroid_control():
    for item in asteroids:

        for rock in item:

            if rock.isalive:
                rock.move_speed()
                rock.rotate(rock.rotation)

                if rock.x < -25:
                    rock.x = camera_width + 25
                elif rock.x > camera_width + 25:
                    rock.x = -25

                #   movement across edges in y
                if rock.y < -25:
                    rock.y = camera_height + 25
                elif rock.y > camera_height + 25:
                    rock.y = -25


def collision_control():
    global med_asteroid_multi, small_asteroid_multi, red_points, blue_points, red_isalive, blue_isalive

    #   asteroid splitting
    for item in asteroids:
        for rock in item:

            for bullet in red_bullets:
                if bullet.touches(rock):
                    rock.justgotshot = True
                    bullet.isalive = False
                    red_points += 500
            for bullet in blue_bullets:
                if bullet.touches(rock):
                    rock.justgotshot = True
                    bullet.isalive = False
                    blue_points += 500
            if rock.touches(red, -30, -30) and not red_invincible:
                red.speedx = 0
                red.speedy = 0
                if red_isalive:
                    red_points -= 250
                red_isalive = False
            if rock.touches(blue, -30, -30) and not blue_invincible:
                blue.speedx = 0
                blue.speedy = 0
                if blue_isalive:
                    blue_points -= 250
                blue_isalive = False
    for bullet in blue_bullets:
        if bullet.touches(red, -15, -15) and not red_invincible:
            bullet.isalive = False
            red.speedx = 0
            red.speedy = 0
            if red_isalive:
                blue_points += 250
                red_points -= -250
            red_isalive = False
    for bullet in red_bullets:
        if bullet.touches(blue, -15, -15) and not blue_invincible:
            bullet.isalive = False
            blue.speedx = 0
            blue.speedy = 0
            if blue_isalive:
                red_points += 250
                blue_points -= 250
            blue_isalive = False

    for rock in large_asteroids_list:
        if rock.justgotshot:

            rock.isalive = False

            for i in range(med_asteroid_multi):
                for item in med_asteroids_list:
                    if not item.isalive:
                        item.x = rock.x + (random.random() * 25) * (random.randrange(
                            -1, 2, 2))
                        item.y = rock.y + (random.random() * 25) * (random.randrange(
                            -1, 2, 2))
                        item.speedx = rock.speedx * 0.5 + rock.speedx * 1.75 * (
                            random.random())
                        item.speedy = rock.speedy * 0.5 + rock.speedy * 1.75 * (
                            random.random())
                        item.isalive = True
                        break

            rock.x = 500
            rock.y = -500
            rock.justgotshot = False

    for rock in med_asteroids_list:
        if rock.justgotshot:

            rock.isalive = False

            for i in range(small_asteroid_multi):
                for item in small_asteroids_list:
                    if not item.isalive:
                        item.x = rock.x + (random.random() * 10) * (random.randrange(
                            -1, 2, 2))
                        item.y = rock.y + (random.random() * 10) * (random.randrange(
                            -1, 2, 2))
                        item.speedx = rock.speedx + rock.speedx * 2 * (random.random())
                        item.speedy = rock.speedy + rock.speedy * 2 * (random.random())
                        item.isalive = True
                        break

            rock.x = 500
            rock.y = -500
            rock.justgotshot = False

    for rock in small_asteroids_list:
        if rock.justgotshot:
            rock.isalive = False
            rock.x = 500
            rock.y = -500
            rock.justgotshot = False


def death_and_spawnprotection():
    global red_isalive, red_frame, red_shooting, red_invincible, red_invincible_counter, blue_isalive, blue_frame, blue_shooting, blue_invincible, blue_invincible_counter
    if not red_isalive:
        red_shooting = True
        red_frame += 1
        if red_frame >= 3:
            red.image = red_images[3]
        if red_frame >= 6:
            red.image = red_images[4]
        if red_frame >= 9:
            red.image = red_images[5]
        if red_frame >= 12:
            red.image = red_images[6]
        if red_frame >= 15:
            red.image = red_images[7]
        if red_frame >= 18:
            red.image = red_images[8]
        if red_frame >= 21:
            red.image = red_images[9]
        if red_frame >= 24:
            red.image = red_images[10]
        if red_frame >= 27:
            red.x = 500
            red.y = -500
        if red_frame >= 190:
            red_frame = 0
            red.image = red_images[0]
            red.x = 225
            red.y = camera_height / 2
            red_isalive = True
            red_invincible = True

    if not blue_isalive:
        blue_shooting = True
        blue_frame += 1
        if blue_frame >= 3:
            blue.image = blue_images[3]
        if blue_frame >= 6:
            blue.image = blue_images[4]
        if blue_frame >= 9:
            blue.image = blue_images[5]
        if blue_frame >= 12:
            blue.image = blue_images[6]
        if blue_frame >= 15:
            blue.image = blue_images[7]
        if blue_frame >= 18:
            blue.image = blue_images[8]
        if blue_frame >= 21:
            blue.image = blue_images[9]
        if blue_frame >= 24:
            blue.image = blue_images[10]
        if blue_frame >= 27:
            blue.x = 500
            blue.y = -500
        if blue_frame >= 190:
            blue_frame = 0
            blue.image = blue_images[0]
            blue.x = camera_width - 225
            blue.y = camera_height / 2
            blue_isalive = True
            blue_invincible = True
    # spawn/respawn protection
    if blue_invincible:
        if blue_invincible_counter >= 90:
            blue_invincible_counter = 0
            blue_invincible = False
        else:
            blue_invincible_counter += 1

    # respawn/invincibility display
    if red_invincible:
        if red_invincible_counter >= 90:
            red_invincible_counter = 0
            red_invincible = False
        else:
            red_invincible_counter += 1


def asteroid_respawn():
    small_count = 0
    med_count = 0
    large_count = 0

    for rock in large_asteroids_list:
        if rock.isalive:
            large_count += 1
    for rock in med_asteroids_list:
        if rock.isalive:
            med_count += 1
    for rock in small_asteroids_list:
        if rock.isalive:
            small_count += 1

    # checks number of asteroids current in play, prevents asteroid from respawning if subdivisions aren't available
    if large_count < asteroid_count:
        if med_count + (med_asteroid_multi * large_count) <= (asteroid_count * med_asteroid_multi) - med_asteroid_multi:
            if (small_count + (med_count * small_asteroid_multi) + (large_count * med_asteroid_multi * small_asteroid_multi)
                    <= (asteroid_count * med_asteroid_multi * small_asteroid_multi)
                    - (med_asteroid_multi * small_asteroid_multi)):

                for rock in large_asteroids_list:

                    # respawns a large rock if respawn condition is met
                    if not rock.isalive:

                        rock.isalive = True

                        rock.rotation = 0
                        while abs(rock.rotation) < 1:
                            rock.rotation = (random.random() * 1.5) * random.randrange(-1, 2, 2)

                        rock.speedx = (random.random() * 2) * random.randrange(-1, 2, 2)
                        rock.speedy = (random.random() * 2) * random.randrange(-1, 2, 2)

                        rock.x = (random.random() * camera_width)
                        if rock.x < camera_width / 2:
                            x_wall_distance = rock.x
                        else:
                            x_wall_distance = camera_width - rock.x

                        rock.y = (random.random() * camera_height)
                        if rock.y < camera_width / 2:
                            y_wall_distance = rock.y
                        else:
                            y_wall_distance = camera_width - rock.y

                        if x_wall_distance < y_wall_distance and rock.x < camera_width / 2:
                            rock.x = -30
                        elif x_wall_distance < y_wall_distance and rock.x >= camera_width / 2:
                            rock.x = camera_width + 30
                        elif y_wall_distance < x_wall_distance and rock.y < camera_height / 2:
                            rock.y = -30
                        elif y_wall_distance < x_wall_distance and rock.y >= camera_height / 2:
                            rock.y = camera_height + 30

                        break


def draw():
    camera.clear("black")

    camera.draw(red)
    for item in red_bullets:
        camera.draw(item)

    camera.draw(blue)
    for item in blue_bullets:
        camera.draw(item)

    for i in asteroids:
        for item in i:
            camera.draw(item)

    # respawn counter/spawn protection display
    if blue_isalive == False and blue_frame >= 27:
        camera.draw(
            uvage.from_text(
                camera_width - 225, 50,
                "Blue Respawn In: " + str(round(
                    (190 - blue_frame) / 30)), 25, "yellow"))
    if red_isalive == False and red_frame >= 27:
        camera.draw(
            uvage.from_text(
                225, 50, "Red Respawn In: " + str(round((190 - red_frame) / 30)),
                25, "yellow"))
    if blue_invincible:
        camera.draw(
            uvage.from_text(camera_width - 225, 50, "Blue is Spawn Protected", 25,
                            "Green"))
    if red_invincible:
        camera.draw(uvage.from_text(225, 50, "Red is Spawn Protected", 25,
                                    "Green"))

    # points/timer
    camera.draw(uvage.from_text(50, 50, str(red_points), 40, "red"))
    camera.draw(
        uvage.from_text(camera_width - 50, 50, str(blue_points), 40, "blue"))

    camera.draw(
        uvage.from_text(
            camera_width / 2, 50, str(round((game_length * 2 - game_length) / 30)),
            30, "white"))

    camera.display()


def tick():
    global game_length, game_on, highscore

    if game_length == 0:
        game_on = False

    if game_on:
        red_movement()
        blue_movement()

        red_projectiles()
        blue_projectiles()

        game_length -= 1

        asteroid_control()
        collision_control()
        asteroid_respawn()
        death_and_spawnprotection()


        draw()

    if not game_on:
        camera.clear("black")

        if red_points > blue_points:
            highscore = open("assets/highscore.txt", "r")
            if red_points > int(highscore.read()):
                highscore.close()
                highscore = open("assets/highscore.txt", "w")
                highscore.write(str(red_points))
                highscore.close()

            camera.draw(
                uvage.from_text(camera_width / 2, camera_height / 2 - 50, "Red Wins!", 45, "red"))
            camera.draw(
                uvage.from_text(camera_width / 2, camera_height / 2, "Score: " + str(red_points), 40, "white"))

        if blue_points > red_points:
            highscore = open("assets/highscore.txt", "r")
            if blue_points > int(highscore.read()):
                highscore.close()
                highscore = open("assets/highscore.txt", "w")
                highscore.write(str(blue_points))
                highscore.close()
            camera.draw(
                uvage.from_text(camera_width / 2, camera_height / 2 - 50, "Blue Wins!", 45, "blue"))
            camera.draw(
                uvage.from_text(camera_width / 2, camera_height / 2, "Score: " + str(blue_points), 40, "white"))
        if red_points == blue_points:
            camera.draw(
                uvage.from_text(camera_width / 2, camera_height / 2 - 50, "Tie!", 45, "Yellow"))
            camera.draw(
                uvage.from_text(camera_width / 2, camera_height / 2, "Score: " + str(red_points), 40, "white"))

        highscore = open("assets/highscore.txt", "r")
        camera.draw(
            uvage.from_text(camera_width / 2, camera_height / 2 + 100, "All Time Highscore: " + str(highscore.read()),
                            40, "yellow"))
        highscore.close()

        camera.draw(uvage.from_text(camera_width / 2, camera_height / 2 + 50, "Select R to Restart!", 40, "yellow"))

        camera.display()
        if uvage.is_pressing("r"):
            game_on = True
            reset()


uvage.timer_loop(30, tick)
