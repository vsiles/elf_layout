#!/usr/bin/env python

import sys, os, time, random
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(prog='PROG')
parser = argparse.ArgumentParser(description='Analyze ELF file')
parser.add_argument('filename', metavar="ELF", help="name of the ELF file")
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-a', '--all', action="store_true", help="display all part of the ELF, not just OBJECTs.")
parser.add_argument('-f', '--filter', type=int, metavar = "X", help="do not display part that exceed X%% of the total.")
parser.add_argument('-l', '--label', action='append', help="compute the space used between labels str_start and str_end.Can be used several times.")

args = parser.parse_args()


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


random.seed(time.time())

top_filter = 1
filename = args.filename
label_start = {}
label_end = {}

if args.filter is not None:
    value = int(args.filter)
    if value < 0:
        value = 0
    elif value >= 100:
        value = 100
    top_filter = float(value)/100.0

if args.label is not None:
    for pattern in args.label:
        label_start[pattern] = 0
        label_end[pattern] = 0


(stdout, stderr) = Popen(["file", filename], stdout=PIPE).communicate()
if not (stderr == None):
    print "file invocation failed: %s"%stderr
    sys.exit(1)

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
    addr = int(tokens[1], 16)

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
    elif args.all == 0: 
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

print "Total size is %d octets."%(total_size)
# Slices are ordered and plotted counter-clockwise
labels = []
sizes = []
colors = []
explode = []

selector = 0

total_showed_size = 0
for (k,v) in symbols.iteritems():
    f = float(v) / float(total_size)
    if f <= top_filter:
        total_showed_size += v
        labels.append(k)
        sizes.append(v)
        colors.append(get_color(selector))
        explode.append(0)
        selector += 1
        selector %= 3
    else:
        print "Hiding %s (size=%d octets) which is %d%% of the total."%(k,v,int(f*100))

for (k,v) in add_labels.iteritems():
    f = float(v) / float(total_size)
    if f <= top_filter:
        total_showed_size += v
        labels.append(k)
        sizes.append(v)
        explode.append(0)
        colors.append(get_color(selector))
        selector += 1
        selector %= 3
    else:
        print "Hiding %s (size=%d octets) which is %d%% of the total."%(k, v, int(f*100))

print "Total displayed size is %d octets."%(total_showed_size)


for i in xrange(len(explode)):
    f = float(sizes[i]) / float(total_showed_size)
    if f < 0.01:
        explode[i] = 1 - f
    else:
        explode[i] = 0.2

plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
plt.axis('equal')

plt.show()

