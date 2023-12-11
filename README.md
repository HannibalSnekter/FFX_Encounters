# FFX Encounter Time Script

This script is designed to estimate the amount of time spent in encounters for a speedrun of Final Fantasy X.

## Output

The script outputs two CSV files which contain estimates of encounter counts on each screen and estimates of time cost of encounters on each screen.

The outputs contain a record for each seed under each combination of the following options:

- Forcing an encounter at the end of one screen
- Lord Ochu on way into Kilika
- Lord Ochu on way out of Kilika
- Luck Sphere in / out of kilika
- Mi'ihen Agency Simulation Encounter
- Old Road Gate Simulation Encounter
- Extra Sandragora (Intentional Sandragora Skip failue)

Note: The script doesn't currently consider both Lord Ochu in and Lord Ochu out as a valid combination.

This makes for 1728 records for each seed at present.

## Functionality

The script currently accounts for the following time costs:

- Time to load into and flee from each encounter
- Time cost from outspeeds based on the probability of outspeed occuring
- Time cost from ambush guaranteed outspeeds
- Time cost / gain from Baaj Sahagins ambush / pre-Empt
- Time cost / gain from Geos pre-empt / ambush
- Time to find a Ghost

The script doesn't currently account for the following:

- Time cost / gain from Forced Piranhas ambush / pre-empt
- Time cost / gain from Tros ambush / pre-empt
- Variable load in times of different enemies. E.g. Some flying enemies seem to cause a longer delay before allowing actions to be taken to Flee.
- Risk of ruin due to ambush game over

## Assumptions and Limitations

The script makes the following assumptions:

- Movement on each screen is equivalent to the optimal path, yielding the fewest random encounter (RNG0) rolls
- A random encounter has a base time of 10 seconds to load into the encounter and flee. An extra 10 seconds is added to Maze Larva encounters to account for summoning and attacking with Ixion
- Routing is with Terra skip

The script has the following limitations:

- The script doesn't account for worse movement enabling a reduced number of encounters throughout the run. This is partially mitigated by scenarios for forced encounters at the end of each screen.
- The script only cares about what is theoretically the fastest seed and gives no care for how dangerous the encounters could be. A consequence of this is that a seed could have low encounter count and few outspeeds but multiple Thunder Plains ambushes and thus would be higher risk.