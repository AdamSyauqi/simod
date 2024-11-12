import random
from collections import deque
from scipy.stats import norm
import numpy as np

# Constants
NUM_TRUCKS = 10
TIME_UNITS = 200
NUM_LOADERS = 2
NUM_SCALERS = 1

# Function to generate time ranges and probabilities
def generate_times_and_probabilities(start, end, peak_probability=0.3):
    time_values = list(range(start, end + 1))
    n = len(time_values)

    if n <= 3:
        if n == 1:
            probabilities = [1.0]
        elif n == 2:
            probabilities = [0.5, 0.5]
        else:
            probabilities = [0.3, 0.4, 0.3]
    else:
        mid_idx = n // 2
        x = np.linspace(-2, 2, n)
        pdf = norm.pdf(x, loc=0, scale=1)
        pdf = pdf / pdf.sum()
        probabilities = pdf.tolist()

    probabilities[mid_idx] = peak_probability
    probabilities = [p * (1 - peak_probability) / sum(probabilities[:mid_idx] + probabilities[mid_idx+1:]) if i != mid_idx else peak_probability for i, p in enumerate(probabilities)]
    return time_values, probabilities

# Generate times and probabilities
LOADING_TIMES, LOADING_PROB = generate_times_and_probabilities(1, 9)
SCALING_TIMES, SCALING_PROB = generate_times_and_probabilities(2, 6)
DUMP_TIMES, DUMP_PROB = generate_times_and_probabilities(10, 20)

print("Loading Times and Probabilities:", LOADING_TIMES, LOADING_PROB)
print("Scaling Times and Probabilities:", SCALING_TIMES, SCALING_PROB)
print("Dumping Times and Probabilities:", DUMP_TIMES, DUMP_PROB)

# Initialize truck states
class Truck:
    def __init__(self, id):
        self.id = id
        self.time_remaining = 0
        self.current_process = "waiting"
        self.loader_wait_time = 0
        self.scaler_wait_time = 0
        self.loader_wait_count = 0
        self.scaler_wait_count = 0

# Create trucks and queues
all_trucks = [Truck(i) for i in range(NUM_TRUCKS)]
loader_queue = deque(all_trucks)
loader_busy = [None] * NUM_LOADERS
scaler_queue = deque()
scaler_busy = [None] * NUM_SCALERS
dumping_queue = deque()
time_log = {truck.id: [] for truck in all_trucks}
loader_time_utilization = [0] * NUM_LOADERS
scaler_time_utilization = [0] * NUM_SCALERS

# Lists for process times
loading_times = []
scaling_times = []
dumping_times = []

# Helper functions
def get_probabilistic_time(options, probabilities):
    return random.choices(options, probabilities)[0]

def advance_time(truck, process, time_log):
    truck.current_process = process
    process_time = get_probabilistic_time(
        LOADING_TIMES if process == "loading" else SCALING_TIMES if process == "scaling" else DUMP_TIMES,
        LOADING_PROB if process == "loading" else SCALING_PROB if process == "scaling" else DUMP_PROB
    )
    truck.time_remaining = process_time
    time_log[truck.id].append((process, process_time))

    if process == "loading":
        loading_times.append(process_time)
    elif process == "scaling":
        scaling_times.append(process_time)
    elif process == "dumping":
        dumping_times.append(process_time)

# Simulation
for current_time in range(TIME_UNITS):
    print(f"\nTime Unit {current_time}")

    # Increment waiting times for trucks in loader and scaler queues
    for truck in loader_queue:
        truck.loader_wait_time += 1
        if truck.current_process != "waiting_in_loader_queue":
            truck.loader_wait_count += 1
            truck.current_process = "waiting_in_loader_queue"

    for truck in scaler_queue:
        truck.scaler_wait_time += 1
        if truck.current_process != "waiting_in_scaler_queue":
            truck.scaler_wait_count += 1
            truck.current_process = "waiting_in_scaler_queue"

    # Check loaders
    for i in range(NUM_LOADERS):
        if loader_busy[i]:
            loader_busy[i].time_remaining -= 1
            if loader_busy[i].time_remaining <= 0:  # Move to scaler queue
                loader_busy[i].current_process = "moving_to_scaler_queue"
                scaler_queue.append(loader_busy[i])
                loader_busy[i] = None

        # Track loader utilization
        if loader_busy[i] is not None:
            loader_time_utilization[i] += 1

    # Fill loaders if available
    for i in range(NUM_LOADERS):
        if loader_busy[i] is None and loader_queue:
            next_truck = loader_queue.popleft()
            advance_time(next_truck, "loading", time_log)
            loader_busy[i] = next_truck

    # Check scalers
    for i in range(NUM_SCALERS):
        if scaler_busy[i]:
            scaler_busy[i].time_remaining -= 1
            if scaler_busy[i].time_remaining <= 0:  # Move to dumping queue
                scaler_busy[i].current_process = "moving_to_dumping_queue"
                advance_time(scaler_busy[i], "dumping", time_log)
                dumping_queue.append(scaler_busy[i])
                scaler_busy[i] = None

        # Track scaler utilization
        if scaler_busy[i] is not None:
            scaler_time_utilization[i] += 1

    # Move truck from scaler queue if scaler is free
    for i in range(NUM_SCALERS):
        if scaler_busy[i] is None and scaler_queue:
            next_truck = scaler_queue.popleft()
            advance_time(next_truck, "scaling", time_log)
            scaler_busy[i] = next_truck

    # Check dumping trucks
    for truck in list(dumping_queue):
        truck.time_remaining -= 1
        if truck.time_remaining <= 0:  # Return to loader queue after dumping
            dumping_queue.remove(truck)
            advance_time(truck, "waiting", time_log)
            truck.current_process = "waiting"
            loader_queue.append(truck)

    # Per-time unit log
    loader_queue_ids = [truck.id for truck in loader_queue]
    scaler_queue_ids = [truck.id for truck in scaler_queue]
    dumping_queue_ids = [truck.id for truck in dumping_queue]
    loaders_status = [(f'{truck.id}' if truck else "Empty") for truck in loader_busy]
    scalers_status = [(f'{truck.id}' if truck else "Empty") for truck in scaler_busy]
    loading_times_display = [truck.time_remaining if truck else "-" for truck in loader_busy]
    scaling_times_display = [truck.time_remaining if truck else "-" for truck in scaler_busy]
    dumping_times_display = [truck.time_remaining for truck in dumping_queue]

    print("Loader Queue:", loader_queue_ids)
    print("Loader Status:", loaders_status, "Time Left:", loading_times_display)
    print("Scaler Queue:", scaler_queue_ids)
    print("Scaler Status:", scalers_status, "Time Left:", scaling_times_display)
    print("Dumping Queue:", dumping_queue_ids, "Time Left for each:", dumping_times_display)

# Print final time logs for each truck
for truck_id, log in time_log.items():
    print(f"\nTruck {truck_id} Log:")
    for process, time in log:
        print(f" - {process.capitalize()} for {time} time units")

# Calculate average waiting times for all trucks
total_loader_wait_time = sum(truck.loader_wait_time for truck in all_trucks)
total_loader_wait_count = sum(truck.loader_wait_count for truck in all_trucks)
loader_avg_waiting_time = total_loader_wait_time / total_loader_wait_count if total_loader_wait_count > 0 else 0

total_scaler_wait_time = sum(truck.scaler_wait_time for truck in all_trucks)
total_scaler_wait_count = sum(truck.scaler_wait_count for truck in all_trucks)
scaler_avg_waiting_time = total_scaler_wait_time / total_scaler_wait_count if total_scaler_wait_count > 0 else 0

# Calculate average process times
average_loading_time = sum(loading_times) / len(loading_times) if loading_times else 0
average_scaling_time = sum(scaling_times) / len(scaling_times) if scaling_times else 0
average_dumping_time = sum(dumping_times) / len(dumping_times) if dumping_times else 0

# Utilization
loader_utilization = [(time / TIME_UNITS) * 100 for time in loader_time_utilization]
scaler_utilization = [(time / TIME_UNITS) * 100 for time in scaler_time_utilization]

average_loader_utilization = sum(loader_utilization) / NUM_LOADERS if NUM_LOADERS > 0 else 0
average_scaler_utilization = sum(scaler_utilization) / NUM_SCALERS if NUM_SCALERS > 0 else 0

# Summary of average times
print("\nSummary of Average Times:")
print(f"Average Waiting Time in Loader Queue: {loader_avg_waiting_time:.2f} time units")
print(f"Average Waiting Time in Scaler Queue: {scaler_avg_waiting_time:.2f} time units")
print(f"Average Loading Time: {average_loading_time:.2f} time units")
print(f"Average Scaling Time: {average_scaling_time:.2f} time units")
print(f"Average Dumping Time: {average_dumping_time:.2f} time units")
print("\nLoader Utilizations:")
for i, utilization in enumerate(loader_utilization):
    print(f"Loader {i+1} Utilization: {utilization:.2f}%")
print(f"Average Loader Utilization: {average_loader_utilization:.2f}%")

print("\nScaler Utilizations:")
for i, utilization in enumerate(scaler_utilization):
    print(f"Scaler {i+1} Utilization: {utilization:.2f}%")
print(f"Average Scaler Utilization: {average_scaler_utilization:.2f}%")
