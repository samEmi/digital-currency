from user import User, addUser, addCryptoUser
import statistics
import plotly.graph_objects as go
import time


def latency_against_transactions(runs, nUsers):
    means = []
    stds = []
    for size in nUsers:
        mean, std = monte_carlo_run(size, runs)
        means.append(mean)
        stds.append(std)
    return means, stds

def monte_carlo_run(size,  runs, transactions=0):
    latencies = []
    for i in range(runs):
        print("Network Size ", size, "nTransactionsPerUser", transactions, "run ", i + 1)
        latency = get_avg_stat(size, transactions=transactions)
        latencies.append(latency)
    mean = statistics.mean(latencies)
    std = statistics.stdev(latencies)
    return mean, std

def get_avg_stat(size, transactions=0):
    stats = []
    userList = []
    for i in range(size):
        response = addUser(i)
        if response and response["success"]:
            token = response["token"]
            user = User(token, init_value=1000, size=size, amount=1,
                        nTransactions=transactions, stats=stats)
            user.start()
            userList.append(user)
        else:
            print(response)
    for user in userList: user.join()
    avgStat = sum(stats)/len(stats)
    return avgStat

def latency_nMSBs(nMSBs, runs):
    means = []
    stds = []
    for nMSB in nMSBs:
        mean, std = get_latency(nMSB, runs)
        means.append(mean)
        stds.append(std)
        print("mean ", mean)
        print("std ", std)
    return means, stds

def get_latency(nMSB, runs):
    msb = nMSB * runs
    latencies = []
    userList = []
    for i in range(nMSB + 1):
        response = addUser(msb + i)
        if response and response["success"]:
            token = response["token"]
            user = User(token, init_value=1000, size=100, amount=1,
                        nTransactions=runs, stats=latencies)
            user.start()
            userList.append(user)
            time.sleep(3)
        else:
            print(response)
    for user in userList: user.join()
    mean = statistics.mean(latencies)
    std = statistics.stdev(latencies)
    return mean, std


def throughput_nMSBs(nMSBs, runs):
    means = []
    stds = []
    for nMSB in nMSBs:
        tokens = [addUser(i)["token"] for i in range(nMSB)]
        mean, std = monteCalro(tokens, runs)
        means.append(mean)
        stds.append(std)
    return means, stds

def monteCalro(tokens, runs):
    throughputs = []
    for i in range(runs):
        throughputs.append(getThroughput(tokens))
    mean = statistics.mean(throughputs)
    std = statistics.stdev(throughputs)
    return mean, std

def getThroughput(tokens):
    stats = []
    users = [User(token, init_value=1000, size=100, amount=1, stats=stats, throughput=True)
             for token in tokens]
    for user in users:user.start()
    time.sleep(10)
    for user in users: user.stopped = True
    for user in users: user.join()
    return sum(stats)



# def get_pw_pw_stats(size, transactions=0, throughput=False):
#     means = []
#     stds = []
#     for i in range(num_users):
#         r = addCryptoUser(str(i), str(i), 'msb1')
#         token = r["token"]
#         user = User(token)
#         r = user.transfer_pw_to_acc(str(i), 1, 100)
#         mean = r["latency"]
#         std = r["std"]
#         means.append(mean)
#         stds.append(stds)
#     return means, stds




def plotExpA(x, y, y1, yerr, yerr1):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y,
                        mode='lines+markers',
                        name='MSB-MSB',
                        error_y=dict(
                type='data',
                array=yerr,
                visible=True)
        ))
    fig.add_trace(go.Scatter(x=x, y=y1,
                        mode='lines+markers',
                        name='PW-MSB',
                        error_y=dict(
                type='data',
                array=yerr1,
                visible=True)
                        ))
    fig.update_layout(title='Latency against number of transactions',
                      xaxis_title='Number of Transactions',
                      yaxis_title='Average Latency/ms')

    fig.show()


def plotExpB(x, y, yerr):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x, y=y,
        error_y=dict(type='data', array=yerr)
    ))
    fig.update_layout(title='Latency against number of MSBs',
                          xaxis_title='Number of MSBs',
                          yaxis_title='Average Latency/ms')
    fig.show()

def plotExpC(x, y, yerr):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x, y=y,
        error_y=dict(type='data', array=yerr)
    ))
    fig.update_layout(title='Throughput against the network size',
                          xaxis_title='Number of MSBs',
                          yaxis_title='Number of transactions in 10seconds/ms')
    fig.show()

#TODO: initialise a batch of users for each one of the msbs
def addUsers(num_users: int):
    for i in range(num_users):
        addCryptoUser(str(i), str(i), 'msb1')
    # TODO: in order to test the system with multiple msbs we need a db to store keys
    # for i in range(num_users):
    #     addCryptoUser(str(i), str(i), 'msb2')


if __name__ == '__main__':
    #Experiment A
    nTransactions = 5
    nUsers = [2, 10, 25, 50, 100, 200]
    means, stds = latency_against_transactions(10, nUsers)
    # means1, stds1 = get_pw_pw_stats(10)
    transactions = [nTransactions * i for i in nUsers]
    plotExpA(transactions, means, means, stds, stds)

    # Experiment B
    nMSBs = [1, 2, 3, 4, 5]
    means, stds = latency_nMSBs(nMSBs, 10)
    plotExpB(nMSBs, means, stds)

    # Experiment C
    nMSBs = [1, 2, 3, 4, 5]
    means, stds = throughput_nMSBs(nMSBs, 10)
    plotExpC(nMSBs, means, stds)





