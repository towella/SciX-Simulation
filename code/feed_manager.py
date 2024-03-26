from standard_values import *
from random import randint


class FeedManager:
    def __init__(self):
        self.feed = max_feed
        self.cap = max_feed
        self.increase_feed = 0
        self.alive = True

    def kill(self, amount=1):
        self.feed -= amount

    def __len__(self):
        return self.feed

    def update(self, agents, timestep):
        # add more feed
        self.increase_feed += feed_per_step  # increment
        # when over 1, add as many feed as the integer part of add_feed
        if self.increase_feed >= 1:
            self.feed += int(self.increase_feed)
            self.increase_feed -= int(self.increase_feed)  # remove integer part of float, leaving decimal
            # cap the amount of feed that can be supported by the environment (creates a carrying capacity for plants)
            if self.feed > self.cap:
                self.feed = self.cap

        return []  # return no offspring
