from standard_values import *
from random import randint


class Fox:
    def __init__(self):
        self.age = 0  # age in minutes
        self.max_age = 3 * year  # average fox lifespan
        self.alive = True

    def kill(self):
        self.alive = False

    def update(self, agents, time):
        self.age += 1
        offspring = []

        # every week, kill one bilby if bilbies are still alive
        if time % week == 0:
            if len(agents[species[0]]) > 0:
                i = randint(0, len(agents[species[0]]) - 1)
                agents[species[0]][i].kill()
            # die if can't eat
            else:
                self.kill()

        return offspring
