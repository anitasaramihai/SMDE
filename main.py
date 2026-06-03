import random
import heapq  #event-driven list

# Kendall parameters

arrival_distribution = "D"   # M / D / G
service_distribution = "M"   # M / D / G
number_of_servers = 1        
capacity = 5                 # total capacity (including servers)
discipline = "FIFO"          # FIFO, LIFO, SIRO


arrival_rate = 2.0            #(lambda)
service_rate = 3.0           # (mu)

# Deterministic times (if the distribution is D)
deterministic_arrival_time = 0.5 #customers arrive every 0.5 units of time
deterministic_service_time = 0.3 #each customer is served in 0.3 units of time

max_clients = 10000

clock = 0.0
event_list = [] 
queue = []       
servers_busy = 0

# statistici
served_clients = 0 #Count how many customers were fully served
total_waiting_time = 0
clients_that_waited = 0
rejected_clients = 0



# functions 

def generate_arrival_time():
    """Calculates the time between arrivals based on the specified distribution"""
    if arrival_distribution == "M":
        return random.expovariate(arrival_rate)
    elif arrival_distribution == "D":
        return deterministic_arrival_time
    elif arrival_distribution == "G":
        
        return random.uniform(0.2, 0.8)
    else:
        raise ValueError("Arrival time unknown")


def generate_service_time():
    """Calculates the serving time based on the specified distribution"""
    if service_distribution == "M":
        return random.expovariate(service_rate)
    elif service_distribution == "D":
        return deterministic_service_time
    elif service_distribution == "G":
       
        return max(0.1, random.gauss(0.5, 0.1))
    else:
        raise ValueError("Service distribution unknown")


def schedule_event(event_time, event_type, client_id):
    """Add a new event to the sorted list"""
    heapq.heappush(event_list, (event_time, event_type, client_id)) #Add an event to the events list, automatically sorting it by the time it takes place.


def process_arrival(client_id):
    """What happens when a new customer comes in"""
    global servers_busy, served_clients, rejected_clients

    print(f"[{clock:.2f}] Client {client_id} has arrived")

    # if the system is full
    if capacity is not None and (len(queue) + servers_busy) >= capacity: 
        print("System full, customer is rejected")
        rejected_clients += 1
        return

    # If the server is free, start serving immediately.
    if servers_busy < number_of_servers:
        servers_busy += 1
        service_time = generate_service_time()
        departure_time = clock + service_time
        print(f"   Service begins (serving time: {service_time:.2f}), will leave for {departure_time:.2f}")
        schedule_event(departure_time, "departure", client_id)
    else:
        # if all servers are busy, join the queue
        print(" if all servers are busy, join the queue")
        queue.append((client_id, clock)) #add the customer to the queue along with the time they arrived

def process_departure(client_id):
    """What happens when a client finishes service"""
    global servers_busy, served_clients, total_waiting_time, clients_that_waited

    print(f"[{clock:.2f}] Client {client_id} leave")

    served_clients += 1 #increase the number of customers served
    servers_busy -= 1 #the number of occupied servers is decreasing

    if queue:
        # select the next client based on the rule
        if discipline == "FIFO":
            next_client, arrival_time = queue.pop(0)
        elif discipline == "LIFO":
            next_client, arrival_time = queue.pop()
        elif discipline == "SIRO":
            idx = random.randrange(len(queue))
            next_client, arrival_time = queue.pop(idx)
        else:
            raise ValueError("Unknown queue rule")

        waiting_time = clock - arrival_time
        total_waiting_time += waiting_time
        clients_that_waited += 1

        print(f"   Client {next_client} waited {waiting_time:.2f} and service begins now")

        servers_busy += 1
        service_time = generate_service_time()
        departure_time = clock + service_time
        schedule_event(departure_time, "departure", next_client)
        print(f" He will be leaving for {departure_time:.2f}")


#simulates the evolution of a queue over time
created_clients = 1
next_arrival_time = clock + generate_arrival_time()
schedule_event(next_arrival_time, "arrival", created_clients)

while event_list:     #As long as there are future events in the priority list, the simulation continues
    event_time, event_type, client_id = heapq.heappop(event_list)
    clock = event_time

    if event_type == "arrival":
        process_arrival(client_id)
        created_clients += 1
        # schedules the next customer's arrival
        if created_clients <= max_clients:
            next_arrival = clock + generate_arrival_time()
            schedule_event(next_arrival, "arrival", created_clients)

    elif event_type == "departure":
        process_departure(client_id)

    # Stop if all customers have been created and there are no more check-out events
    if created_clients > max_clients and not any(e[1] == "departure" for e in event_list):
        break



print("\n=== statistics ===")
print(f"Customers served: {served_clients}")
print(f"Rejected customers: {rejected_clients}")
print(f"Customers who have been waiting: {clients_that_waited}")

if clients_that_waited > 0:
    avg_wait = total_waiting_time / clients_that_waited
    print(f"Average wait time (simulated): {avg_wait:.2f}")

# validation using the theoretical formula M/M/1
if (arrival_distribution == "M" and service_distribution == "M" 
        and number_of_servers == 1 and arrival_rate < service_rate):
    wq_theoretical = arrival_rate / (service_rate * (service_rate - arrival_rate))
    print(f"Theoretical average time Wq (M/M/1): {wq_theoretical:.2f}")
    print(f"Difference between simulation and theory: {abs(avg_wait - wq_theoretical):.2f}")
