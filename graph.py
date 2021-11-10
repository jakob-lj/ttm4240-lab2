import matplotlib.pyplot as plt

graphs = "1.2"


def formatLine(line):
    return float(line.split()[-1])


inFile = open("data/%s/in.5" % graphs)

inData = inFile.readlines()

inFile.close()


outFile = open("data/%s/out.5" % graphs)
outData = outFile.readlines()
outFile.close()

outAttributes = [formatLine(line) for line in outData]

inAttributes = [formatLine(line) for line in inData]

x = [5*x for x in range(len(inAttributes))]

plt.plot(x, inAttributes, label="In")
plt.plot(x, outAttributes, label="Out")
plt.legend()
plt.savefig("graphs/" + graphs + ".png")
plt.show()
