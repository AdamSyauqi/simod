
import random

class Vehicle:
    def __init__(self, vehicle_type, length):
        self.type = vehicle_type
        self.length = int(length*10)/10.0

    def __str__(self):
        return self.type + ', ' + str(self.length) + 'm'

class FerryDeck:
    def __init__(self):
        self.length = 32.0
        self.columns = 2
        self.deck = [[], []]
        self.space_remaining = [self.length] * self.columns
        self.vehicle_count = 0
        self.vehicle_count_by_type = [0, 0, 0]
        self.last_vehicle_failed_to_load = None

    def load_vehicle(self, vehicle):
        for i in range(self.columns):
            if self.space_remaining[i] >= vehicle.length:
                self.deck[i].append(vehicle)
                self.space_remaining[i] -= vehicle.length
                self.vehicle_count += 1
                if vehicle.type == 'Car':
                    self.vehicle_count_by_type[0] += 1
                elif vehicle.type == 'Lorry':
                    self.vehicle_count_by_type[1] += 1
                else:
                    self.vehicle_count_by_type[2] += 1
                return 1

        self.last_vehicle_failed_to_load = vehicle
        return 0

    def __str__(self):
        string = ''
        for i in range(self.columns):
            string += f'Column {i}\n'
            for vehicle in self.deck[i]:
                string += vehicle.__str__()
                string += '; '
            string += f'\nWasted space: {self.space_remaining[i]}m\n\n'
        string += f'Total wasted space: {sum(self.space_remaining)}m\n'
        string += f'Total vehicles carried: {self.vehicle_count}\n'
        string += f'Total cars carried: {self.vehicle_count_by_type[0]}\n'
        string += f'Total lorries carried: {self.vehicle_count_by_type[1]}\n'
        string\
            += f'Total motorcycles carried: {self.vehicle_count_by_type[2]}\n'
        string += f'Last vehicle that failed to load: \
            {self.last_vehicle_failed_to_load.__str__()}\n'
        return string
    
    def check_deck(self):
        return self.deck[0], self.deck[1]

def random_vehicle():
    r = random.randint(1, 100)
    if r <= 40:
        length = random.uniform(3.5, 5.5)
        return Vehicle('Car', length)
    elif r <= 95:
        length = random.uniform(8.0, 10.0)
        return Vehicle('Lorry', length)
    else:
        length = random.uniform(2.0, 3.0)
        return Vehicle('Motorcycle', length)

def main():
    total_sim = input("How many simulations? ")
    total_sim = int(total_sim)
    total_wasted_space = 0
    total_vehicles_carried = 0
    total_cars_carried = 0
    total_lorries_carried = 0
    total_motorcycles_carried = 0

    for i in range(total_sim):
        print(f"Simulation {i+1} out of {total_sim}")
        ferry_deck = FerryDeck()
        for j in range(100):
            ferry_deck.load_vehicle(random_vehicle())

        # deck_1, deck_2 = ferry_deck.check_deck()
        # print("Deck 1")
        # print(deck_1)
        # print("Deck 2")
        # print(deck_2)

        total_wasted_space += sum(ferry_deck.space_remaining)
        total_vehicles_carried += ferry_deck.vehicle_count
        total_cars_carried += ferry_deck.vehicle_count_by_type[0]
        total_lorries_carried += ferry_deck.vehicle_count_by_type[1]
        total_motorcycles_carried += ferry_deck.vehicle_count_by_type[2]

    avg_wasted_space = round((total_wasted_space*100) / (total_sim*64), 2)
    avg_vehicles_carried = total_vehicles_carried / total_sim
    avg_cars_carried\
        = round((total_cars_carried*100)
                / (total_sim*avg_vehicles_carried), 2)
    avg_lorries_carried\
        = round((total_lorries_carried*100)
                / (total_sim*avg_vehicles_carried), 2)
    avg_motorcycles_carried\
        = round((total_motorcycles_carried*100)
                / (total_sim*avg_vehicles_carried), 2)

    string = ''
    string += f'Average wasted space: {avg_wasted_space}%\n'
    string += f'Average vehicles carried: {avg_vehicles_carried}\n'
    string += f'Average cars carried: {avg_cars_carried}%\n'
    string += f'Average lorries carried: {avg_lorries_carried}%\n'
    string +=\
        f'Average motorcycles carried: {avg_motorcycles_carried}%\n'
    print(string)

if __name__ == '__main__':
    main()
