from user import User, addUser
import matplotlib.pyplot as plt

monte_carlo_runs = 10
nTransactions = 5
networkSizes = [2, 10, 50, 100, 500, 1000]


def simulate():
    avg_latencies = []
    for size in networkSizes:
        avg_latencies.append(avg_monte_carlo_latency(size))
    return avg_latencies

def avg_monte_carlo_latency(size):
    total = 0
    for i in range(monte_carlo_runs):
        print("Network Size ", size, "run ", i + 1)
        total += get_avg_latency(size)
    return total/monte_carlo_runs

def get_avg_latency(size):
    latencyList = []
    userList = []
    for i in range(size):
        response = addUser(i)
        if response and response["success"]:
            token = response["token"]
            user = User(token, init_value=100, size=size, amount=1, nTransactions=nTransactions, latencyList=latencyList)
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

def plot_latency_size(avg_latencies):
    plt.plot(networkSizes, avg_latencies)
    plt.xlabel("Network Size")
    plt.ylabel("Average Latency")
    plt.title("Measuring Average Latency against Network Size")
    plt.show()

avg_latencies = simulate()
plot_latency_size(avg_latencies)


