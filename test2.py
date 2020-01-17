from collections import deque
import itertools


from fitparse import FitFile


fitfile = FitFile("./test.fit")

# Get all data messages that are of type record
for record in fitfile.get_messages("record"):

    # Go through all the data entries in this record
    for record_data in record:

        # Print the records name and value (and units if it has any)
        if record_data.units:
            print(
                " * %s: %s %s"
                % (record_data.name, record_data.value, record_data.units,)
            )
        else:
            print(" * %s: %s" % (record_data.name, record_data.value))
    print()
