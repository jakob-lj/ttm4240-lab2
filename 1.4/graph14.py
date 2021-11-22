# Using datetime as time will base on 1970-1-1 anyways
import datetime
import matplotlib.pyplot as plt


fileStream = open("data/1.4.dat", "r")

# Start End Sif SrcIPaddress SrcP DIf DstIPaddress DstP P Fl Pkts Octets


class LINE_INDEX:
    START = 0
    END = 1
    SOURCE_INTERFACE = 2
    SORUCE_IP = 3
    DESTINATION_INTERFACE = 4
    DESTINATION_IP = 5
    DESTIONATION_PORT = 6
    P = 7
    FL = 8
    PACKETS = 9
    OCTETS = 10


class IP_DOMAIN_INFO:
    IPERF_SERVER = "10.0.1.1"
    HAS_SERVER = "10.0.1.2"
    IPERF_CLIENT = "10.0.2.1"
    HAS_CLIENT = "10.0.2.2"


def formatLine(line):
    return line.strip().split()


fileData = [formatLine(x) for x in fileStream.readlines()]

fileStream.close()

firstLine = fileData[0]
lastLine = fileData[-1]

startClock = firstLine[LINE_INDEX.START][5:]
startClockTime = datetime.datetime.strptime(startClock, "%H:%M:%S.%f")


def clockToDatetime(clock):
    return datetime.datetime.strptime(clock[5:], "%H:%M:%S.%f")


def roundToNearestFive(numb):
    base = 5
    return base * round(numb / base)


def clockToSecOffset(clock):
    secOffset = roundToNearestFive(
        (clockToDatetime(clock) - startClockTime).seconds)
    return secOffset


def requestTimeInMillis(data):
    return int((clockToDatetime(data[LINE_INDEX.END]) - clockToDatetime(data[LINE_INDEX.START])).microseconds)


class InterstingFields:
    REQUEST_TIME = "requestTimeMicros"
    REQUEST_PKTS = "requestPackets"
    REQUEST_OCTETS = "requestOctets"


def extractInterstingData(data):
    return {
        InterstingFields.REQUEST_TIME: requestTimeInMillis(data),
        InterstingFields.REQUEST_PKTS: int(data[LINE_INDEX.PACKETS]),
        InterstingFields.REQUEST_OCTETS: int(data[LINE_INDEX.OCTETS])
    }


class DataGroupings:
    HAS_TO_CLIENT = "hasToClient"
    HAS_FROM_CLIENT = "hasFromClient"
    IPERF_TO_CLIENT = "iperfToClient"
    IPERF_FROM_CLIENT = "iperfFromClient"


dataGroupedByOperationAnd = {
    DataGroupings.IPERF_TO_CLIENT: {},
    DataGroupings.IPERF_FROM_CLIENT: {},
    DataGroupings.HAS_TO_CLIENT: {},
    DataGroupings.HAS_FROM_CLIENT: {},


}

for data in fileData:
    if (data[LINE_INDEX.SORUCE_IP] == IP_DOMAIN_INFO.HAS_SERVER):
        dataToModify = dataGroupedByOperationAnd[DataGroupings.HAS_TO_CLIENT]
    elif (data[LINE_INDEX.SORUCE_IP] == IP_DOMAIN_INFO.HAS_CLIENT):
        dataToModify = dataGroupedByOperationAnd[DataGroupings.HAS_FROM_CLIENT]
    elif (data[LINE_INDEX.SORUCE_IP] == IP_DOMAIN_INFO.IPERF_SERVER):
        dataToModify = dataGroupedByOperationAnd[DataGroupings.IPERF_TO_CLIENT]
    elif (data[LINE_INDEX.SORUCE_IP] == IP_DOMAIN_INFO.IPERF_CLIENT):
        dataToModify = dataGroupedByOperationAnd[DataGroupings.IPERF_FROM_CLIENT]

    interstingData = extractInterstingData(data)

    try:
        dataToModify[str(
            clockToSecOffset(data[LINE_INDEX.START])).append(interstingData)]
    except:
        dataToModify[str(
            clockToSecOffset(data[LINE_INDEX.START]))] = [interstingData]


def groupBySeconds(dictElementArray):
    resultdict = {}
    dictElementKeys = [int(x) for x in dictElementArray]

    sortedDictElementKeys = [str(x) for x in sorted(dictElementKeys)]

    for element in sortedDictElementKeys:

        result = {
            InterstingFields.REQUEST_TIME: 0,
            InterstingFields.REQUEST_PKTS: 0,
            InterstingFields.REQUEST_OCTETS: 0
        }

        for innerEl in dictElementArray[element]:
            result[InterstingFields.REQUEST_TIME] += innerEl[InterstingFields.REQUEST_TIME]
            result[InterstingFields.REQUEST_PKTS] += innerEl[InterstingFields.REQUEST_PKTS]
            result[InterstingFields.REQUEST_OCTETS] += innerEl[InterstingFields.REQUEST_OCTETS]

        result[InterstingFields.REQUEST_TIME] = result[InterstingFields.REQUEST_TIME] / \
            len(dictElementArray[element])
        result[InterstingFields.REQUEST_PKTS] = result[InterstingFields.REQUEST_PKTS] / \
            len(dictElementArray[element])
        result[InterstingFields.REQUEST_OCTETS] = result[InterstingFields.REQUEST_OCTETS] / \
            len(dictElementArray[element])

        resultdict[element] = result

    return resultdict


class PlotterReadyData:
    X = 0
    Y = 1


def getPlotDataByDataGroupAndInterstingField(datagroup, interstingField):
    goupredData = groupBySeconds(
        dataGroupedByOperationAnd[datagroup])

    x = [int(element) for element in goupredData]
    y = [int(
        goupredData[element][interstingField]) for element in goupredData]

    return x, y


def getTitleFromGroupAndField(group, field):
    if(group == DataGroupings.IPERF_TO_CLIENT):
        title = "Iperf ingress"

    elif (group == DataGroupings.IPERF_FROM_CLIENT):
        title = "Iperf egress"
    elif (group == DataGroupings.HAS_TO_CLIENT):
        title = "Has ingress"
    else:
        title = "Has egress"

    titleType = ""
    if (field == InterstingFields.REQUEST_OCTETS):
        titleType = "request octets"
    elif (field == InterstingFields.REQUEST_PKTS):
        titleType = "request packets"
    elif (field == InterstingFields.REQUEST_TIME):
        titleType = "request time"

    title += " - " + titleType

    return title


def getYLabelFromField(field):
    if (field == InterstingFields.REQUEST_TIME):
        return "Micro seconds"
    elif (field == InterstingFields.REQUEST_PKTS):
        return "Number of packets"
    elif (field == InterstingFields.REQUEST_OCTETS):
        return "Number of octets"


def plot(group, field):
    plotterData = getPlotDataByDataGroupAndInterstingField(group, field)
    plt.plot(plotterData[PlotterReadyData.X],
             plotterData[PlotterReadyData.Y])

    title = getTitleFromGroupAndField(group, field)

    plt.title(title)
    plt.legend([title])

    plt.xlabel("Seconds")
    plt.ylabel(getYLabelFromField(field))

    plt.savefig("plots/%s/%s.png" % (group, field))

    plt.show()


def plotCombination(group1, group2, field):

    title = getTitleFromGroupAndField(
        group1, field) + " combined with " + getTitleFromGroupAndField(group2, field)

    plotterData1 = getPlotDataByDataGroupAndInterstingField(group1, field)
    plt.plot(plotterData1[PlotterReadyData.X],
             plotterData1[PlotterReadyData.Y], label=getTitleFromGroupAndField(group1, field))

    plotterData2 = getPlotDataByDataGroupAndInterstingField(group2, field)
    plt.plot(plotterData2[PlotterReadyData.X],
             plotterData2[PlotterReadyData.Y], label=getTitleFromGroupAndField(group2, field))

    plt.xlabel("Seconds")
    plt.ylabel(getYLabelFromField(field))

    plt.title(title)
    plt.legend([getTitleFromGroupAndField(group1, field),
               getTitleFromGroupAndField(group2, field)])

    plt.savefig("plots/combinations/%s.png" % (group1 + group2 + field))

    plt.show()


plotGroups = [DataGroupings.IPERF_TO_CLIENT, DataGroupings.IPERF_FROM_CLIENT,
              DataGroupings.HAS_FROM_CLIENT, DataGroupings.HAS_TO_CLIENT]
plotFields = [InterstingFields.REQUEST_PKTS,
              InterstingFields.REQUEST_TIME, InterstingFields.REQUEST_OCTETS]

for group in plotGroups:
    for field in plotFields:
        plot(group, field)

plotCombination(DataGroupings.IPERF_TO_CLIENT,
                DataGroupings.HAS_TO_CLIENT, InterstingFields.REQUEST_PKTS)
plotCombination(DataGroupings.HAS_FROM_CLIENT,
                DataGroupings.IPERF_FROM_CLIENT, InterstingFields.REQUEST_PKTS)

plotCombination(DataGroupings.IPERF_TO_CLIENT,
                DataGroupings.HAS_TO_CLIENT, InterstingFields.REQUEST_OCTETS)
plotCombination(DataGroupings.HAS_FROM_CLIENT,
                DataGroupings.IPERF_FROM_CLIENT, InterstingFields.REQUEST_OCTETS)

plotCombination(DataGroupings.HAS_FROM_CLIENT,
                DataGroupings.HAS_TO_CLIENT, InterstingFields.REQUEST_OCTETS)

plotCombination(DataGroupings.HAS_FROM_CLIENT,
                DataGroupings.HAS_TO_CLIENT, InterstingFields.REQUEST_PKTS)

plotCombination(DataGroupings.IPERF_TO_CLIENT,
                DataGroupings.IPERF_FROM_CLIENT, InterstingFields.REQUEST_PKTS)

plotCombination(DataGroupings.IPERF_TO_CLIENT,
                DataGroupings.IPERF_FROM_CLIENT, InterstingFields.REQUEST_OCTETS)
