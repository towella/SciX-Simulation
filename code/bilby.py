from standard_values import *
from random import randint


class Bilby:
    def __init__(self):
        # TODO ? self.agentID = ID  # unique ID int

        # - age -
        self.age = 0  # age in minutes
        lifespan = (5, 7)  # in years
        self.max_age = randint(lifespan[0] * 525600, lifespan[1] * 525600)  # lifetime in minutes (5 to 7 year lifespan)

        # - gender -
        self.gender = randint(1, 2)  # 1 = male, 2 = female

        # - hunger -   currently assuming ample food
        '''self.energy = 550.0  # energy in KJ/d
        self.energy_loss = 0.8  # energy loss per minute in KJ (timestep) (0.8 * 60 * 12 ~= 550)'''

        # - reproduction -
        # male
        if self.gender == 1:
            self.reproduce_timer = 8 * month  # can reproduce once mature (time = timer)
            self.reproduce_interval = day24  # minimum interval between litters
        # female
        else:
            self.reproduce_timer = 5 * month
            self.reproduce_interval = 3 * month

    def update(self):
        self.age += 1  # increment age
