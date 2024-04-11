from random import randint

# --- standard units of time in minutes --------------------------------------------------------------------------------
year = 525600
month = 43800
week = 10080
day24 = 1440
day12 = 720
hour = 60


# --- simulation params ------------------------------------------------------------------------------------------------
species = ["bilby", "fox", "plant", "hunter"]
granularity = 5  # predator population (in % of bilby population) increase between sets of testing
use_threading = False
if use_threading:
    print("USING THREADING")
else:
    print("NOT USING THREADING")

# -- bilbies --
bilbies = 100  # 70

# -- foxes --
foxes = 9
fox_sensitivity = 30  # must be between 1 and initial bilby population
if fox_sensitivity < 1:
    fox_sensitivity = 1
elif fox_sensitivity > bilbies:
    fox_sensitivity = bilbies
fox_arrival_prob = 0.1  # 10% chance a fox will arrive each week (under max fox number)

# -- hunters --
hunters_active = True  # whether human hunters are included in the simulation
if hunters_active:
    print("HUNTERS ACTIVE")
else:
    print("HUNTERS ARE NOT ACTIVE")
hunter_sensitivity = 1  # must be between 1 and initial fox population
hunt_interval = year // 2  # how long between hunts
hunt_duration = week * 2  # how long a hunt lasts

# -- feed --
max_feed = 900
feed_per_step = max_feed / week

# -- simulation duration --
iterations = 1
years = 12  # 3 generations of bilbies
burn_in = 200 * day24     # IF SOMETHING IS WRONG ON THE GRAPH, CHECK BURN IN! ----------------------------
max_time = years * year + burn_in  # length of iter + startup time

# -- graphing --
use_graph = True
display_graph = year
log_graph = day24


# --- support functions ------------------------------------------------------------------------------------------------
# time: current sim time, frequency: how often hunting occurs, agent list: list of agents to prey upon,
# sensitivity: how effective hunting is, time range: [frequency, freq+time_range] range of time hunt is accepted
def scaled_hunt(agent_list, sensitivity):
    hunt_prob = randint(0, 1)
    N = len(agent_list)
    hunt_threshold = N / (N + sensitivity)  # scales prob of killing bilby with bilby population
    # compare probability of kill with random gen val. Also, bilbies need to still be alive to hunt
    print(hunt_threshold)
    if hunt_prob >= hunt_threshold and N > 0:
        i = randint(0, N - 1)
        agent_list[i].kill()