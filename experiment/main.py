from user import User, addUser
import matplotlib.pyplot as plt

monte_carlo_runs = 10
# Constants for the latency against network size graph
nTransactions = 5
networkSizes = [2, 10, 25, 50, 100, 200]
# Constants for the latency against numberOfTransactions per user graph
network_size = 5
transactions = [5, 10, 25, 50, 75, 100, 150, 200] # each value represents the number of transactions per user for an experiment

# Gets values for the latency against network size graph
def latency_against_size():
    avg_latencies = []
    for size in networkSizes:
        avg_latency = avg_monte_carlo_latency(size, nTransactions)
        print("Avg Latency : ", avg_latency)
        avg_latencies.append(avg_latency)
    return avg_latencies

# Gets values for the latency against numberOfTransactions per user graph
def latency_against_transactions():
    avg_latencies = []
    for transaction in transactions:
        avg_latency = avg_monte_carlo_latency(network_size, transaction)
        print("Avg Latency : ", avg_latency)
        avg_latencies.append(avg_latency)
    return avg_latencies

def avg_monte_carlo_latency(size, transactions):
    total = 0
    for i in range(monte_carlo_runs):
        print("Network Size ", size, "nTransactionsPerUser", transactions, "run ", i + 1)
        total += get_avg_latency(size, transactions)
    return total/monte_carlo_runs

def get_avg_latency(size, transactions):
    latencyList = []
    userList = []
    for i in range(size):
        response = addUser(i)
        if response and response["success"]:
            token = response["token"]
            user = User(token, init_value=1000, size=size, amount=1, nTransactions=transactions, latencyList=latencyList)
            user.start()
            # time.sleep(3)
            userList.append(user)
        else:
            print(response)
    for user in userList: user.join()
    avgLatency = sum(latencyList)/len(latencyList)
    # print("List ", latencyList)
    # print("avg ", avgLatency)
    return avgLatency

def plot_latency_size(avg_latencies, x, xLabel='Number of users'):
    plt.plot(x, avg_latencies)
    plt.xlabel(xLabel)
    plt.ylabel("Average Latency / ms")
    plt.title(f"Average Latency against {xLabel}")
    plt.show()

avg_latencies = latency_against_size()
plot_latency_size(avg_latencies, networkSizes, xLabel='Number of users')

avg_latencies = latency_against_transactions()
plot_latency_size(avg_latencies, transactions, xLabel='Number of transactions per user')


