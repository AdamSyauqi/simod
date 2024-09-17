import random
import pandas as pd

time_between_arrival_arrival = [
    (1, 125, 1), # Assigned Number 1, Assigned Number 2, Value
    (126, 250, 2),
    (251, 375, 3),
    (376, 500, 4),
    (501, 625, 5),
    (626, 750, 6),
    (751, 875, 7),
    (876, 1000, 8)
]

service_time_dist = [
    (1, 10, 1), # Assigned Number 1, Assigned Number 2, Value
    (11, 30, 2),
    (31, 60, 3),
    (61, 85, 4),
    (86, 95, 5),
    (96, 100, 6)
]

def roll_d1000():
    return random.randint(1, 1000)

def roll_d100():
    return random.randint(1, 100)

def get_time_between_arrival_arrival(roll):
    for start, end, value in time_between_arrival_arrival:
        if start <= roll <= end:
            return value
    return 0

def get_service_time(roll):
    for start, end, value in service_time_dist:
        if start <= roll <= end:
            return value
    return 0

def simulate_customers(num_customers=20):
    customers = []
    total_idle_time = 0
    starting_time = 0  
    
    for i in range(num_customers):
        time_between_arrival = 0
        if i == 0:
            arrival_time = starting_time 
        else:
            arrival_roll = roll_d1000()
            time_between_arrival = get_time_between_arrival_arrival(arrival_roll)
            arrival_time = customers[-1]['arrival_time'] + time_between_arrival

        service_roll = roll_d100()
        service_time = get_service_time(service_roll)
        
        time_service_begins = max(arrival_time, customers[-1]['time_service_ends']) if i > 0 else arrival_time
        time_service_ends = time_service_begins + service_time
        idle_time = max(0, time_service_begins - customers[-1]['time_service_ends']) if i > 0 else 0

        waiting_time = max(0, time_service_begins - arrival_time)

        total_idle_time += idle_time

        customers.append({
            'customer': i + 1,
            'time_between_arrival': time_between_arrival,
            'arrival_time': arrival_time,
            'time_service_begins': time_service_begins,
            'service_time_duration': service_time,
            'time_service_ends': time_service_ends,
            'waiting_time': waiting_time,
            'idle_time': total_idle_time
        })

    return customers

def report(df, num_customers):
    last_customer = df.iloc[-1]

    total_idle = last_customer['idle_time']
    average_idle_time = float(total_idle) / float(num_customers)
    
    waiting_time = last_customer['waiting_time']
    average_waiting_time = float(waiting_time) / float(num_customers)

    time_between_arrival = df['time_between_arrival'].sum()
    average_time_between_arrival = float(time_between_arrival) / float(num_customers)

    service_time_duration = df['service_time_duration'].sum()
    average_service_time_duration = float(service_time_duration) / float(num_customers)

    return(average_idle_time, average_waiting_time, average_time_between_arrival, average_service_time_duration)

customers_number = input("Select number of Customers: ")

mode = input("Select mode 1 (Single), 2 (Multiple) (Type the number): ")

if mode == "1":
    customers_data = simulate_customers(int(customers_number))

    df_customers = pd.DataFrame(customers_data)

    simulation_report = report(df_customers, customers_number)

    print(df_customers)

    print("Simulation Report: ")
    print(f"Average Idle Time: {simulation_report[0]}")
    print(f"Average Waiting Time: {simulation_report[1]}")
    print(f"Average Time Between Arrival: {simulation_report[2]}")
    print(f"Average Service Time Duration: {simulation_report[3]}")
elif mode == "2":
    num_simulations = input("How many simulations? ")
    total_average_idle_time = 0
    total_average_waiting_time = 0
    total_average_time_between_arrival = 0
    total_average_service_time_duration = 0

    for num in range(int(num_simulations)):
        print(f"Simulation {num + 1}")
        customers_data = simulate_customers(int(customers_number))

        df_customers = pd.DataFrame(customers_data)

        simulation_report = report(df_customers, customers_number)

        print(df_customers)

        print("Simulation Report: ")
        print(f"Average Idle Time: {simulation_report[0]}")
        print(f"Average Waiting Time: {simulation_report[1]}")
        print(f"Average Time Between Arrival: {simulation_report[2]}")
        print(f"Average Service Time Duration: {simulation_report[3]}")
        print("------------------------------------------------------------")

        total_average_idle_time += simulation_report[0]
        total_average_waiting_time += simulation_report[1]
        total_average_time_between_arrival += simulation_report[2]
        total_average_service_time_duration += simulation_report[3]

    total_average_idle_time = total_average_idle_time / int(num_simulations)
    total_average_waiting_time = total_average_waiting_time / int(num_simulations)
    total_average_time_between_arrival = total_average_time_between_arrival / int(num_simulations)
    total_average_service_time_duration = total_average_service_time_duration / int(num_simulations)

    print("Simulation Report: ")
    print(f"Total Average Idle Time: {total_average_idle_time}")
    print(f"Total Average Waiting Time: {total_average_waiting_time}")
    print(f"Total Average Time Between Arrival: {total_average_time_between_arrival}")
    print(f"Total Average Service Time Duration: {total_average_service_time_duration}")
