import csv
import json
import os
import Rng

seed_rolls = []
skiplucksphere = False
killChocoboEater = False


def getNextRoll(index, rngArrays, rollIndexes):
    rollIndexes[index] += 1
    return rngArrays[index][rollIndexes[index]]

# options:
# 0x01 - Ochu In
# 0x02 - Luck Sphere Out (Default distances assume luck sphere obtained on way in)
# 0x04 - Ochu Out
# 0x08 - Mi'ihen Sim
# 0x10 - Old Road Sim
# 0x20 - Extra Sandragora

def runArea(areas: list, areaIndex: int, rng: list, rngIndex: list, forceFinalEncounter: bool, forceEncounterAreaName: str, area_times: list,
            area_encounters: list, kilikaKills: int, forcedEncounters: int, options: int, maxDistanceOverride: int = -1):
    areacount = 0
    areadict = areas[areaIndex]
    areaName = areadict["Name"]
    maxDistance = maxDistanceOverride if maxDistanceOverride >= 0 else areadict["Distance"]
    dangerValue = areadict["DangerValue"]
    graceperiod = dangerValue // 2
    formationcount = len(areadict["Formations"])

    # Start Total Distance at 1 because nothing happens at 0 distance
    totaldistance = 1
    currentdistance = areadict["StartSteps"]

    # Roll rng1 equal to the number of forced encounters that have occured since the last area

    rngIndex[1] = rngIndex[1] + (areadict["Forced Encounters"] - forcedEncounters)

    # Update forced encounters for this area
    forcedEncounters = areadict["Forced Encounters"]

    ambush = False
    preempt = False
    attackcount = 0.0
    firststrike = areadict["First Strike"]

    time_area = 0.0

    if areaName == "Old Road Screen 1" and (options & 0x08) == 0x08:
        rngIndex[1] = rngIndex[1] + 1
        time_area += 10.0

    if areaName == "Clasko Skip Screen 1" and (options & 0x10) == 0x10:
        rngIndex[1] = rngIndex[1] + 1
        time_area += 10.0

    # Iterate distance 1 unit at a time until max distance is reached
    while totaldistance <= maxDistance or forceFinalEncounter:

        if areaName == "Kilika In" and (options & 0x01) == 0x01 and totaldistance == 73:
            rngIndex[1] = rngIndex[1] + 1
            currentdistance = 0
            time_area += 10.0

        elif areaName == "Kilika Out" and (options & 0x04) == 0x04 and totaldistance == 74:
            rngIndex[1] = rngIndex[1] + 1
            currentdistance = 0
            time_area += 10.0

        # If distance since previous encounter is more than Grace Period check for encounter
        elif currentdistance > graceperiod:
            encounterchance = (currentdistance - graceperiod) * 256 // (4 * dangerValue)
            encounterroll = getNextRoll(0, rng, rngIndex) % 256
            if encounterroll < encounterchance:
                currentdistance = 0

                # Add base time for encounter and extra for Maze Larva
                areacount += 1
                time_area += 10.0
                if areaName == "Via Purifico (Land)": time_area += 10.0

                # Calculation formation and ambush / pre-empt
                formationroll = getNextRoll(1, rng, rngIndex) % formationcount
                formation = areadict["Formations"][formationroll]
                ambushroll = getNextRoll(1, rng, rngIndex) % 256

                if ambushroll < 32:
                    preempt = True
                elif ambushroll >= 223:
                    ambush = True

                # Calculate outspeeds
                if not (firststrike or preempt):
                    for enemy in formation:
                        if ambush:
                            attackcount = 1.0 + attacks[enemy]["ambushoutspeed"]
                        else:
                            attackcount = attacks[enemy]["outspeed"]
                        time_area += attackcount * attacks[enemy]["attacktime"]

                # Calculate max possible Kilika kills for speed spheres
                if areaName == "Kilika In" or areaName == "Kilika Out":
                    for enemy in formation:
                        if enemy == "dinonix":
                            kilikaKills += 1
                        elif enemy == "killer_bee":
                            kilikaKills += 2

                ambush = False
                preempt = False
                attackcount = 0.0

                if totaldistance > maxDistance and forceFinalEncounter:
                    forceFinalEncounter = False

        totaldistance += 1
        currentdistance += 1

    # Add time for extra Sandragora
    if areaName == "Bikanel (West Post-Sandragora 1)" and (options & 0x20) == 0x20:
        rngIndex[1] = rngIndex[1] + 1
        time_area += 10

    area_times = area_times + [time_area]
    area_encounters = area_encounters + [areacount]

    # If current area isn't the final area process the next area
    if areaIndex < len(areas) - 1:

        nextArea = areas[areaIndex + 1]["Name"]

        # Conditional processing for specific areas then general processing
        #
        # For Kilika In process each combination of Ochu In and Luck Sphere In/Out
        # For Kilika Out process each combination of Ochu Out and Luck Sphere In/Out conditional on Kilika In options
        # For Old Road Screen 1 process Mi'ihen simulation encounter options
        # For Clasko Skip Screen 1 process Old Road simulation encounter options
        # For Bikanel West (Post Teleport Sphere Sandragora) process extra Sandragora encounter options

        if nextArea == "Kilika In":
            if forceEncounterAreaName == "":
                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options,
                        )

                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options | 0x01,
                        maxDistanceOverride=205
                        )

                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options | 0x02,
                        maxDistanceOverride=141
                        )

                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options | 0x03,
                        maxDistanceOverride=149
                        )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options
                    )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options | 0x01,
                    maxDistanceOverride=205
                    )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options | 0x02,
                    maxDistanceOverride=141
                    )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options | 0x03,
                    maxDistanceOverride=149
                    )

        elif nextArea == "Kilika Out":
            if forceEncounterAreaName == "":
                # Don't want to run both Ochu In and Ochu Out
                if (options & 0x01) == 0x00:
                    if (options & 0x02) == 0x02:
                        runArea(areas=areas,
                                areaIndex=areaIndex + 1,
                                rng=rng,
                                rngIndex=rngIndex[:],
                                forceFinalEncounter=True,
                                forceEncounterAreaName=nextArea,
                                area_times=area_times,
                                area_encounters=area_encounters,
                                kilikaKills=kilikaKills,
                                forcedEncounters=forcedEncounters,
                                options=options,
                                maxDistanceOverride=212
                                )

                        runArea(areas=areas,
                                areaIndex=areaIndex + 1,
                                rng=rng,
                                rngIndex=rngIndex[:],
                                forceFinalEncounter=True,
                                forceEncounterAreaName=nextArea,
                                area_times=area_times,
                                area_encounters=area_encounters,
                                kilikaKills=kilikaKills,
                                forcedEncounters=forcedEncounters,
                                options=options | 0x04,
                                maxDistanceOverride=229
                                )
                    else:
                        runArea(areas=areas,
                                areaIndex=areaIndex + 1,
                                rng=rng,
                                rngIndex=rngIndex[:],
                                forceFinalEncounter=True,
                                forceEncounterAreaName=nextArea,
                                area_times=area_times,
                                area_encounters=area_encounters,
                                kilikaKills=kilikaKills,
                                forcedEncounters=forcedEncounters,
                                options=options,
                                maxDistanceOverride=165
                                )

                        runArea(areas=areas,
                                areaIndex=areaIndex + 1,
                                rng=rng,
                                rngIndex=rngIndex[:],
                                forceFinalEncounter=True,
                                forceEncounterAreaName=nextArea,
                                area_times=area_times,
                                area_encounters=area_encounters,
                                kilikaKills=kilikaKills,
                                forcedEncounters=forcedEncounters,
                                options=options | 0x04,
                                maxDistanceOverride=172
                                )
                else:
                    if (options & 0x02) == 0x02:
                        runArea(areas=areas,
                                areaIndex=areaIndex + 1,
                                rng=rng,
                                rngIndex=rngIndex[:],
                                forceFinalEncounter=True,
                                forceEncounterAreaName=nextArea,
                                area_times=area_times,
                                area_encounters=area_encounters,
                                kilikaKills=kilikaKills,
                                forcedEncounters=forcedEncounters,
                                options=options,
                                maxDistanceOverride=212
                                )
                    else:
                        runArea(areas=areas,
                                areaIndex=areaIndex + 1,
                                rng=rng,
                                rngIndex=rngIndex[:],
                                forceFinalEncounter=True,
                                forceEncounterAreaName=nextArea,
                                area_times=area_times,
                                area_encounters=area_encounters,
                                kilikaKills=kilikaKills,
                                forcedEncounters=forcedEncounters,
                                options=options,
                                maxDistanceOverride=165
                                )

            if (options & 0x01) == 0x00:
                if (options & 0x02) == 0x02:
                    runArea(areas=areas,
                            areaIndex=areaIndex + 1,
                            rng=rng,
                            rngIndex=rngIndex[:],
                            forceFinalEncounter=False,
                            forceEncounterAreaName=forceEncounterAreaName,
                            area_times=area_times,
                            area_encounters=area_encounters,
                            kilikaKills=kilikaKills,
                            forcedEncounters=forcedEncounters,
                            options=options,
                            maxDistanceOverride=212
                            )

                    runArea(areas=areas,
                            areaIndex=areaIndex + 1,
                            rng=rng,
                            rngIndex=rngIndex[:],
                            forceFinalEncounter=False,
                            forceEncounterAreaName=forceEncounterAreaName,
                            area_times=area_times,
                            area_encounters=area_encounters,
                            kilikaKills=kilikaKills,
                            forcedEncounters=forcedEncounters,
                            options=options | 0x04,
                            maxDistanceOverride=229
                            )
                else:
                    runArea(areas=areas,
                            areaIndex=areaIndex + 1,
                            rng=rng,
                            rngIndex=rngIndex[:],
                            forceFinalEncounter=False,
                            forceEncounterAreaName=forceEncounterAreaName,
                            area_times=area_times,
                            area_encounters=area_encounters,
                            kilikaKills=kilikaKills,
                            forcedEncounters=forcedEncounters,
                            options=options,
                            maxDistanceOverride=165
                            )

                    runArea(areas=areas,
                            areaIndex=areaIndex + 1,
                            rng=rng,
                            rngIndex=rngIndex[:],
                            forceFinalEncounter=False,
                            forceEncounterAreaName=forceEncounterAreaName,
                            area_times=area_times,
                            area_encounters=area_encounters,
                            kilikaKills=kilikaKills,
                            forcedEncounters=forcedEncounters,
                            options=options | 0x04,
                            maxDistanceOverride=172
                            )
            else:
                if (options & 0x02) == 0x02:
                    runArea(areas=areas,
                            areaIndex=areaIndex + 1,
                            rng=rng,
                            rngIndex=rngIndex[:],
                            forceFinalEncounter=False,
                            forceEncounterAreaName=forceEncounterAreaName,
                            area_times=area_times,
                            area_encounters=area_encounters,
                            kilikaKills=kilikaKills,
                            forcedEncounters=forcedEncounters,
                            options=options,
                            maxDistanceOverride=212
                            )
                else:
                    runArea(areas=areas,
                            areaIndex=areaIndex + 1,
                            rng=rng,
                            rngIndex=rngIndex[:],
                            forceFinalEncounter=False,
                            forceEncounterAreaName=forceEncounterAreaName,
                            area_times=area_times,
                            area_encounters=area_encounters,
                            kilikaKills=kilikaKills,
                            forcedEncounters=forcedEncounters,
                            options=options,
                            maxDistanceOverride=165
                            )

        elif nextArea == "Old Road Screen 1":
            if forceEncounterAreaName == "":
                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options,
                        )

                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options | 0x08
                        )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options,
                    )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options | 0x08
                    )

        elif nextArea == "Clasko Skip Screen 1":
            if forceEncounterAreaName == "":
                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options,
                        )

                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options | 0x10
                        )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options,
                    )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options | 0x10
                    )

        elif nextArea == "Bikanel (West Post-Sandragora 1)":
            if forceEncounterAreaName == "":
                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options,
                        )

                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options | 0x20,
                        maxDistanceOverride=45
                        )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options,
                    )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options | 0x20,
                    maxDistanceOverride=45
                    )

        else:
            if forceEncounterAreaName == "":
                runArea(areas=areas,
                        areaIndex=areaIndex + 1,
                        rng=rng,
                        rngIndex=rngIndex[:],
                        forceFinalEncounter=True,
                        forceEncounterAreaName=nextArea,
                        area_times=area_times,
                        area_encounters=area_encounters,
                        kilikaKills=kilikaKills,
                        forcedEncounters=forcedEncounters,
                        options=options
                        )

            runArea(areas=areas,
                    areaIndex=areaIndex + 1,
                    rng=rng,
                    rngIndex=rngIndex[:],
                    forceFinalEncounter=False,
                    forceEncounterAreaName=forceEncounterAreaName,
                    area_times=area_times,
                    area_encounters=area_encounters,
                    kilikaKills=kilikaKills,
                    forcedEncounters=forcedEncounters,
                    options=options
                    )

    else:
        # Roll Rng1 for Defender X encounter
        rngIndex[1] += 1

        ghostFound = False
        ghostEncounters = 0
        ghostTime = 0.0

        while not ghostFound:
            formationroll = getNextRoll(1, rng, rngIndex)
            ambushroll = getNextRoll(1, rng, rngIndex)

            # If ghost is in Green area look from encounter 3 onwards
            if formationroll % 13 == 8 or (formationroll % 10 == 0 and ghostEncounters > 2):
                ghostFound = True
            else:
                ghostEncounters += 1
                ghostTime += 13.0

        ochuIn = True if (options & 0x01) == 0x01 else False
        luckSphereIn = True if (options & 0x02) == 0x00 else False
        ochuOut = True if (options & 0x04) == 0x04 else False
        miihenSim = True if (options & 0x08) == 0x08 else False
        oldRoadSim = True if (options & 0x10) == 0x10 else False
        extraSandragora = True if (options & 0x20) == 0x20 else False

        encounterWriter.writerow([x + 1] + seed_rolls + [forceEncounterAreaName, ochuIn, ochuOut, luckSphereIn, miihenSim, oldRoadSim, extraSandragora] + [kilikaKills, sum(area_encounters) + ghostEncounters] + area_encounters + [ghostEncounters])
        timingWriter.writerow([x + 1] + seed_rolls + [forceEncounterAreaName, ochuIn, ochuOut, luckSphereIn, miihenSim, oldRoadSim, extraSandragora] + [kilikaKills, sum(area_times) + ghostTime] + area_times + [ghostTime])

# Load encounter details for areas
with open("../Data/EncounterAreas_CSR.json") as EncounterAreas:
    areas = json.load(EncounterAreas)

# Load enemy attack delay details
with open("../Data/EnemyAttacks.json") as EnemyAttacks:
    attacks = json.load(EnemyAttacks)

# open AreaTimings CSV file for writing
with open("../Output/AreaTimings.csv", "w", newline='') as timingOutput, open("../Output/AreaEncounters.csv", "w", newline='') as encounterOutput:
    timingWriter = csv.writer(timingOutput)
    encounterWriter = csv.writer(encounterOutput)

    # Initialise areanames array
    areanames = []

    areanames.append("Sahagins")
    areanames.append("Geosgaeno")

    for i in range(len(areas)):
        areanames.append(areas[i]["Name"])

    timingWriter.writerow(['Seed ID', 'Auron1', 'Tidus1', 'Auron2', 'Tidus2', 'Auron3', 'Tidus3', 'Extra Encounter Area', 'Ochu In', 'Ochu Out', 'Luck Sphere In', 'Mi''ihen sim', 'Old Road Sim', 'Extra Sandragora', 'Kilika Kills', 'Total'] + areanames + ['Encounters for Ghost'])
    encounterWriter.writerow(['Seed ID', 'Auron1', 'Tidus1', 'Auron2', 'Tidus2', 'Auron3', 'Tidus3', 'Extra Encounter Area', 'Ochu In', 'Ochu Out', 'Luck Sphere In', 'Mi''ihen sim', 'Old Road Sim', 'Extra Sandragora', 'Kilika Kills', 'Total'] + areanames + ['Time for Ghost'])

    # Loop through all 256 PC Seeds
    for x in range(0, 256):

        rng = Rng.RngPC(x)
        rngIndex = [0] * 68

        # Calculate first 6 Sinscale damage rolls for output
        seed_rolls = []

        AuronICVRoll = getNextRoll(22, rng.rngArrays, rngIndex)
        TidusICVRoll = getNextRoll(20, rng.rngArrays, rngIndex)

        for i in range(3):
            AuronDamageRoll = getNextRoll(22, rng.rngArrays, rngIndex)
            AuronCritRoll = getNextRoll(22, rng.rngArrays, rngIndex)

            TidusDamageRoll = getNextRoll(20, rng.rngArrays, rngIndex)
            TidusCritRoll = getNextRoll(20, rng.rngArrays, rngIndex)

            AuronDamage = (278 * ((AuronDamageRoll & 31) + 240)) // 256
            TidusDamage = (134 * ((TidusDamageRoll & 31) + 240)) // 256

            seed_rolls.append(AuronDamage)
            seed_rolls.append(TidusDamage)

        area_times = []
        area_encounters = []

        # Roll rng1 3 times for Sinscales, Ammes and Tanker
        rngIndex[1] += 3

        # Check for Sahagins Pre-Empt / Ambush and apply the time delta
        ambushroll = getNextRoll(1, rng.rngArrays, rngIndex) % 256

        if ambushroll < 32:
            area_times.append(-4.0)
        elif ambushroll >= 223:
            area_times.append(6.0)
        else:
            area_times.append(0.0)

        # Check for Geos Pre-Empt / Ambush and apply the time delta
        ambushroll = getNextRoll(1, rng.rngArrays, rngIndex) % 256

        if ambushroll < 32:
            area_times.append(3.0)
        elif ambushroll >= 223:
            area_times.append(-3.0)
        else:
            area_times.append(0.0)

        area_encounters.append(0)
        area_encounters.append(0)

        # initialise forced encounters at 5 for Sinscales, Ammes , Tanker, Sahagins and Geos
        forcedEncounters = 5

        # kilikaKills = 0

        runArea(areas=areas,
                areaIndex=0,
                rngIndex=rngIndex[:],
                rng=rng.rngArrays,
                forceFinalEncounter=False,
                forceEncounterAreaName="",
                area_times=area_times,
                area_encounters=area_encounters,
                kilikaKills=0,
                forcedEncounters=forcedEncounters,
                options=0x00
                )

        runArea(areas=areas,
                areaIndex=0,
                rngIndex=rngIndex[:],
                rng=rng.rngArrays,
                forceFinalEncounter=True,
                forceEncounterAreaName="Chain",
                area_times=area_times,
                area_encounters=area_encounters,
                kilikaKills=0,
                forcedEncounters=forcedEncounters,
                options=0x00
                )

        os.system("cls")
        print(f"Seed {x+1} / 256 Complete!")
