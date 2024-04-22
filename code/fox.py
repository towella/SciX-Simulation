from standard_values import *
from random import randint


class FoxManager:
    def __init__(self):
        self.foxes = [Fox(initial_pop=True) for agent in range(foxes)]  # list of fox instances
        self.max_num = foxes  # maximum number of foxes
        self.fox_arrival_prob = fox_arrival_prob

    def __len__(self):
        return len(self.foxes)

    def attempt_hunt(self, sensitivity):
        scaled_hunt(self.foxes, sensitivity)

    def update(self, timestep, agents):
        pop_indices = []
        # remove if dead, otherwise update
        for i, agent in enumerate(self.foxes):
            if not agent.alive:
                pop_indices.append(i)
            else:
                agent.update(timestep, agents)

        # pop in reverse order so lower indices are unaffected by modification
        pop_indices.sort()
        pop_indices.reverse()
        for i in pop_indices:
            self.foxes.pop(i)

        # potentially introduce new fox randomly each week as long as len < threshold
        if timestep % week == 0 and len(self.foxes) < self.max_num:
            val = randint(0, 1)
            if val <= self.fox_arrival_prob:
                self.foxes.append(Fox())

        return []  # return 'offspring' will always be none


class Fox:
    def __init__(self, initial_pop=False):
        self.max_age = 3 * year  # average fox lifespan
        # initial population will have a distribution of ages
        if initial_pop:
            self.age = randint(0, self.max_age)
        else:
            self.age = 6 * month  # age in minutes (independent at 6 months)
        self.alive = True
        self.sensitivity = fox_sensitivity

    def kill(self):
        self.alive = False

    def update(self, timestep, agents):
        self.age += 1

        # die if too old
        if self.age > self.max_age:
            self.alive = False
        # if still alive
        else:
            # no hunting during burn in
            # every week (relative to the fox's age to distribute hunting randomly over time),
            # attempt to kill one bilby
            if timestep >= 0 and self.age % week == 0:
                agents[species[0]].attempt_hunt(self.sensitivity)
