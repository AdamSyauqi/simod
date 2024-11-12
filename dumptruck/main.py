import random
from collections import deque
from scipy.stats import norm
import numpy as np

# Constants
NUM_TRUCKS = 6
TIME_UNITS = 200

def generate_times_and_probabilities(start, end, peak_probability=0.3):
    time_values = list(range(start, end + 1))
    n = len(time_values)

    # Generate probabilities based on normal distribution
    if n <= 3:
        # Special case: if 3 or fewer values, set 40% for the middle value and 30% for others
        if n == 1:
            probabilities = [1.0]
        elif n == 2:
            probabilities = [0.5, 0.5]
        else:
            probabilities = [0.3, 0.4, 0.3]
    else:
        # Normal distribution with peak probability in the middle
        mid_idx = n // 2
        x = np.linspace(-2, 2, n)
        pdf = norm.pdf(x, loc=0, scale=1)
        pdf = pdf / pdf.sum()  # Normalize to make sum 1
        probabilities = pdf.tolist()

    # Ensure the middle value gets the specified peak probability
    probabilities[mid_idx] = peak_probability
    probabilities = [p * (1 - peak_probability) / sum(probabilities[:mid_idx] + probabilities[mid_idx+1:]) if i != mid_idx else peak_probability for i, p in enumerate(probabilities)]
    return time_values, probabilities

# Generate loading, scaling, and dumping times with specified distributions
print("Generating Loading Distribution")
LOADING_TIMES, LOADING_PROB = generate_times_and_probabilities(1, 9)
print("Generating Scaling Distribution")
SCALING_TIMES, SCALING_PROB = generate_times_and_probabilities(2, 6)
print("Generating Dumping Distribution")
DUMP_TIMES, DUMP_PROB = generate_times_and_probabilities(10, 30)

# Display the generated times and probabilities
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

# Create all trucks and add to the loader queue initially
all_trucks = [Truck(i) for i in range(NUM_TRUCKS)]
loader_queue = deque(all_trucks)
loader_busy = [None, None]  # Two loaders, None means available
scaler_queue = deque()
scaler_busy = None
dumping_queue = deque()
time_log = {truck.id: [] for truck in all_trucks}  # Log times for each process
loader_time_utilization = 0
scaler_time_utilization = 0

# Lists to calculate averages for loading, scaling, and dumping times
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

    # Log times for each process to calculate averages
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
    for i, loader in enumerate(loader_busy):
        if loader:
            loader.time_remaining -= 1
            if loader.time_remaining <= 0:  # Move to scaler queue
                loader.current_process = "moving_to_scaler_queue"
                scaler_queue.append(loader)
                loader_busy[i] = None

    # Fill loaders if available; no queue, direct to loaders with 50/50 chance
    for i in range(2):
        if loader_busy[i] is None and loader_queue:
            next_truck = loader_queue.popleft()
            advance_time(next_truck, "loading", time_log)
            loader_busy[i] = next_truck

    # Loader 0 utilization counter
    if loader_busy[0] != None:
        print("Loader 1 Busy")
        loader_time_utilization += 1

    # Loader 1 utilization counter
    if loader_busy[1] != None:
        print("Loader 2 Busy")
        loader_time_utilization += 1

    # Check scaler
    if scaler_busy:
        scaler_busy.time_remaining -= 1
        if scaler_busy.time_remaining <= 0:  # Move to dumping queue with correct dumping time
            scaler_busy.current_process = "moving_to_dumping_queue"
            advance_time(scaler_busy, "dumping", time_log)  # Set dumping time here
            dumping_queue.append(scaler_busy)
            scaler_busy = None

    # Move truck from scaler queue if scaler is free; skip queue if empty
    if scaler_busy is None and scaler_queue:
        next_truck = scaler_queue.popleft()
        advance_time(next_truck, "scaling", time_log)
        scaler_busy = next_truck

    # Scaler utilization counter
    if scaler_busy:
        scaler_time_utilization += 1

    # Check dumping trucks, iterate over a copy to modify safely
    for truck in list(dumping_queue):
        truck.time_remaining -= 1
        if truck.time_remaining <= 0:  # Return to loader queue after dumping
            dumping_queue.remove(truck)
            advance_time(truck, "waiting", time_log)
            truck.current_process = "waiting"
            loader_queue.append(truck)

    # Visualization of queues and busy states
    loader_queue_ids = [truck.id for truck in loader_queue]
    scaler_queue_ids = [truck.id for truck in scaler_queue]
    dumping_queue_ids = [truck.id for truck in dumping_queue]
    loaders_status = [(f'Truck {truck.id}' if truck else "Empty") for truck in loader_busy]
    scaler_status = f'Truck {scaler_busy.id}' if scaler_busy else "Empty"
    loading_times_display = [truck.time_remaining if truck else "-" for truck in loader_busy]
    scaling_time_display = scaler_busy.time_remaining if scaler_busy else "-"
    dumping_times_display = [truck.time_remaining for truck in dumping_queue]

    print("Loader Queue:", loader_queue_ids)
    print("Loader 1:", loaders_status[0], "Time Left:", loading_times_display[0])
    print("Loader 2:", loaders_status[1], "Time Left:", loading_times_display[1])
    print("Scaler Queue:", scaler_queue_ids)
    print("Scaler:", scaler_status, "Time Left:", scaling_time_display)
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
utilization_loader_time = (loader_time_utilization / TIME_UNITS) / 2 * 100
utilization_scaler_time = (scaler_time_utilization / TIME_UNITS) * 100

# Summary of average times
print("\nSummary of Average Times:")
print(f"Average Waiting Time in Loader Queue: {loader_avg_waiting_time:.2f} time units")
print(f"Average Waiting Time in Scaler Queue: {scaler_avg_waiting_time:.2f} time units")
print(f"Average Loading Time: {average_loading_time:.2f} time units")
print(f"Average Scaling Time: {average_scaling_time:.2f} time units")
print(f"Average Dumping Time: {average_dumping_time:.2f} time units")
print(f"Loader Utilization: {utilization_loader_time:.2f}%")
print(f"Scaler Utilization: {utilization_scaler_time:.2f}%")