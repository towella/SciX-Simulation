from standard_values import *
from random import randint
import threading
import time
from bilby import Bilby
from fox import Fox
from feed_manager import FeedManager


def format_file_header(species, years):
    header = ["Foxes in % of Bilby Pop"]
    for species in species:
        for year in range(0, years+1):
            if year == 0:
                header.append(f"{species.capitalize()} Initial")
            else:
                header.append(f"{species.capitalize()} Year {year}")
    return ",".join(header)


# generates a row to be output to file containing all population data for a single iteration of simulation
def gen_iter_pop_line(pop_data, keys):
    line = []
    for key in keys:
        line += pop_data[key]
    return ",".join(line)


# batch output of multiple rows of data in format ["line", "line", ...]
def output_to_file(file, pop_data):
    pop_data = "\n".join(pop_data)
    file.write("\n"+pop_data)


def run_simulation():
    agents = {species[0]: [Bilby() for agent in range(bilbies)],
              species[1]: [Fox() for agent in range(foxes)],
              species[2]: [FeedManager()]}
    # begins with initial populations
    iter_population_data = {species[0]: [str(bilbies)],
                            species[1]: [str(foxes)],
                            species[2]: [str(initial_feed)]}
    feed_to_add = 0

    # --- TIMESTEP ---
    for timestep in range(max_time):

        # TODO debug -- current populations
        if timestep % day24 == 0:
            print(f"Bilbies {len(agents[species[0]])}, Foxes {len(agents[species[1]])}, Food {len(agents[species[2]][0])}")

        # -- UPDATES --
        for key in species:
            pop_indices = []
            new_agents = []
            # remove if dead, otherwise update and collect offspring
            for i, agent in enumerate(agents[key]):
                if not agent.alive:
                    pop_indices.append(i)
                else:
                    new_agents += agent.update(agents, timestep)  # agent.update -> [offspring_agent]
            # add in new offspring
            agents[key] += new_agents

            # pop in reverse order so lower indices are unaffected by modification
            pop_indices.sort()
            pop_indices.reverse()
            for i in pop_indices:
                agents[key].pop(i)

        # -- CHECKS --
        # if a year has passed record population data (exclude initial)
        if timestep % year == 0 and timestep > 0:
            for key in species:
                iter_population_data[key].append(str(len(agents[key])))
            print("Year " + str(timestep // year))

        # kill instance if one bilby left (none left to reproduce) or all are dead
        if len(agents[species[0]]) <= 1:
            break

    return iter_population_data


def percentage_set(percentage):
    print(f"Beginning {percentage}%...")  # <-- progress update
    set_population_data = []

    # open file once rather than every time output
    # buffering allows for faster output to file (output in chunks)
    with open(f"../output/{percent}.csv", "w", buffering=16384) as f:
        # initialise file
        header = format_file_header(species, years)
        f.write(header)

        # --- ITERATION ---
        itert = time.time()
        for iteration in range(iterations):
            t = time.time()
            
            iter_pop_data = run_simulation()

            # save iteration population data
            set_population_data.append(gen_iter_pop_line(iter_pop_data, species))

            print(iteration + 1, time.time() - t)  # <-- log time for one iteration

        # batch output set population data rows to file
        output_to_file(f, set_population_data)

        print(f"{percentage}% complete: " + str(time.time() - itert))  # <-- log time for percentage set


# --- PERCENTAGE SET ---
totalt = time.time()
threads = []
# loop from 0% to 100% of bilby population
for percent in range(0, 101, granularity):
    # threading
    if use_threading:
        # generate all threads
        thread = threading.Thread(target=percentage_set, args=(percent,))
        thread.start()
        threads.append(thread)
    # no threading
    else:
        percentage_set(percent)

if use_threading:
    # join all threads
    for thread in threads:
        thread.join()

print(time.time() - totalt)

