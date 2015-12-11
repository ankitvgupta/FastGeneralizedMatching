##############################
# This solves a version of matching with contracts using Spark, and a dynamic-programming based knapsack solver
# that we wrote.
#
# Authors: Ankit Gupta, Jonah Kallenbach
################################

# Comment out these two lines when running on AWS
import findspark
findspark.init()


import pyspark
# Remove appname="Spark1" when running on AWS
sc = pyspark.SparkContext(appName="Spark1")
sc.setCheckpointDir("checkpoints")

import numpy as np
import itertools
import sys

# CLI stuff
if sys.argc != 3:
    print "Proper usage: python [program] [doc_prefs] [hosp_prefs]"
    sys.exit(1)

doc_prefs = sys.argv[1]
hosp_prefs = sys.argv[2]

# Reduce the amount that Spark logs to the console.
logger = sc._jvm.org.apache.log4j
logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR)
logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR)

# hospital's utility for that doctor, scale of 0 to 200
# the utility function is totally arbitrary, so fuck it
def get_utility((doc, hosp)):
    return ((doc + 17) * (hosp + 79) * 393342739) % 200

def get_capacity(hosp):
    return ((hosp * 67867967) % 700) + 300

# the minimum price at which doc will work for hosp
def get_min_price(doc, hosp):
    return ((doc + 7) * (hosp + 3) * 413158511) % 500

# Input: id_val_map is a dict of id -> val mappings
# (aka the hospital utility function)
# id_cost_list is the price at which all of the ids listed
# above will work for this particular hospital
# Output: returns a list of the ids of the doctors we're choosing.
# We don't want to mess around with function call overhead, so we'll
# do a fast top down DP
def fast_knapsack_solver(id_val_map, id_cost_list, capacity):
    dp_arr = [[0]* capacity for i in range(len(id_cost_list))]
    ptr_arr = [[(0,0)]* capacity for i in range(len(id_cost_list))]
    for i in range(capacity):
        if i >= id_cost_list[0][1]:
            dp_arr[0][i] = id_val_map[id_cost_list[0][0]]
    for i in range(1, len(id_cost_list)):
        for j in range(capacity):
            if (j - id_cost_list[i][1] < 0 or dp_arr[i - 1][j] > dp_arr[i - 1][j - id_cost_list[i][1]] \
                     + id_val_map[id_cost_list[i][0]]):
                dp_arr[i][j] = dp_arr[i - 1][j]
                ptr_arr[i][j] = (i - 1, j)
            else:
                dp_arr[i][j] = dp_arr[i - 1][j - id_cost_list[i][1]] \
                 + id_val_map[id_cost_list[i][0]]
                ptr_arr[i][j] = (i - 1, j - id_cost_list[i][1])       
    maxind = 0
    maxval = 0
    for k in range(capacity):
        if dp_arr[len(dp_arr) - 1][k] > maxval:
            maxind = k
            maxval = dp_arr[len(dp_arr) - 1][k]
    # Trace back to figure out what went in our knapsack
    knapsack_contents = []
    i = len(dp_arr) - 1
    j = maxind
    cur = (len(dp_arr) - 1, maxind)
    bn = False
    while 1:
        if (ptr_arr[cur[0]][cur[1]][1] != cur[1]):
            knapsack_contents.append(id_cost_list[cur[0]][0])
        cur = ptr_arr[cur[0]][cur[1]]
        if bn:
            break
        if cur[0] == 0:
            bn = True
    return knapsack_contents

ivm_test_1 = {0:2, 1:3, 2:4, 3:2, 4:5}
# [doc, price] CURRENTLY MUST BE ORDERED IN THIS WAY
icl_test_1 = [[0,1],[1,2],[2,3],[3,6],[4,1]]

# Use for testing
#print fast_knapsack_solver(ivm_test_1, icl_test_1, 3)

def copartitioned(RDD1, RDD2):
    "check if two RDDs are copartitioned"
    return RDD1.partitioner == RDD2.partitioner

spots_per_hospital = 6
numPartitions = 4

# These RDD are KV pairs, where the key is the ID of the doctor/hospital, and the values are the IDs of the respective 
# doctors or hospitals in order of preference.
# By this, I mean that hospitals have a set of preferences over doctors, and doctors have preferences over hospitals
doctor_RDD = sc.textFile(doc_prefs, numPartitions).map(lambda x: map(int, x.split())).zipWithIndex().map(lambda (x, y): (y, x)).partitionBy(numPartitions).cache()
hospital_RDD = sc.textFile(hosp_prefs, numPartitions).map(lambda x: map(int, x.split())).zipWithIndex().map(lambda (x, y): (y, x)).partitionBy(numPartitions).cache()


assert(copartitioned(doctor_RDD, hospital_RDD))

# Preferences is a list of ints in order that you want them
# pickingfrom is the ones you are picking from
# N is how many you are picking
# Ex: pick_top_N([3, 4, 5, 1, 2, 7, 8], [7, 1, 2, 4, 5], 3) -> [4, 5, 1]
def pick_top_N(preferences, pickingfrom, N):
    pickingfrom.sort(key=lambda x: preferences.index(x))
    return pickingfrom[:N]


def pick_best_program(pickingfrom, preferences):
    
    if pickingfrom == None:
        return -1
    pickingfrom = list(pickingfrom)
    if len(pickingfrom) == 0:
        return -1
    pickingfrom.sort(key=lambda x: preferences.index(x))
    return pickingfrom[0]



def combine_old_new(newoptions, oldoptions, hospid):
    if newoptions == None:
        newoptions = []
    if oldoptions == None:
        oldoptions = []
    alloptions = list(set(newoptions).union(set(oldoptions)))
    id_val_map = {key: value for (key, value) in zip(alloptions, map(get_utility, zip(alloptions, [hospid] * len(alloptions))))}
    id_cost_list = [[a, get_min_price(a,hospid)] for a in alloptions]
    return fast_knapsack_solver(id_val_map, id_cost_list, get_capacity(hospid))
    #return pick_top_N(preferences, alloptions, spots_per_hospital)


def accept_new_hospital_assignment(old, new):
    if new == None:
        return -1
    return new


# If unmatched (match == -1), then we are gonna use try to use the next pref, so one remove from the list
def remove_pref_if_needed(prefs, match):
    # If unmatched and pref remaining, remove it.
    if match == -1 and len(prefs) > 0:
        return prefs[1:]
    # Else return original prefs
    return prefs


def is_changed(old, new):
    if old == -1 and new == None:
        return False
    elif old == -1 and new != None:
        return True
    return old != new
    


doctor_prefs = doctor_RDD.map(lambda x: x).partitionBy(numPartitions).cache()


doctor_matchings = doctor_RDD.mapValues(lambda x : -1).partitionBy(numPartitions).cache()
hospital_matchings = hospital_RDD.mapValues(lambda x: []).partitionBy(numPartitions).cache()


def get_better_prefs(prefs, match):
    if match == -1:
        return prefs
    return prefs[:prefs.index(match)+1]


def update_hospital_matches(new_matches, old_matches):
    if new_matches == None:
        return old_matches
    return new_matches


iteration = 0
steps_per_checkpoint = 5

# Convergence criterion
# If we see 5 iterations within 
epsilon = 0.1
while True:
    iteration += 1
    # These are the top remaining choices for the unmatched doctors
    assert(copartitioned(doctor_prefs, doctor_matchings))
    doctor_filtered = doctor_prefs.join(doctor_matchings).mapValues(lambda (prefs, match): get_better_prefs(prefs, match))
    applications_per_hospital = doctor_filtered.flatMapValues(lambda x:x).map(lambda (x,y):(y,x)).partitionBy(numPartitions).groupByKey().partitionBy(numPartitions)
    assert(copartitioned(applications_per_hospital, hospital_matchings))
    assert(copartitioned(hospital_matchings, hospital_RDD))
    joined_with_old_matches = applications_per_hospital.rightOuterJoin(hospital_matchings).map(lambda (hospital_id, (new,old)): (hospital_id, combine_old_new(new, old, hospital_id)))
    acceptances_per_doctor = joined_with_old_matches.flatMapValues(lambda x:x).map(lambda (x,y):(y,x)).partitionBy(numPartitions).groupByKey()
    assert(copartitioned(acceptances_per_doctor, doctor_RDD))
    new_matchings = acceptances_per_doctor.rightOuterJoin(doctor_RDD).mapValues(lambda (programs,preferences): pick_best_program(programs, preferences)).cache()
    assert(copartitioned(new_matchings, doctor_matchings))
    num_changes = new_matchings.join(doctor_matchings).filter(lambda (doc, (new, old)): new != old).count()
    print num_changes
    if num_changes == 0:
        print "done"
        break
    doctor_matchings = new_matchings
    doctor_matchings.cache()

    hospital_new_versions = doctor_matchings.filter(lambda (doc, match): match != -1).map(lambda (x,y) : (y,x)).partitionBy(numPartitions).groupByKey()
    hospital_matchings = hospital_new_versions.rightOuterJoin(hospital_matchings).mapValues(lambda (new_matches, old_matches): update_hospital_matches(new_matches, old_matches))
    hospital_matchings.cache()
    
    num_changes = new_matchings.join(doctor_matchings).filter(lambda (doc, (new, old)): new != old).count()
    print "End of iteration"
    #print "The number of changes in matches in this iteration was:", num_changes
    #if num_changes == 0:
    #    break
    
# Given a match that a doctor had and the original preferences, determine all of the hospitals the doctor would have preferred.
def getpreferredhospitals(match, preferences):
    # If you weren't matched, you would have preferred any of the original ranked ones
    if match == -1:
        return preferences
    # If you were matched, you would have preferred everything up until that one.
    return preferences[:preferences.index(match)]
# Given the matches that a hospital got, determine all of the doctors the hospital would have preferred
def getpreferreddoctors(matches, preferences):
    # Figure out out which of the preferences were actually picked
    if len(matches) == 0:
        return matches
    indicies = [preferences.index(match) for match in matches]
    max_index = max(indicies)
    # Get all of the people up until the worst person picked
    best_people = set(preferences[:max_index])
    # Remove the people that were successfully picked
    better_people = best_people - set(matches)
    return list(best_people)
    
# Checks if all of the matches are stable
# def verify_matches(doc_matches, hos_matches, original_doc_prefs, original_hos_prefs):
#     doctor_to_hospital_preferences = doc_matches.join(original_doc_prefs).mapValues(lambda (match, preferences): getpreferredhospitals(match, preferences)).flatMapValues(lambda x: x)
#     hospital_to_doctor_preferences = hos_matches.join(original_hos_prefs).mapValues(lambda (matches, preferences): getpreferreddoctors(matches, preferences)).flatMapValues(lambda x: x).partitionBy(numPartitions)
#     flip_prefs = doctor_to_hospital_preferences.map(lambda (x,y): (y,x)).partitionBy(numPartitions)
#     return flip_prefs.intersection(hospital_to_doctor_preferences)


#bad_results = verify_matches(doctor_matchings, hospital_matchings, doctor_RDD, hospital_RDD)
# If the assertion passes, then this is a stable matching!
#assert(bad_results.count() == 0)


# Make sure the number of matched doctors agrees in both RDDs
# assert(doctor_matchings.filter(lambda (x,y): y != -1).count() == hospital_matchings.mapValues(len).values().sum())


