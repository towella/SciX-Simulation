# pyinstaller code/main.py code/camera.py code/game_data.py code/player.py code/level.py code/spawn.py code/support.py code/tiles.py code/trigger.py --onefile --noconsole


# screen resizing tut, dafluffypotato: https://www.youtube.com/watch?v=edJZOQwrMKw

import pygame, sys, time, json, math, csv
from level import Level
from text import Font
from game_data import *
from support import resource_path

# General setup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

# window and screen Setup ----- window is real pygame window. screen is surface everything is placed on then resized
# to blit on window. (art pixel == game pixel)
# https://stackoverflow.com/questions/54040397/pygame-rescale-pixel-size

# https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
# https://www.reddit.com/r/pygame/comments/r943bn/game_stuttering/
# vsync only works with scaled flag. Scaled flag will only work in combination with certain other flags.
# although resizeable flag is present, window can not be resized, only fullscreened with vsync still on
# vsync prevents screen tearing (multiple frames displayed at the same time creating a shuddering wave)
window = pygame.display.set_mode((int(screen_width * scaling_factor), int(screen_height * scaling_factor)), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.SCALED, vsync=True)

# all pixel values in game logic should be based on the screen! NO .display FUNCTIONS!!
screen = pygame.Surface((screen_width, screen_height))  # the display surface, re-scaled and blit to the window
screen_rect = screen.get_rect()  # used for camera scroll boundaries

# caption and icon
pygame.display.set_caption('Sample')
pygame.display.set_icon(pygame.image.load(resource_path('../assets/icon/app_icon.png')))

# get controller joysticks
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
print(f"joy {len(joysticks)}")
for joystick in joysticks:
    joystick.init()

# font
font = Font(fonts['small_font'], 'white')


# calculates population estimation for case data using logistic growth
def math_mod(pop_data):
    # time is based on months NOT years

    months = list(pop_data.keys())
    P_init = pop_data["0"]  # initial population at t=0
    P_current = pop_data[months[-2]]  # Last measured pop size
    t_current = int(months[-2])  # Time of most recent data point
    t = int(months[-1])  # time to be estimated

    # interpolated growth rate = (final pop - init pop) / init pop / dif t
    r = (P_current - P_init) / P_init / int(months[-2])
    # rearranged logistic growth formula, solving for K
    k = (-P_current * P_init * math.pow(math.e, -r*t_current) + P_current * P_init) / (P_init - P_current * math.pow(math.e, -r*t_current))

    P_estimate = (P_init * k) / ((k - P_init) * math.pow(math.e, -r*t) + P_init)

    return P_estimate  # return population estimate


def sim_mod():
    click = False

    # delta time
    previous_time = time.time()
    dt = time.time() - previous_time
    previous_time = time.time()
    fps = clock.get_fps()

    # MODIFY TO LOAD DESIRED ROOMS
    starting_spawn = 'room_1'
    level = Level(fps, '../rooms/tiled_rooms/room_0.tmx', screen, screen_rect, joysticks, starting_spawn)

    run = False  # TODO testing stub, should start as True
    while run:
        # delta time  https://www.youtube.com/watch?v=OmkAUzvwsDk
        dt = time.time() - previous_time
        dt *= 60  # keeps units such that movement += 1 * dt means add 1px if at 60fps
        previous_time = time.time()
        fps = clock.get_fps()

        # x and y mouse pos
        mx, my = pygame.mouse.get_pos()

        # -- INPUT --
        click = False
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_COMMA or event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                    sys.exit()
                # TODO Debugging only, remove
                elif event.key == pygame.K_x:
                    global game_speed
                    if game_speed == 60:
                        game_speed = 20
                    else:
                        game_speed = 60

            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

            # Controller events
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == controller_map['left_analog_press']:
                    run = False
                    pygame.quit()
                    sys.exit()

        # -- Update --
        screen.fill((48, 99, 142))  # fill background with colour
        level.update(dt, fps)  # runs level processes

        font.render(f'FPS: {str(clock.get_fps())}', screen, (0, 0))  # TODO Debugging only, remove

        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))  # scale screen to window

        # -- Render --
        pygame.display.update()
        clock.tick(game_speed)

    return 0


def main(num_cases, iters):
    error_diffs = []

    with open("../output/out.csv", 'w') as outf:
        writer = csv.writer(outf)
        # iterates through all case data (files numerically named)
        for case in range(num_cases):
            writer.writerow([f"Case {case}"])  # out -> case title
            print(f"Beginning case {case}...")

            # -- LOAD CASE DATA --
            with open(f"../case data/{case}.txt") as f:
                data = json.load(f)  # dict with case data
            true_val = data["pop_data"][list(data["pop_data"].keys())[-1]]
            writer.writerow(["True value", true_val])  # out -> true val

            # -- MATH MODULE --
            m_estimate = math_mod(data["pop_data"])
            writer.writerow(["Math", m_estimate])  # out -> math estimate
            print("-- Mathematical module complete --")

            # -- SIMULATION MODULE --
            #TODO Implement simulation module
            s_estimates = ["Program"]
            # run sim iterations
            for i in range(iters):
                s_estimates.append(sim_mod())
                print(f"Simulation: iteration {i} complete")
            writer.writerow(s_estimates)  # out -> simulation estimates

            # find average simulation estimate
            sim_avg_est = 0
            for i in s_estimates[1:]:
                sim_avg_est += i
            sim_avg_est /= iters
            writer.writerow(["Program avg", sim_avg_est])  # out -> simulation avg estimate
            print("-- Simulation module complete --")

            # -- ERROR EVALUATION --
            print("Calculating error")
            # - MATH ERROR -
            m_error = ((true_val - m_estimate) / true_val) * 100
            writer.writerow(["Math error (%)", m_error])  # out -> math error

            # - SIM ERROR -
            s_error = ((true_val - sim_avg_est) / true_val) * 100
            writer.writerow(["Simulation error (%)", s_error])  # out -> sim error

            # - ERROR DIFFERENCE -
            dif = m_error - s_error
            writer.writerow(["Error difference (%)", dif])  # out -> error diff
            error_diffs.append(dif)

            print(" -- Error calculation complete --")

            # -- END CASE --
            writer.writerow("")  # new line in file
            print(f"Case {case} complete\n")

        # -- AVG ERROR DIFFERENCE --
        avg_dif = 0
        for i in error_diffs:
            avg_dif += i
        avg_dif /= len(error_diffs)
        writer.writerow(["Avg error difference", avg_dif])  # out -> avg error difference


main(1, 100)
