# - standard units of time in minutes -
year = 525600
month = 43800
week = 10080
day24 = 1440
day12 = 720
hour = 60


# -- simulation params --
species = ["bilby", "fox", "plant"]
granularity = 5  # predator population (in % of bilby population) increase between sets of testing
use_threading = False
if use_threading:
    print("Using threading")
else:
    print("Not using threading")

# land and population density (individuals per hectare)
land_size = 5000  # land size in hectares
bilby_density = 0.01555555556

# interaction chances (agents per 10m^2)
bilby_interact = bilby_density/1000

# populations
bilbies = 15  # 70
foxes = 0
burn_in = 200  # in days
max_feed = 150
feed_per_step = max_feed / week

# simulation duration
iterations = 1
years = 12  # 3 generations of bilbies
max_time = years * year + burn_in  # length of iter + startup time

# graphing
display_graph = year
log_graph = day24
