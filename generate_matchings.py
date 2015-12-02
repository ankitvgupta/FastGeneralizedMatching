# Randomly generates a set of matchings for patients and for doctors.
import numpy as np
import csv

numDoctors = 4000
numHospitals = 400
numPositionsPerHospital = 8
numPreferencesPerDoctor = 20

doctor_prefs = []
hospital_applications = {}

# Start by initializing empty arrays for each hospital
for hospital in xrange(numHospitals):
	hospital_applications[hospital] = []

# Determine up to numPreferencesPerDoctor hospital preferences per doctor
# Submit an "application" to each of those hospitals
for doctor in xrange(numDoctors):
    preferences = np.random.permutation(numHospitals)[:numPreferencesPerDoctor]
    # add each preffed hospital to that hospital's applications
    for preference in preferences:
    	hospital_applications[preference].append(doctor)
    doctor_prefs.append(preferences)
# Write to file
doctor_prefs = np.array(doctor_prefs).astype(int)
np.savetxt("doctor_preferences.txt", doctor_prefs, fmt="%5d")
hospital_prefs = []

# For each received application, give them some order, and write to file
for hospital, applications in zip(hospital_applications.keys(), hospital_applications.values()) :
    preferences = np.random.permutation(applications)
    hospital_prefs.append(preferences.astype(int))
with open('hospital_preferences.txt', 'wb') as csvfile:
	writer = csv.writer(csvfile, delimiter=' ')
	for pref in hospital_prefs:
		writer.writerow(pref)



