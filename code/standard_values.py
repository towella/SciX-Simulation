# standard units of time in minutes
year = 525600
month = 43800
day24 = 1440
day12 = 720
hour = 60

# simulation params
species = ["bilby", "fox", "plant", "insect", "rabbit"]
granularity = 5  # predator population (in % of bilby population) increase between sets of testing
use_threading = True

# simulation duration
iterations = 2
years = 12  # 2 generations of bilbies
max_time = years * year

# land and population density (individuals per hectare)
land_size = 4500  # land size in hectares
bilby_density = 0.01555555556

# populations
bilbies = int(bilby_density * land_size)
