from random import randint


# --- support functions ------------------------------------------------------------------------------------------------
# time: current sim time, frequency: how often hunting occurs, agent list: list of agents to prey upon,
# sensitivity: how effective hunting is, time range: [frequency, freq+time_range] range of time hunt is accepted
def scaled_hunt(agent_list, sensitivity):
    hunt_prob = randint(0, 1)
    N = len(agent_list)
    hunt_threshold = N / (N + sensitivity)  # scales prob of killing bilby with bilby population
    # compare probability of kill with random gen val. Also, bilbies need to still be alive to hunt
    if hunt_prob <= hunt_threshold and N > 0:
        i = randint(0, N - 1)
        agent_list[i].kill()


# --- standard units of time in minutes --------------------------------------------------------------------------------
year = 525600
month = 43800
week = 10080
day24 = 1440
day12 = 720
hour = 60


# --- simulation params ------------------------------------------------------------------------------------------------
species = ["bilby", "fox", "plant", "hunter"]
use_threading = True
if use_threading:
    print("USING THREADING")
else:
    print("NOT USING THREADING")

# -- bilbies --
bilbies = 80  # not very important as bilby carrying capacity is determined by feed input which should be reached during burn in

# -- foxes --
foxes = 6
fox_sensitivity = 1  # must be between 1 and initial bilby population
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
hunter_sensitivity = 6  # must be between 1 and initial fox population

# -- feed --
max_feed = 500
feed_per_step = max_feed / week

# -- simulation duration --
iterations = 10
years = 12  # 3 generations of bilbies
burn_in = 200 * day24     # IF SOMETHING IS WRONG ON THE GRAPH, CHECK BURN IN! ----------------------------
max_time = years * year  # length of iter

# -- graphing --
use_graph = False
display_graph = year
log_graph = day24


# --- test cases -------------------------------------------------------------------------------------------------------
# [[hunt_interval, hunt_duration, num_hunters]]
efforts = [0, 1, 2, 3, 5, 10, 20]
# must subtract duration from interval otherwise duration will offset interval (e.g. bi-annual interval + 2 weeks)
strats = [[0, year*12], [month-week, week], [2*month-week, week], [4*month-week, week],
          [6*month-2*week, 2*week], [year-3*week, 3*week], [2*year-month, month], [0, 0]]
test_cases = []
for strat in range(len(strats)):
    test_cases.append([])
    for effort in range(len(efforts)):
        test_cases[strat].append(strats[strat] + [efforts[effort]])
