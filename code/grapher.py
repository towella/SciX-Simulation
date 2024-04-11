from standard_values import *
import matplotlib.pyplot as plt


class Grapher:
    def __init__(self):
        self.active = use_graph  # only allows use of graphing if true (false for generating bulk data)
        # graphing datapoints lists (can't assume initial values)
        self.plot_data = [[], [], []]
        self.plot_interval = log_graph  # interval of time between data points
        self.display = display_graph  # how often the graph is displayed during sim run time (in timesteps)

    def plot_graph(self):
        if self.active:
            plt.plot([i + 1 for i in range(len(self.plot_data[0]))], self.plot_data[0], label="Bilbies")
            plt.plot([i + 1 for i in range(len(self.plot_data[1]))], self.plot_data[1], label="Foxes")
            plt.plot([i + 1 for i in range(len(self.plot_data[2]))], self.plot_data[2], label="Grass")
            plt.legend()
            plt.show(block=True)

    def update(self, timestep, agents):
        if self.active:
            # update plot data from t=0 onwards
            if timestep % self.plot_interval == 0 and timestep >= 0:
                self.plot_data[0].append(len(agents[species[0]]))
                self.plot_data[1].append(len(agents[species[1]]))
                self.plot_data[2].append(len(agents[species[2]]))

            # display graph after t=0 (not inclusive)
            if timestep % self.display == 0 and timestep > 0:
                self.plot_graph()


