A script for running the q-learner.

It's not pretty, it's probably buggy, but, you know...

run_mission.py
This file is to run the agent for data collection.
You can run any number of locations, any number of times.
To change the number of times, change the for in in range(1): to... whatever you want.
It will dump a .p file of the mission uuids at a given hiker location, if you want to recover them for a query.
It will try and avoid mountains so long as the associated .xml file has the a path to the particular location.
It DOES NOT navigate without <path>.  It's designed to fly in same locations the drone was trained on.

there are a few variables to pay attention to:
combinations: this is the product of hiker_positions_x, hiker_positions_y but can be set manually (as I'm currently using it).
version_number: this is the version number (ql_v, local_v) of the drone.

It's currently setup to run the drone version 3.0 (local_v{}).

It's recommended that you read the code before running.

Oh, it also starts as thread that it never kills (bad_navigation.py)

There are other useful tools in there (useful for me, anyway).  They query the database, make dictionaries of q-learner portions of the mission, make act-r chunks.
If you're curious about any of that, ask.