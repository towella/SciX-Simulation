from standard_values import *
from random import randint
import threading
import time
from bilby import Bilby


def format_file_header(species, years):
    header = ["Foxes in % of Bilby Pop"]
    for species in species:
        for year in range(1, years+1):
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
            agents = {species[0]: [Bilby() for agent in range(bilbies)],
                      species[1]: [],
                      species[2]: [],
                      species[3]: [],
                      species[4]: []}
            iter_population_data = {}
            for key in species:
                iter_population_data[key] = []

            # --- TIMESTEP ---
            for timestep in range(max_time):
                # TODO UPDATE ALL AGENTS

                # if a year has passed record population data
                # TODO VERY COSTLY - 0.3 SECONDS PER ITER!!!!
                if timestep % year == 0:
                    for key in species:
                        iter_population_data[key].append(str(len(agents[key])))

            # save iteration population data
            set_population_data.append(gen_iter_pop_line(iter_population_data, species))

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

