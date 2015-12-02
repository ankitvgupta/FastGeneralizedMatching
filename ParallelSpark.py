

import findspark
findspark.init()

import pyspark
sc = pyspark.SparkContext(appName="Spark1")
sc.setCheckpointDir("checkpoints")

import numpy as np
import itertools

# Reduce the amount that Spark logs to the console.
logger = sc._jvm.org.apache.log4j
logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )


# In[2]:

import sys


# In[3]:

def copartitioned(RDD1, RDD2):
    "check if two RDDs are copartitioned"
    return RDD1.partitioner == RDD2.partitioner


# In[4]:

spots_per_hospital = 8
numPartitions = 4


# In[5]:

# These RDD are KV pairs, where the key is the ID of the doctor/hospital, and the values are the IDs of the respective 
# doctors or hospitals in order of preference.
# By this, I mean that hospitals have a set of preferences over doctors, and doctors have preferences over hospitals
doctor_RDD = sc.textFile('doctor_preferences.txt', numPartitions).map(lambda x: map(int, x.split())).zipWithIndex()                                                        .map(lambda (x, y): (y, x)).partitionBy(numPartitions).cache()
hospital_RDD = sc.textFile('hospital_preferences.txt', numPartitions).map(lambda x: map(int, x.split())).zipWithIndex()                                                        .map(lambda (x, y): (y, x)).partitionBy(numPartitions).cache()

# In[6]:



assert(copartitioned(doctor_RDD, hospital_RDD))


# In[6]:




# In[6]:




# In[7]:

# Preferences is a list of ints in order that you want them
# pickingfrom is the ones you are picking from
# N is how many you are picking
# Ex: pick_top_N([3, 4, 5, 1, 2, 7, 8], [7, 1, 2, 4, 5], 3) -> [4, 5, 1]
def pick_top_N(preferences, pickingfrom, N):
    pickingfrom.sort(key=lambda x: preferences.index(x))
    return pickingfrom[:N]

    


# In[7]:




# In[8]:

doctor_matchings = doctor_RDD.mapValues(lambda x : -1).cache()
hospital_matchings = hospital_RDD.mapValues(lambda x: []).cache()

# In[9]:

def combine_old_new(newoptions, oldoptions, preferences):
    if newoptions == None:
        newoptions = []
    if oldoptions == None:
        oldoptions = []
    alloptions = list(set(newoptions).union(set(oldoptions)))
    return pick_top_N(preferences, alloptions, spots_per_hospital)


# In[10]:

def accept_new_hospital_assignment(old, new):
    if new == None:
        return -1
    return new


# In[11]:

# If unmatched (match == -1), then we are gonna use try to use the next pref, so one remove from the list
def remove_pref_if_needed(prefs, match):
    # If unmatched and pref remaining, remove it.
    if match == -1 and len(prefs) > 0:
        return prefs[1:]
    # Else return original prefs
    return prefs


# In[12]:

def is_changed(old, new):
    if old == -1 and new == None:
        return False
    elif old == -1 and new != None:
        return True
    return old != new
    


# In[13]:

doctor_prefs = doctor_RDD.map(lambda x: x).partitionBy(numPartitions).cache()

# In[13]:




# In[13]:




# In[14]:

# Accum1 tracks the number of doctors whose status changed
while True:
    # These are the top remaining choices for the unmatched doctors
    assert(copartitioned(doctor_prefs, doctor_matchings))
    unmatched_doctors_joined = doctor_prefs.join(doctor_matchings).filter(lambda (doc, (prefs, match)): match == -1 and len(prefs) > 0).cache()
    num_unmatched = unmatched_doctors_joined.count() 
    print "Number doctors to work on:", num_unmatched
    if num_unmatched == 0:
        break
    unmatched_doctor_preferences = unmatched_doctors_joined.mapValues(lambda (prefs, match): prefs).cache()
    # Update all of the doctor prefs by removing the first pref from each unmatched doctor
    assert(copartitioned(doctor_prefs, doctor_matchings))
    # Force a checkpoint and evaluation to avoid StackOverflowError
    doctor_prefs = doctor_prefs.join(doctor_matchings).mapValues(lambda (prefs, match): remove_pref_if_needed(prefs, match)).cache()
    doctor_prefs.checkpoint()
    doctor_prefs.count()
    # Take the first pref from each unmatched doctor 
    doctor_proposals = unmatched_doctor_preferences.mapValues(lambda x: x[0]).cache()
    # Group the requests by hospital
    hospital_groupings = doctor_proposals.map(lambda (x, y) : (y, x)).partitionBy(numPartitions).groupByKey().cache()
    # Join the new requests for each hospital with what they previously had and their preferences
    assert(copartitioned(hospital_groupings, hospital_matchings))
    assert(copartitioned(hospital_groupings, hospital_RDD))
    joined_hospital = hospital_groupings.rightOuterJoin(hospital_matchings).join(hospital_RDD).cache()
    # Determine the best ones
    # Force a checkpoint and evaluation to avoid a StackOverflow
    hospital_matchings = joined_hospital.mapValues(lambda ((new, old), preferences): combine_old_new(new, old, preferences)).cache()
    hospital_matchings.checkpoint()
    hospital_matchings.count()
    # Inform the doctors of the match
    matched_doctors = hospital_matchings.flatMapValues(lambda x: x).map(lambda (x, y) : (y, x)).partitionBy(numPartitions).cache()
    # Update the doctor matchings
    assert(copartitioned(doctor_matchings, matched_doctors))

    # Force a checkpoint and evaluation to avoid StackOverflowError
    doctor_matchings = doctor_matchings.leftOuterJoin(matched_doctors).mapValues(lambda (old,new) : accept_new_hospital_assignment(old, new)).cache()
    doctor_matchings.checkpoint()
    doctor_matchings.count()
    sys.stdout.flush()


# In[ ]:

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
    indicies = [preferences.index(match) for match in matches]
    max_index = max(indicies)
    # Get all of the people up until the worst person picked
    best_people = set(preferences[:max_index])
    # Remove the people that were successfully picked
    better_people = best_people - set(matches)
    return list(best_people)
    
# Checks if all of the matches are stable
def verify_matches(doc_matches, hos_matches, original_doc_prefs, original_hos_prefs):
    doctor_to_hospital_preferences = doc_matches.join(original_doc_prefs).mapValues(lambda (match, preferences): getpreferredhospitals(match, preferences)).flatMapValues(lambda x: x)
    hospital_to_doctor_preferences = hos_matches.join(original_hos_prefs).mapValues(lambda (matches, preferences): getpreferreddoctors(matches, preferences)).flatMapValues(lambda x: x).partitionBy(numPartitions)
    flip_prefs = doctor_to_hospital_preferences.map(lambda (x,y): (y,x)).partitionBy(numPartitions)
    return flip_prefs.intersection(hospital_to_doctor_preferences)

        


# In[ ]:

bad_results = verify_matches(doctor_matchings, hospital_matchings, doctor_RDD, hospital_RDD)
# If the assertion passes, then this is a stable matching!
assert(bad_results.count() == 0)


# In[ ]:




# In[ ]:



