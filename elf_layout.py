#!/usr/bin/env python

import sys, os, time, random
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt

VMAJOR=1
VMINOR=0

def banner(prog):
    print "%s version %d.%d"%(prog, VMAJOR, VMINOR)

def usage(prog):
    print "Usage: %s --version\tPrint current version."%(prog)
    print "       %s --help\tPrint this message."%(prog)
    print "       %s [--all] [--filter=X] [--label=str ...] filename.elf\tAnalyze ELF file."%(prog)
    print "       \t--all: display all part of the ELF, not just OBJECTs."
    print "       \t--filter=X: do not display part that exceed X% of the total."
    print "       \t--label=str: compute the space used between labels str_start and str_end."
    print "       \t\tCan be used several times."


def get_size(s):
    if len(s) >= 3:
        if s[1] == 'x':
            return int(s, 16)
        elif s[1] == 'b':
            return int(s, 2)
        elif s[1] == 'o':
            return int(s, 8)
        else:
            return int(s)
    else:
        return int(s)

def get_color(i):
    if i == 0:
        return (random.random(), 1, 0.5)
    elif i == 1:
        return (0.5, random.random(), 1)
    else:
        return (1, 0.5, random.random())


if len(sys.argv) <= 1:
    usage(sys.argv[0])

if sys.argv[1] == "--version":
    banner(sys.argv[0])
    sys.exit(0)

if sys.argv[1] == "--help":
    usage(sys.argv[0])
    sys.exit(0)

random.seed(time.time())

args = sys.argv[1:]
show_all = 0
top_filter = 1
filename = ""
label_start = {}
label_end = {}

while len(args) > 0:
    head = args.pop(0)
    if head == "--all":
        show_all = 1
    elif "--filter=" in head:
        value = get_size(head.split('=')[1])
        if value < 0:
            value = 0
        elif value >= 100:
            value = 100
        top_filter = float(value)/100.0
    elif "--label=" in head:
        pattern = head.split('=')[1]
        label_start[pattern] = 0
        label_end[pattern] = 0
    elif len(head) >= 1 and head[0]=='-':
        print "Unsupported option: %s"%(head)
        sys.exit(1)
    else:
        filename = head
        break

(stdout, stderr) = Popen(["readelf", "-s", filename], stdout=PIPE).communicate()
if not (stderr == None):
    print "readelf invocation failed: %s"%stderr
    sys.exit(1)

symbols = {}
lines = stdout.split('\n')[3:]
total_size = 0
to_skip = ["SECTION", "NOTYPE", "FILE", "FUNC" ]
# skip the first 3 lines we don't care
for line in lines:
    tokens = line.split()
    if len(tokens) == 0:
        continue
    addr = get_size("0x"+tokens[1])

    if len(tokens) >= 8:
        name = tokens[7]
    else:
        name = "<noname>"

    size = get_size(tokens[2])
    typ  = tokens[3]

    if name.endswith('_start'):
        name = name[:-6]
        if name in label_start.keys():
            label_start[name] = addr
    elif name.endswith('_end'):
        name = name[:-4]
        if name in label_end.keys():
            label_end[name] = addr
    elif show_all == 0:
        if typ in to_skip:
            continue
    total_size += size
    if name in symbols.keys():
        symbols[name] += size
    else:
        symbols[name] = size

add_labels = {}
for name in label_start.keys():
    n = label_end[name] - label_start[name]
    total_size += n
    add_labels[name] = n

print "Total size is %d"%(total_size)
# Slices are ordered and plotted counter-clockwise
labels = []
sizes = []
colors = []
explode = []

selector = 0

for (k,v) in symbols.iteritems():
    f = float(v) / float(total_size)
    if f <= top_filter:
        labels.append(k)
        sizes.append(v)
        colors.append(get_color(selector))
        explode.append(0.2)
        selector += 1
        selector %= 3
    else:
        print "Hiding %s (size=%d) which is %d%% of the total."%(k,v,int(f*100))

for (k,v) in add_labels.iteritems():
    f = float(v) / float(total_size)
    if f <= top_filter:
        labels.append(k)
        sizes.append(v)
        colors.append(get_color(selector))
        explode.append(0.5)
        selector += 1
        selector %= 3
    else:
        print "Hiding %s (size=%d) which is %d%% of the total."%(k, v, int(f*100))

plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
plt.axis('equal')

plt.show()

