import matplotlib.pyplot as plt

graphs = "1.2"


def formatLine(line):
    return float(line.split()[-1])


def plotFile(plt, fileName):
    if ("in" in fileName):
        legend = "Interface %s: ifInUcastPkts" % fileName.split(".")[-1]
    else:
        legend = "Interface %s: ifOutUcastPkts" % fileName.split(".")[-1]
    with open("data/%s/%s" % (graphs, fileName)) as f:
        data = f.readlines()
        attributes = [formatLine(line) for line in data]

        x = [5*x for x in range(len(attributes))]

        plt.plot(x, attributes, label=legend)


#plotFile(plt, "in.6")
#plotFile(plt, "in.7")
#plotFile(plt, "out.6")
#plotFile(plt, "out.7")
plotFile(plt, "in.5")
plotFile(plt, "out.5")

plt.title("Reuqests per 5 seconds")
plt.xlabel("Time [sec]")
plt.ylabel("Number of requests per 5 sec")
plt.legend()
plt.savefig("graphs/" + graphs + ".png")
plt.show()
