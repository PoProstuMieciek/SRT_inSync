import sys
import argparse
from pysrt import SubRipFile, SubRipItem, open
from datetime import time, timedelta
from typing import List

parser = argparse.ArgumentParser(description='Command line utility for checking if two subtitle files are in sync')
parser.add_argument('paths', metavar='PATH', type=str, nargs=2, help='path to subtitle file')
parser.add_argument('--verbose', '-v', help='verbose mode', action='store_true')
parser.add_argument('--diff', '-d', dest='diff', type=float, help='diff tolerance in seconds', default=2.5)

args = parser.parse_args()

def time_to_microseconds(t: time):
    delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
    return delta.total_seconds() * (10**6)

def time_diff(x: time, y: time):
    x_us = time_to_microseconds(x)
    y_us = time_to_microseconds(y)
    return y_us - x_us

def search_for_closest(target: time, search: SubRipFile):
    last_delta = timedelta(days=1).total_seconds() * (10**6)
    last_delta_index = len(search)-1

    for i in range(len(search)):
        entry: SubRipItem = search[i]
        diff = time_diff(target, entry.start.to_time())

        if(abs(diff) < last_delta):
            last_delta = abs(diff)
            last_delta_index = i
    
    return search[last_delta_index]


first = open(args.paths[0], encoding='utf-8')
second = open(args.paths[1], encoding='utf-8')

print(first.path, second.path, sep='\n')

shorter, longer = None, None
if(len(first) > len(second)):
    longer = first
    shorter = second
else:
    longer = second
    shorter = first

correct, incorrect = 0, 0
for i in range(len(longer)):
    current: SubRipItem = longer[i]
    
    closest: SubRipItem = search_for_closest(current.start.to_time(), shorter)
    diff = time_diff(current.start.to_time(), closest.start.to_time())
    diff_sec = diff / (10**6)

    if abs(diff_sec) < args.diff: correct += 1
    else: incorrect += 1

    if args.verbose:
        print(current, closest, diff_sec, '\n', sep='\n')

percent_correct = correct / ( correct + incorrect ) * 100
print('\n', correct, '/', incorrect, '\n', percent_correct, '% correct', '\n', sep='')