from standard_values import *
from random import randint


# gets approximately 3 months
def get_reproduction_timer():
    gestation = randint(12 * day24, 14 * day24)
    pouch = randint(75 * day24, 80 * day24)
    burrow = 2 * week
    return gestation + pouch + burrow


class Bilby:
    def __init__(self, initial_pop=False):
        # TODO ? self.agentID = ID  # unique ID int

        # - age -
        # if part of initial population of bilbies, randomise age otherwise start young
        if initial_pop:
            self.age = randint(0, 7 * year)
        else:
            self.age = randint(75 * day24, 80 * day24) + 2 * week  # age in minutes when become independent
        self.max_age = randint(5 * year, 7 * year)  # lifetime in minutes (5 to 7 year lifespan)
        self.alive = True  # whether alive or dead

        # - gender -
        self.gender = randint(1, 2)  # 1 = male, 2 = female

        # - hunger -
        self.feed_per_day = 1  # required amount of feed to consume each day

        # - reproduction (Only used by females) -
        # time until new litter has been conceived, birthed, gone through infancy and left natal burrow
        # if part of initial population, randomise timer otherwise start from 0
        if initial_pop:
            self.reproduce_timer = randint(0, year // 4)
        else:
            self.reproduce_timer = get_reproduction_timer()

    def kill(self):
        self.alive = False

    def update(self, agents, time):
        feed_manager = agents[species[2]][0]
        self.age += 1  # increment age
        offspring = []

        # kill agent
        if self.age >= self.max_age:
            self.alive = False
        else:
            # eat once a day if there is feed available
            if time % day24 == 0:
                for feed in range(self.feed_per_day):
                    if len(feed_manager) > 0:
                        feed_manager.kill()  # remove a feed from feed manager
                    # die if can't eat
                    else:
                        self.kill()
                        break

            # reproduce
            # must be a female that is older than 5 months to reproduce
            if self.gender == 2 and self.age > 5 * month:
                self.reproduce_timer -= 1
                if self.reproduce_timer == 0:
                    self.reproduce_timer = get_reproduction_timer()
                    for child in range(randint(1, 3)):
                        offspring.append(Bilby())  # TODO <--

        return offspring
