from user import User, addUser, addCryptoUser
import statistics
from dsdb import db
import matplotlib.pyplot as plt

# Gets values for the latency against transactions graph
def latency_against_transactions(runs):
    means = []
    stds = []
    for size in nUsers:
        mean, std = monte_carlo_run(size, runs, transactions=nTransactions)
        means.append(mean)
        stds.append(std)
        print("mean Latency : ", mean)
        print("mean std : ", std)
    return mean, std
#
# # Gets values for the latency against numberOfTransactions per user graph
# def latency_against_transactions(runs):
#     avg_latencies = []
#     for transaction in transactions:
#         avg_latency = monte_carlo_run(network_size, runs, transactions=transaction)
#         print("Avg Latency : ", avg_latency)
#         avg_latencies.append(avg_latency)
#     return avg_latencies
#
# def transactions_against_size(runs):
#     avg_transactions = []
#     for size in networkSizes:
#         avg_transaction = monte_carlo_run(size, runs, throughput=True)
#         print("Avg Transactions : ", avg_transaction)
#         avg_transactions.append(avg_transaction)
#     return avg_transactions


def monte_carlo_run(size,  runs, transactions=0, throughput=False):
    latencies = []
    for i in range(runs):
        print("Network Size ", size, "nTransactionsPerUser", transactions, "run ", i + 1)
        latency = get_avg_stat(size, transactions=transactions, throughput=throughput)
        latencies.append(latency)
    mean = statistics.mean(latencies)
    std = statistics.stdev(latencies)
    return mean, std

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
            # time.sleep(3)
            userList.append(user)
        else:
            print(response)
    for user in userList: user.join()
    avgStat = sum(stats)/len(stats)
    return avgStat

# def measure_dsdb(spent_tokens):
#     result = []
#     response = addUser("root")
#     if response and response["success"]:
#         token = response["token"]
#         dataBase = db(token)
#         for token in spent_tokens:
#             dataBase.AddToken(str(token))
#             r = dataBase.FindToken(token)
#             result.append(r["latency"])
#     else:
#         print("Failed to Measure dsdb")
#     return result
#
#
# def plot_latency_size(avg_latencies, x, xLabel='Number of users', yLabel="Average Latency / ms"
#                       , title=f"Average Latency against Number of users"):
#     plt.plot(x, avg_latencies)
#     plt.xlabel(xLabel)
#     plt.ylabel(yLabel)
#     plt.title(title)
#     plt.show()

def plotLine(x, y, yerr, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.errorbar(x, y,yerr=yerr, fmt='-o')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.show()

#TODO: initialise a batch of users for each one of the msbs
def addUsers(num_users: int):
    for i in range(num_users):
        addCryptoUser(str(i), str(i), 'msb1')
    # TODO: in order to test the system with multiple msbs we need a db to store keys
    # for i in range(num_users):
    #     addCryptoUser(str(i), str(i), 'msb2')


if __name__ == '__main__':
    # Constants for the latency against number of transactions graph
    nTransactions = 5
    nUsers = [2, 10, 25, 50, 100, 200]
    means, stds = latency_against_transactions(3)
    transactions = [nTransactions * i for i in nUsers]
    plotLine(transactions, means, stds, "Latency against number of transactions", "Number of Transactions", "Average Latency/ms")
    # avg_latencies = latency_against_size(10)
    # plot_latency_size(avg_latencies, networkSizes)
    # #----------------------------------------------------------------------------------------------------------
    # #
    # # # # Constants for the latency against numberOfTransactions per user graph
    # network_size = 5
    # transactions = [5, 10, 25, 50, 75, 100, 150, 200] # each value represents the number of transactions per user for an experiment
    # avg_latencies = latency_against_transactions(10)
    # plot_latency_size(avg_latencies, transactions, xLabel='Number of transactions per user', yLabel="Average Latency / ms"
    #                   , title='Average Latency against Number of Users per transaction')
    #
    # # # #----------------------------------------------------------------------------------------------------------
    # avg_transactions = transactions_against_size(1)
    # plot_latency_size(avg_transactions, networkSizes, xLabel='Number of users', yLabel="avg number of transactions in 10 seconds", title='Throughput against number of users')
    #
    # # #------------------------------------------------------------------------------------------------------------
    # spent_tokens = [2, 5, 10, 20, 50, 100, 200, 400, 800, 1000, 2000]
    # result = measure_dsdb(spent_tokens)
    # print(result)


    # Instantiating a user
    # response = addUser("sam")
    # if response and response["success"]:
    #     token = response["token"]
    #     user = User(token, init_value=1000, size=None, amount=1, stats=[])
    #     r1 = user.addAsset(1000)
    #     r2 = user.removeAsset(200)
    #     print("addAsser : ", r1)
    #     print("removeAsset: ", r2)




