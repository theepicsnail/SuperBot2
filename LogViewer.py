import os
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, NONE = range(0, 9)
from sys import argv

if len(argv) == 1:
    print "Usage: %s [-C] File1 File2..."
    print " -C    Do not print with colors"
    exit(1)
NoColors = argv[1] == "-C"
if NoColors:
    argv = argv[1:]  # deletes wrong arg, but the first arg isn't used anyway


def Color(bold=0, fg=NONE, bg=NONE):
    global NoColors
    if NoColors:
        return ""
    return "\033[%i;%i;%im" % (bold, fg + 30, bg + 40)


lines = []
import re
basePath = re.compile("^(.*\\.log)(\\.\\d+)?$")
logName = re.compile(".*/(.*?)(\\.\\d+)?$")
sortID = 0  # not actually of value
            # only used to keep items in the same ms in order


def getSortID():
    global sortID
    sortID += 1
    return sortID

pids = []


def getPIDColor(pid):
    global pids
    try:
        return pids.index(pid) % 7 + 1
    except:
        num = len(pids) % 7 + 1
        pids.append(pid)
    return num


def handleLog(path, num):
    global lines

    prefix = Color(0, 0, num) + "%35s|" % logName.match(path).groups()[0]
    r = file(path, "r")
    for line in r:
        data = line.split("|", 4)
        head = Color(0, 0, getPIDColor(data[1])) + data[1] + Color(0, 0, num) +
        " | " + data[2] + " | " + data[3]

        lines += [(data[0], getSortID(), head, data[-1][:-1], prefix)]

if __name__ == "__main__":

    bases = []
    for files in argv[1:]:
        m = basePath.match(files).groups()[0]
        try:
            num = bases.index(m) % 7 + 1
        except:
            num = len(bases) % 7 + 1
            bases += [m]
        handleLog(files, num)

    lines.sort()
    for date, sortID, args, msg, prefix in lines:
        print "%s%s | %s" % (prefix, date, args)
        for m in msg.split("\t"):
            print "%s    %s" % (prefix, m)
    print Color()
