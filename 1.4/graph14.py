
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


def formatLine(line):
    return line.strip().split()


fileData = [formatLine(x) for x in fileStream.readlines()]

fileStream.close()

firstLine = fileData[0]
lastLine = fileData[-1]

print(firstLine[LINE_INDEX.PACKETS])
