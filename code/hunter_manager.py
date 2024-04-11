from random import randint
from standard_values import *


class HunterManager:
    def __init__(self):
        self.active = hunters_active
        self.interval = hunt_interval  # interval between hunts
        self.sensitivity = hunter_sensitivity  # how sensitive human hunters are (how effective)
        self.duration = hunt_duration  # length of a hunt
        self.timer = 0

    # pop data is not relevant for hunters
    def __len__(self):
        return 0

    def update(self, timestep, agents):
        # no hunting of foxes during burn in
        if self.active and timestep >= 0:
            self.timer += 1

            # hunt only after t=0, for a given duration with intervals between. Check hunt outcome each day
            if self.timer % day24 == 0 and self.timer < self.duration and timestep >= 0:
                agents[species[1]].attempt_hunt(self.sensitivity)
            # reset timer after hunt and interval time period is complete ready for next cycle of culling
            elif self.timer >= self.duration + self.interval:
                self.timer = 0

        return []
