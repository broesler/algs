#!/home/broesler/anaconda3/bin/python3
#==============================================================================
#     File: day1.py
#  Created: 2018-12-05 19:59
#   Author: Bernie Roesler
#
"""
  Description: Advent of Code Day 1
"""
#==============================================================================

filename = "./data/input_1.dat"

# Challenge 1 + 2
freq = 0;       # initial frequency
file_reads = 0
# cumsum = [freq]  # for plotting only
d = dict()  # track seen values to look for repeats
found = False

# Read the file each time
while not found:
    file_reads += 1

    with open(filename, 'r') as fp:
        for line in fp:
            freq += int(line.rstrip())
            # cumsum.append(freq)

            # Check for repeats
            if freq in d:
                found = True
                repeat_freq = freq
                break
            else:
                d[freq] = True

        # Store the frequency at the end of the file
        if file_reads == 1:
            first_freq = freq

print(f'File frequency = {first_freq:d}')
print(f'Repeated freq. = {repeat_freq:d}')
print(f'Total file reads = {file_reads:d}')

#==============================================================================
#==============================================================================
