from user import User, addUser
import matplotlib.pyplot as plt
import time


# Constants for the number of transactions in 5 seconds against network size graph


# Gets values for the latency against network size graph
def latency_against_size(runs):
    avg_latencies = []
    for size in networkSizes:
        avg_latency = monte_carlo_run(size, runs, transaction=nTransactions)
        print("Avg Latency : ", avg_latency)
        avg_latencies.append(avg_latency)
    return avg_latencies

# Gets values for the latency against numberOfTransactions per user graph
def latency_against_transactions(runs):
    avg_latencies = []
    for transaction in transactions:
        avg_latency = monte_carlo_run(network_size, runs, transaction=transaction)
        print("Avg Latency : ", avg_latency)
        avg_latencies.append(avg_latency)
    return avg_latencies

def transactions_against_size(runs):
    avg_transactions = []
    for size in networkSizes:
        avg_transaction = monte_carlo_run(size, runs, throughput=True)
        print("Avg Transactions : ", avg_transaction)
        avg_transactions.append(avg_transaction)
    return avg_transactions


def monte_carlo_run(size,  runs, transactions=0, throughput=False):
    total = 0
    for i in range(runs):
        print("Network Size ", size, "nTransactionsPerUser", transactions, "run ", i + 1)
        total += get_avg_stat(size, transactions=transactions, throughput=throughput)
    return total/runs

def get_avg_stat(size, transactions=0, throughput=False):
    stats = []
    userList = []
    for i in range(size):
        response = addUser(i)
        if response and response["success"]:
            token = response["token"]
            user = User(token, init_value=1000, size=size, amount=1,
                        nTransactions=transactions, stats=stats,
                        throughput=throughput)
            user.start()
            time.sleep(3)
            userList.append(user)
        else:
            print(response)
    for user in userList: user.join()
    avgStat = sum(stats)/len(stats)
    # print("List ", stats)
    # print("avg ", avgStat)
    return avgStat

def plot_latency_size(avg_latencies, x, xLabel='Number of users', yLabel="Average Latency / ms"
                      , title=f"Average Latency against Number of users"):
    plt.plot(x, avg_latencies)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

if __name__ == '__main__':
    # Constants for the latency against network size graph
    # nTransactions = 5
    networkSizes = [2, 10, 25, 50, 100, 200]
    # avg_latencies = latency_against_size(10)
    # plot_latency_size(avg_latencies, networkSizes)
    #----------------------------------------------------------------------------------------------------------

    # # Constants for the latency against numberOfTransactions per user graph
    # network_size = 5
    # transactions = [5, 10, 25, 50, 75, 100, 150, 200] # each value represents the number of transactions per user for an experiment
    # avg_latencies = latency_against_transactions(10)
    # plot_latency_size(avg_latencies, transactions, xLabel='Number of transactions per user', yLabel="Average Latency / ms"
    #                   , title='Average Latency against Number of Users per transaction')
    # #----------------------------------------------------------------------------------------------------------
    networkSizes = [500, 1000]
    avg_transactions = transactions_against_size(1)
    plot_latency_size(avg_transactions, networkSizes, xLabel='Number of users', yLabel="avg number of transactions in 10 seconds", title='Throughput against number of users')


