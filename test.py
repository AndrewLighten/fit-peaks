from fitparse import FitFile
from collections import deque
import itertools


def moving_average(iterable, n):
    # http://en.wikipedia.org/wiki/Moving_average
    it = iter(iterable)
    # create an iterable object from input argument
    d = deque(itertools.islice(it, n - 1))
    # create deque object by slicing iterable
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / n


fitfile = FitFile("./test.fit")

power = []

# Get all data messages that are of type record
for record in fitfile.get_messages("record"):

    # Go through all the data entries in this record
    for record_data in record:

        if record_data.name == "power":
            power.append(int(record_data.value))

max_5s = int(max(moving_average(power, 5)))
print(f"Peak 5 second power .... {max_5s}")

max_30s = int(max(moving_average(power, 30)))
print(f"Peak 30 second power ... {max_30s}")

max_60s = int(max(moving_average(power, 60)))
print(f"Peak 60 second power ... {max_60s}")

max_5 = int(max(moving_average(power, 60 * 5)))
print(f"Peak 5 minute power .... {max_5}")

max_10 = int(max(moving_average(power, 60 * 10)))
print(f"Peak 10 minute power ... {max_10}")

max_20 = int(max(moving_average(power, 60 * 20)))
print(f"Peak 20 minute power ... {max_20}")

max_30 = int(max(moving_average(power, 60 * 30)))
print(f"Peak 30 minute power ... {max_30}")

max_60 = int(max(moving_average(power, 60 * 60)))
print(f"Peak 60 minute power ... {max_60}")

max_120 = int(max(moving_average(power, 60 * 120)))
print(f"Peak 120 minute power .. {max_120}")
