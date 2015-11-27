# Randomly generates a set of matchings for patients and for doctors.

import numpy as np


numDoctors = 200
numHospitals = 20
numPositionsPerHospital = 8
numPreferencesPerDoctor = 15

doctor_prefs = []
for doctor in xrange(numDoctors):
    preferences = np.random.permutation(numHospitals)[:numPreferencesPerDoctor]
    doctor_prefs.append(preferences)
doctor_prefs = np.array(doctor_prefs).astype(int)
np.savetxt("doctor_preferences.txt", doctor_prefs, fmt="%5d")
hospital_prefs = []
for hospital in xrange(numHospitals):
    preferences = np.random.permutation(numDoctors)
    hospital_prefs.append(preferences)
hospital_prefs = np.array(hospital_prefs).astype(int)
np.savetxt("hospital_preferences.txt", hospital_prefs, fmt="%5d")


