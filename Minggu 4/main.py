import random


class Vehicle:
    def __init__(self, vehicle_type, length):
        self.type = vehicle_type
        self.length = int(length*10)/10.0

    def __str__(self):
        return self.type + ', ' + str(self.length) + 'm'


class FerryDeck:
    def __init__(self, loading_proceduce):
        self.length = 32.0
        self.columns = 2
        self.deck = [[], []]
        self.space_remaining = [self.length] * self.columns
        self.vehicle_count = 0
        self.vehicle_count_by_type = [0, 0, 0]
        self.last_vehicle_failed_to_load = None
        self.loading_proceduce = loading_proceduce

    def load_vehicle(self, vehicle):
        if self.loading_proceduce == 1:
            return self.__load_one_deck_first(vehicle)
        elif self.loading_proceduce == 2:
            return self.__load_cars_and_lorries_separately(vehicle)
        elif self.loading_proceduce == 3:
            return self.__load_randomly(vehicle)
        else:
            vehicle = random_vehicle_no_motor()
            return self.__load_motorcyle_after(vehicle)

    def __load_one_deck_first(self, vehicle):
        for i in range(self.columns):
            #print(f"remaining space: {self.space_remaining[i]}")
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

    def __load_cars_and_lorries_separately(self, vehicle):
        if vehicle.type == 'Car':
            if self.space_remaining[0] >= vehicle.length:
                self.deck[0].append(vehicle)
                self.space_remaining[0] -= vehicle.length
                self.vehicle_count += 1
                self.vehicle_count_by_type[0] += 1
                return 1
            elif self.space_remaining[1] >= vehicle.length:
                self.deck[1].append(vehicle)
                self.space_remaining[1] -= vehicle.length
                self.vehicle_count += 1
                self.vehicle_count_by_type[0] += 1
                return 1
            else:
                return 0
        elif vehicle.type == 'Lorry':
            if self.space_remaining[1] >= vehicle.length:
                self.deck[1].append(vehicle)
                self.space_remaining[1] -= vehicle.length
                self.vehicle_count += 1
                self.vehicle_count_by_type[1] += 1
                return 1
            elif self.space_remaining[0] >= vehicle.length:
                self.deck[0].append(vehicle)
                self.space_remaining[0] -= vehicle.length
                self.vehicle_count += 1
                self.vehicle_count_by_type[1] += 1
                return 1
            else:
                return 0
        else:
            return self.__load_randomly(vehicle)

    def __load_randomly(self, vehicle):
        random_col = list(range(self.columns))
        random.shuffle(random_col)

        for i in random_col:
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
    
    def __load_motorcyle_after(self, vehicle):
        for i in range(self.columns):
            # print(f"remaining space: {self.space_remaining[i]}")
            if self.space_remaining[i] >= vehicle.length:
                self.deck[i].append(vehicle)
                self.space_remaining[i] -= vehicle.length
                self.vehicle_count += 1
                if vehicle.type == 'Car':
                    self.vehicle_count_by_type[0] += 1
                elif vehicle.type == 'Lorry':
                    self.vehicle_count_by_type[1] += 1
            else:
                vehicle = random_vehicle_only_motor()
                if self.space_remaining[i] >= vehicle.length:
                    self.deck[i].append(vehicle)
                    self.space_remaining[i] -= vehicle.length
                    self.vehicle_count += 1
                    self.vehicle_count_by_type[2] += 1

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

def random_vehicle():
    r = random.randint(1, 100)
    if r <= 40:
        length = random.uniform(3.5, 5.5)
        return Vehicle('Car', length)
    elif r <= 95:
        length = random.uniform(8.0, 10.0)
        return Vehicle('Lorry', length)
    else:
        length = random.uniform(0.7, 0.9)
        return Vehicle('Motorcycle', length)
    
def random_vehicle_no_motor():
    r = random.uniform(1.0, 100.0)
    if r <= 42.5:
        length = random.uniform(3.5, 5.5)
        return Vehicle('Car', length)
    else:
        length = random.uniform(8.0, 10.0)
        return Vehicle('Lorry', length)
    
def random_vehicle_only_motor():
    length = random.uniform(0.7, 0.9)
    return Vehicle('Motorcycle', length)

def simulate(total_sim, algorithm=1):
    total_wasted_space = 0
    total_vehicles_carried = 0
    total_cars_carried = 0
    total_lorries_carried = 0
    total_motorcycles_carried = 0

    for i in range(total_sim):
        ferry_deck = FerryDeck(algorithm)
        while ferry_deck.load_vehicle(random_vehicle()):
            pass

        total_wasted_space += sum(ferry_deck.space_remaining)
        total_vehicles_carried += ferry_deck.vehicle_count
        total_cars_carried += ferry_deck.vehicle_count_by_type[0]
        total_lorries_carried += ferry_deck.vehicle_count_by_type[1]
        total_motorcycles_carried += ferry_deck.vehicle_count_by_type[2]

        #print(ferry_deck)

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
    string += f'Total simulation: {total_sim}\n'
    string += f'Algorithm: {algorithm}\n'
    string += f'Average wasted space: {avg_wasted_space}%\n'
    string += f'Average vehicles carried: {avg_vehicles_carried}\n'
    string += f'Average cars carried: {avg_cars_carried}%\n'
    string += f'Average lorries carried: {avg_lorries_carried}%\n'
    string +=\
        f'Average motorcycles carried: {avg_motorcycles_carried}%\n'
    print(string)


def main():
    simulate(10000, 1)
    simulate(10000, 2)
    simulate(10000, 3)
    #simulate(10, 4) # motors after

if __name__ == '__main__':
    main()