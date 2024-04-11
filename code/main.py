from standard_values import *
import threading
import time
from bilby import BilbyManager
from fox import FoxManager
from hunter_manager import HunterManager
from feed_manager import FeedManager
from grapher import Grapher


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
    agents = {species[0]: BilbyManager(),
              species[1]: FoxManager(),
              species[2]: FeedManager(),
              species[3]: HunterManager()}
    # begins with no data points as they can not be assumed after burn in period
    iter_population_data = {species[0]: [],
                            species[1]: [],
                            species[2]: [],
                            species[3]: []}
    graph = Grapher()

    feed_to_add = 0
    # --- TIMESTEP ---
    t = time.time()
    for timestep in range(-burn_in, max_time):
        # TODO: Terminal logging for testing
        if timestep < 0:
            print(f"Burn in day: [{timestep // day24}]")
        else:
            print(f"Time day: [{timestep // day24}] | Bilbies {len(agents[species[0]])}, Foxes {len(agents[species[1]])}, Food {len(agents[species[2]])}")

        # update graph (after addition of foxes for first data point to reflect t=0)
        graph.update(timestep, agents)

        # -- UPDATES --
        for key in species:
            agents[key].update(timestep, agents)

        # -- CHECKS --
        # if a year has passed record population data (include initial t=0 after burn in)
        if timestep % year == 0:
            for key in species:
                iter_population_data[key].append(str(len(agents[key])))
            print("Year " + str(timestep // year))

        # kill instance if all bilbies are dead :(
        if len(agents[species[0]]) <= 0:
            break
    print("One iter: " + str(time.time() - t))
    graph.plot_graph()  # display graph before next iter
    return iter_population_data


def percentage_set(percentage):
    print(f"\nBeginning {percentage}%...")  # <-- progress update
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

