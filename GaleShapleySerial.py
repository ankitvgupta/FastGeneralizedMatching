#####################:
# GaleShapleySerial.py
# Authors: Ankit Gupta, Jonah Kallenbach
#
# Implements the Gale-Shapley Algorithm
#########################

import csv
import numpy as np
import itertools
import sys

# CLI stuff
if sys.argc != 3:
    print "Proper usage: python [program] [doc_prefs] [hosp_prefs]"
    sys.exit(1)

doc_prefs = sys.argv[1]
hosp_prefs = sys.argv[2]

doctor_prefs = np.loadtxt("doctor_preferences.txt").astype(int).tolist()

hospital_prefs = []
with open('hospital_preferences.txt') as inputfile:
    for row in csv.reader(inputfile, delimiter=" "):
        hospital_prefs.append(map(int, row))

numPartitions = 64
numPositionsPerHospital = 6

print doctor_prefs[0]
print hospital_prefs[0]
x = [1,4,2,1]
y = sorted(x, reverse=True)
print y

# Simply perform the well-known Gale Shapley algorithm for the
# national residency match.  This is probably along the lines of
# what the national residency match actually implements.
def serial_implementation():
    hospital_accepted = [[] for i in range(len(hospital_prefs))]
    doc_indices = [0] * len(doctor_prefs)
    hospital_dicts = [{} for i in range(len(hospital_prefs))]
    for i, l in enumerate(hospital_prefs):
        for val, ind in enumerate(l):
            hospital_dicts[i][ind] = val
    iter_n = 0
    doc_pool = set(range(len(doctor_prefs)))
    # s.discard s.add
    brk = True
    while brk:
        brk = False
        hospital_queues = [[] for i in range(len(hospital_prefs))]
        to_pop = []
        # each remaining doctor proposes to their first choice school
        for doc in list(doc_pool):
            #if doc_indices[doc] == numPositionsPerHospital:
            #    doc_pool.discard(doc)
            #    continue
            if doc_indices[doc] >= len(doctor_prefs[doc]):
                doc_pool.discard(doc)
                continue
            brk = True
            hospital_queues[doctor_prefs[doc][doc_indices[doc]]].append(doc)
            doc_indices[doc] += 1
        # each hospital accepts its top spots_per_hospital applicants
        for j in range(len(hospital_queues)):
            old = hospital_accepted[j]
            cor = old + [a for a in hospital_queues[j] if a in hospital_dicts[j].keys()]
            assert(len(cor) == len(old + [a for a in hospital_queues[j]]))
            #cor = sorted(cor, key=lambda x: hospital_dicts[j][x])
            cor2 = sorted(cor, key=lambda x: hospital_prefs[j].index(x))
            #assert(cor == cor2)
            hospital_accepted[j] = cor2[:numPositionsPerHospital]
            if hospital_accepted[j] != old:
                brk = True
            for k in range(min(numPositionsPerHospital, len(cor2))):
                doc_pool.discard(cor2[k])
            for k in range(numPositionsPerHospital, len(cor2)):
                doc_pool.add(cor2[k])
        # TODO: check serial implementation stability
        iter_n += 1
        for p in sorted(to_pop, reverse=True):
            doc_pool.pop(p)
    print iter_n
    return hospital_accepted


matches = serial_implementation()
print matches

# Get the index in the hospital prefs for the worst person that hospital selected
def get_worst_person_selected_index(hospital_i_prefs, hospital_i_matchings):
    return max([hospital_i_prefs.index(x) for x in hospital_i_matchings])


get_worst_person_selected_index(hospital_prefs[2], matches[2])


def check_results(doc_prefs, hospital_prefs, hospital_matchings):
    "Checking"
    doc_to_hospital_matching = {}
    # Determine what the matchings were
    for doc in range(len(doc_prefs)):
        doc_to_hospital_matching[doc] = -1
    for hospital in range(len(hospital_matchings)):
        for match in hospital_matchings[hospital]:
            doc_to_hospital_matching[match] = hospital
    #print doc_to_hospital_matching
    for doc, hosp in zip(doc_to_hospital_matching.keys(), doc_to_hospital_matching.values()):
        if hosp == -1:
            # For each hospital that person prefs, they were worse rating and any of the people they picked
            for hospital in doc_prefs[doc]:
                assert(hospital_prefs[hospital].index(doc) > get_worst_person_selected_index(hospital_prefs[hospital], hospital_matchings[hospital]))
        else:
            for hospital in doc_prefs[doc][:doc_prefs[doc].index(hosp)]:
                assert(hospital_prefs[hospital].index(doc) > get_worst_person_selected_index(hospital_prefs[hospital], hospital_matchings[hospital]))

check_results(doctor_prefs, hospital_prefs, matches)
