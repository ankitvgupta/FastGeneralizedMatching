# Randomly generates a set of matchings for patients and for doctors.
import numpy as np
import csv

numDoctors = 410000
numHospitals = 50000
numPositionsPerHospital = 6
numPreferencesPerDoctor = 40

doctor_prefs = []
hospital_applications = [[] for i in range(numHospitals)]

# Start by initializing empty arrays for each hospital
for hospital in xrange(numHospitals):
	hospital_applications[hospital] = []

# Determine up to numPreferencesPerDoctor hospital preferences per doctor
# Submit an "application" to each of those hospitals
for doctor in xrange(numDoctors):
	if doctor % 10000 == 0:
		print "Doctor number", doctor
	#preferences = np.random.permutation(numHospitals)[:numPreferencesPerDoctor]
	preferences = np.random.permutation(np.random.choice(numHospitals, size=numPreferencesPerDoctor, replace=True))
	# add each preffed hospital to that hospital's applications
	for preference in preferences:
		hospital_applications[preference].append(doctor)
	doctor_prefs.append(preferences)
# Write to file
print "Writing doctor preferences to file"
doctor_prefs = np.array(doctor_prefs).astype(int)
np.savetxt("doctor_preferences.txt", doctor_prefs, fmt="%5d")
hospital_prefs = []
print "Working on hospitals"
# For each received application, give them some order, and write to file
last_hosp = -1
for hospital, applications in zip(hospital_applications.keys(), hospital_applications.values()):
	if hospital % 10000 == 0:
		print "Hospital number", hospital
	assert(hospital == last_hosp + 1)
	last_hosp = hospital
	preferences = np.random.permutation(applications)
	hospital_prefs.append(preferences.astype(int))
print "Writing hospital preferences to file"
with open('hospital_preferences.txt', 'wb') as csvfile:
	writer = csv.writer(csvfile, delimiter=' ')
	for pref in hospital_prefs:
		writer.writerow(pref)



