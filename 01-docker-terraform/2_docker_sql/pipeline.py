"""A very basic pipeline script that takes a day as an argument and prints it out"""

import sys

import pandas as pd

print(sys.argv)

day = sys.argv[1]

# some fancy stuff with pandas

print(f"job finished successfully for day = {day}")
