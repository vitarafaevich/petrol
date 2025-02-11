#trying to put it together
import datetime
import math
import random
import ru_local as ru


class GasStation:
    """
    representing the gas station
    """

    def __init__(self, station_id, queue_limit, available_gas):
        """
        :param station_id: station id
        :param queue_limit: the max amount of cars in the line
        :param available_gas: available types of petrol
        """
        self.station_id = station_id
        self.queue_limit = queue_limit
        self.available_gas = available_gas
        self.line = []

    def is_queue_full(self):
        """
        checks are there some places in the line available
        :return: True, if the line if full, False otherwise
        """
        return len(self.line) >= self.queue_limit

    def add_client(self, client_info):
        """
        adds the client in the line.
        :param client_info: client information (arrival time, the amount of liters needed, type of petrol)
        """
        self.line.append(client_info)

    def serve_client(self):
        """
        serves the client from the line
        :return: information about served client or None if there line is empty
        """
        if self.line:
            return self.line.pop(0)
        return None


class GasStationManaging:
    """
    class for managing petrol stations and clients
    """

    def __init__(self):
        """
        giving the parameters of the gas station
        """
        self.stations = {}
        self.sales = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0}
        self.available = {}
        self.left = 0

    def load_stations(self, filename):
        """
        getting the data about the gas stations from the file
        :param filename: filename there the data is stored
        """
        with open('stations.txt', encoding='utf-8') as gas_stops:
            for row in gas_stops:
                machine = row.split()
                station_id = machine[0]
                queue_limit = int(machine[1])
                available_gas = list(machine[2:])
                self.stations[station_id] = GasStation(station_id, queue_limit, available_gas)
                self.available[station_id] = queue_limit

    def calculating_time(self, liters):
        """
        counting the serving time relying on the amount of liters and random param
        :param liters: the amount of petrol needed in liters
        :return: time in minutes
        """
        time = math.ceil(int(liters) / 10)
        if time > 1:
            time += random.randint(-1, 1)
        return time

    def clients_ids(self, req):
        """
        generating the client id
        :param req: list with data about client
        :return: line with the client id
        """
        return f"{str(req[0])[-8:-3]} {req[-1]} {req[1]} {req[2]}"


    def process_requests(self, filename):
        """
        processing the clients requests
        :param filename: the filename there the data about clients is stored
        :return: the result of processing
        """
        results = []
        with open(filename, encoding='utf-8') as clients_requests:
            for row in clients_requests:
                request = row.split()
                today = str(datetime.date.today())                                                                      #getting the current date
                arrival = datetime.datetime.strptime(today + ' ' + request[0], '%Y-%m-%d %H:%M')
                mins_needed = self.calculating_time(request[1])                                                         #counting the serving time (in mins)
                departure = arrival + datetime.timedelta(minutes=mins_needed)
                gasoline = request[2]                                                                                   #getting the type of petrol from request
                assigned_station = None                                                                                 #will be storing the number of the assigned station for the particular client

                #looking for a suitable station to service the customer
                for station_id, station in self.stations.items():
                    if gasoline in station.available_gas and not station.is_queue_full():
                        assigned_station = station_id
                        break
                if assigned_station:
                    client_id = self.clients_ids(request)                                                               #getting the client id (just info about)
                    self.stations[assigned_station].add_client((arrival, mins_needed, gasoline, client_id))             #assigning the station
                    self.available[assigned_station] -= 1
                    results.append(
                        f"{arrival.strftime('%H:%M')} {ru.NEW_CLIENT} {arrival.strftime('%H:%M')} {request[1]} {gasoline} {ru.IN_LINE} {assigned_station}")
                else:
                    self.left += 1                                                                                      #clients left
                    results.append(
                        f"{arrival.strftime('%H:%M')} {ru.CLIENT_LEFT} {arrival.strftime('%H:%M')} {request[1]} {gasoline} {ru.FULL_LINES}")

                #serving customers who are already in the queue
                for station_id in self.stations:
                    client = self.stations[station_id].serve_client()                                                   #the first client in the line
                    if client:
                        client_arrival, client_time, client_gasoline, client_id = client
                        if arrival >= client_arrival + datetime.timedelta(minutes=client_time):                         #arrival - 'current', client_arrival - arrival for client in the line
                            self.available[station_id] += 1
                            self.sales[client_gasoline] += int(request[1])
                            results.append(f"{departure.strftime('%H:%M')} {ru.TRANSPORT_ID} {client_id} {ru.SERVED_IN} {station_id}")

                #info about current lines on the stations
                for station_id, station in self.stations.items():
                    queue_info = f"{ru.STATION_NUM} {station_id} {ru.MAX_LINE} {station.queue_limit} " \
                                 f"{ru.PETROL_TYPE} {' '.join(station.available_gas)} -> "
                    queue_info += " ".join(f"* {client[3]} {client[1]} {ru.MIN}" for client in station.line)
                    results.append(queue_info)
                    #results.append(f"\n{ru.FINAL_SALES}")

        #final petrol sales in liters
        for gas, amount in self.sales.items():
            results.append(f"{gas}: {amount} {ru.LITERS}")

        return results

if __name__ == "__main__":
    managing = GasStationManaging()
    managing.load_stations('stations.txt')
    output = managing.process_requests('input.txt')

    for line in output:
        print(line)
