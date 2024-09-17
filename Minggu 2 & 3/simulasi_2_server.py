import random
import pandas as pd

arrival_delay_arrival = [
    (1, 25, 1), 
    (26, 65, 2),
    (66, 85, 3),
    (86, 100, 4)
]

service_time_ali = [
    (1, 30, 2),
    (31, 58, 3),
    (59, 83, 4),
    (84, 100, 5)
]

service_time_badu = [
    (1, 35, 3),
    (36, 60, 4),
    (61, 80, 5),
    (81, 100, 6)
]

def roll_d100():
    return random.randint(1, 100)

def get_arrival_delay_arrival(roll):
    for start, end, value in arrival_delay_arrival:
        if start <= roll <= end:
            return value
    return 0

def get_service_time(roll, server):
    if server == "Ali":
        for start, end, value in service_time_ali:
            if start <= roll <= end:
                return value
    elif server == "Badu":
        for start, end, value in service_time_badu:
            if start <= roll <= end:
                return value
    return 0

def simulate_customers(num_customers=20):
    customers = []
    server_available_time = {"Ali": 0, "Badu": 0} 
    idle_time = {"Ali": 0, "Badu": 0}
    ali_count = 0
    badu_count = 0

    for i in range(num_customers):
        arrival_delay = 0
        if i == 0:
            arrival_time = 0  # First customer arrives at time 0
        else:
            arrival_roll = roll_d100()
            arrival_delay = get_arrival_delay_arrival(arrival_roll)
            arrival_time = customers[-1]['arrival_time'] + arrival_delay

        # Determine which server is available first (Ali or Badu)
        ali_idle = arrival_time >= server_available_time["Ali"]
        badu_idle = arrival_time >= server_available_time["Badu"]

        # Assign to Ali if available, otherwise assign to Badu
        if ali_idle:
            server_assigned = "Ali"
            ali_count += 1
            if arrival_time > server_available_time["Ali"]:
                idle_time["Ali"] += arrival_time - server_available_time["Ali"]
        elif badu_idle:
            server_assigned = "Badu"
            badu_count += 1
            if arrival_time > server_available_time["Badu"]:
                idle_time["Badu"] += arrival_time - server_available_time["Badu"]
        else: # Both end at the same time
            server_assigned = "Ali"
            ali_count += 1
            if arrival_time > server_available_time["Ali"]:
                idle_time["Ali"] += arrival_time - server_available_time["Ali"]

        service_roll = roll_d100()
        service_time = get_service_time(service_roll, server_assigned)

        # Service begins either when the server is free or when the customer arrives (whichever is later)
        service_start = max(arrival_time, server_available_time[server_assigned])
        service_end = service_start + service_time

        waiting_time = service_start - arrival_time

        # Update server's next available time
        server_available_time[server_assigned] = service_end

        customers.append({
            'customer': i + 1,
            'arrival_delay': arrival_delay,
            'arrival_time': arrival_time,
            'service_start': service_start,
            'service_time': service_time,
            'service_end': service_end,
            'server_assigned': server_assigned,
            'waiting_time': waiting_time,
            'idle_time_Ali': idle_time["Ali"],
            'idle_time_Badu': idle_time["Badu"],
        })

    return customers, ali_count, badu_count, idle_time

def report(df, num_customers, ali_count, badu_count, idle_time):
    # Report generation
    total_idle = idle_time["Ali"] + idle_time["Badu"]
    average_idle_time = total_idle / num_customers
    average_ali_idle_time = idle_time["Ali"] / num_customers
    average_badu_idle_time = idle_time["Badu"] / num_customers

    waiting_time = df['waiting_time'].sum()
    total_waiting_time = waiting_time
    average_waiting_time = total_waiting_time / num_customers

    service_time = df['service_time'].sum()
    average_service_time = service_time / num_customers

    arrival_delay = df['arrival_delay'].sum()
    average_arrival_delay = arrival_delay / num_customers

    return (average_idle_time, average_waiting_time, average_service_time, ali_count, badu_count, idle_time, average_arrival_delay, average_ali_idle_time, average_badu_idle_time)

customers_number = input("Select number of Customers: ")

mode = input("Select mode 1 (Single), 2 (Multiple) (Type the number): ")

if mode == "1":
    customers_data, ali_count, badu_count, idle_time = simulate_customers(int(customers_number))
    df_customers = pd.DataFrame(customers_data)
    simulation_report = report(df_customers, int(customers_number), ali_count, badu_count, idle_time)
    print(df_customers)
    print("Simulation Report: ")
    print(f"Average Idle Time: {simulation_report[0]}")
    print(f"Average Time Between Arrival: {simulation_report[6]}")
    print(f"Average Waiting Time: {simulation_report[1]}")
    print(f"Average Service Time Duration: {simulation_report[2]}")
    print(f"Total customers served by Ali: {simulation_report[3]}")
    print(f"Total customers served by Badu: {simulation_report[4]}")
    print(f"Total idle time for Ali: {simulation_report[5]['Ali']}")
    print(f"Average idle time for Ali: {simulation_report[7]}")
    print(f"Total idle time for Badu: {simulation_report[5]['Badu']}")
    print(f"Average idle time for Badu: {simulation_report[8]}")

elif mode == "2":
    num_simulations = input("How many simulations? ")
    print_mode = input("Need to print the table? (Type y or n)")
    total_average_idle_time = 0
    total_average_arrival_delay = 0
    total_average_waiting_time = 0
    total_average_service_time = 0
    total_ali_count = 0
    total_badu_count = 0
    total_ali_idle = 0
    average_ali_idle = 0
    total_badu_idle = 0
    average_badu_idle = 0

    for num in range(int(num_simulations)):
        customers_data, ali_count, badu_count, idle_time = simulate_customers(int(customers_number))
        df_customers = pd.DataFrame(customers_data)
        simulation_report = report(df_customers, int(customers_number), ali_count, badu_count, idle_time)

        if print_mode == "y":
            print(f"Simulation {num + 1}")
            print(df_customers.to_string())
            print("Simulation Report: ")
            print(f"Average Idle Time: {simulation_report[0]}")
            print(f"Average Time Between Arrival: {simulation_report[6]}")
            print(f"Average Waiting Time: {simulation_report[1]}")
            print(f"Average Service Time Duration: {simulation_report[2]}")
            print(f"Total customers served by Ali: {simulation_report[3]}")
            print(f"Total customers served by Badu: {simulation_report[4]}")
            print(f"Total idle time for Ali: {simulation_report[5]['Ali']}")
            print(f"Average idle time for Ali: {simulation_report[7]}")
            print(f"Total idle time for Badu: {simulation_report[5]['Badu']}")
            print(f"Average idle time for Badu: {simulation_report[8]}")
            print("------------------------------------------------------------")
        else:
            print(f"Simulation {num + 1} out of {num_simulations}")

        total_average_idle_time += simulation_report[0]
        total_average_arrival_delay += simulation_report[6]
        total_average_waiting_time += simulation_report[1]
        total_average_service_time += simulation_report[2]
        total_ali_count += ali_count
        total_badu_count += badu_count
        total_ali_idle += simulation_report[5]['Ali']
        average_ali_idle += simulation_report[7]
        total_badu_idle += simulation_report[5]['Badu']
        average_badu_idle += simulation_report[8]

    total_average_idle_time = total_average_idle_time / int(num_simulations)
    total_average_arrival_delay = total_average_arrival_delay / int(num_simulations)
    total_average_waiting_time = total_average_waiting_time / int(num_simulations)
    total_average_service_time = total_average_service_time / int(num_simulations)
    total_ali_count = total_ali_count / int(num_simulations)
    total_badu_count = total_badu_count / int(num_simulations)
    total_ali_idle = total_ali_idle / int(num_simulations)
    average_ali_idle = average_ali_idle / int(num_simulations)
    total_badu_idle = total_badu_idle / int(num_simulations)
    average_badu_idle = average_badu_idle / int(num_simulations)

    print("Total Simulation Report: ")
    print(f"Total Average Idle Time: {total_average_idle_time}")
    print(f"Total Average Waiting Time: {total_average_waiting_time}")
    print(f"Total Average Service Time Duration: {total_average_service_time}")
    print(f"Average customers served by Ali per simulation: {total_ali_count}")
    print(f"Average customers served by Badu per simulation: {total_badu_count}")
    print(f"Total idle time for Ali: {total_ali_idle}")
    print(f"Average idle time for Ali: {average_ali_idle}")
    print(f"Total idle time for Badu: {total_badu_idle}")
    print(f"Average idle time for Badu: {average_badu_idle}")
