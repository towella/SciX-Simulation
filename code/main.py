from standard_values import *
import threading
import time
from bilby import BilbyManager
from fox import FoxManager
from hunter_manager import HunterManager
from feed_manager import FeedManager
from grapher import Grapher


def format_file_header(species, years):
    header = []
    for type in species:
        if type != "hunter":
            for month in range(0, years*12 + 1):
                if month == 0:
                    header.append(f"{type.capitalize()} Initial")
                else:
                    header.append(f"{type.capitalize()} Month {month}")
    return ",".join(header)


# generates a row to be output to file containing all population data for a single iteration of simulation
def gen_iter_pop_line(pop_data, keys):
    line = []
    for key in keys:
        # ensure lines are correct length
        while len(pop_data[key]) != 144:
            pop_data[key].append("0")
        line += pop_data[key]
    return ",".join(line)


# batch output of multiple rows of data in format ["line", "line", ...]
def output_to_file(file, pop_data):
    pop_data = "\n".join(pop_data)
    file.write("\n"+pop_data)


def run_simulation(params):
    agents = {species[0]: BilbyManager(),
              species[1]: FoxManager(),
              species[2]: FeedManager(),
              species[3]: HunterManager(params)}
    # begins with no data points as they can not be assumed after burn in period
    iter_population_data = {species[0]: [],
                            species[1]: [],
                            species[2]: [],
                            species[3]: []}
    graph = Grapher()

    # --- TIMESTEP ---
    t = time.time()
    for timestep in range(-burn_in, max_time + 1):  # +1 to include max bound of range
        # TODO: Terminal logging for testing
        '''if timestep < 0:
            print(f"Burn in day: [{timestep // day24}]")
        else:
            print(f"Time day: [{timestep // day24}] | Bilbies {len(agents[species[0]])}, Foxes {len(agents[species[1]])}, Food {len(agents[species[2]])}")
        '''

        # -- RECORD POPS --
        # update graph (after addition of foxes for first data point to reflect t=0)
        graph.update(timestep, agents)
        # if a year has passed record population data (include initial t=0 after burn in)
        if timestep % month == 0 and timestep >= 0:
            for key in species:
                if key != "hunter":  # exclude hunter pop (since always constant)
                    iter_population_data[key].append(str(len(agents[key])))
            print("Month " + str(timestep // month))

        # -- UPDATES --
        for key in species:
            agents[key].update(timestep, agents)

        # -- CHECKS --
        # kill instance if all bilbies are dead :(
        if len(agents[species[0]]) <= 0:
            break

    graph.plot_graph()  # display graph before next iter
    return iter_population_data


def iteration_set(name, params):
    print(f"\n--- Iteration set ({name}): {iterations} iters ---")  # <-- progress update
    set_population_data = []

    # open file once rather than every time output
    # buffering allows for faster output to file (output in chunks)
    with open(f"../output/{name}.csv", "w", buffering=16384) as f:
        # initialise file
        header = format_file_header(species, years)
        f.write(header)

        # --- ITERATION ---
        itert = time.time()
        for iteration in range(iterations):
            print(f"Beginning iter {iteration}")
            t = time.time()
            
            iter_pop_data = run_simulation(params)

            # save iteration population data
            set_population_data.append(gen_iter_pop_line(iter_pop_data, species))

            print(f"Iteration {iteration + 1}: ", time.time() - t)  # <-- log time for one iteration

        # batch output set population data rows to file
        output_to_file(f, set_population_data)

        print(f"{name} complete: " + str(time.time() - itert))  # <-- log time for iteration set


# --- PERCENTAGE SET ---
totalt = time.time()
threads = []
# loop through all the predefined test cases
for y in range(len(test_cases)):
    for x in range(len(test_cases[y])):
        cell_name = str(y) + "," + str(x)
        # threading
        if use_threading:
            # generate all threads
            thread = threading.Thread(target=iteration_set, args=(cell_name, test_cases[y][x],))
            thread.start()
            threads.append(thread)
        # no threading
        else:
            iteration_set(cell_name, test_cases[y][x])

if use_threading:
    # join all threads
    for thread in threads:
        thread.join()

print("\nTOTAL RUN TIME: " + str(time.time() - totalt))

