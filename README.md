# FastGeneralizedMatching
A repository for an implementation of Matching with Contracts. Initial work will be applied to CS 205 Final Project at Harvard University.
Contributors: Ankit Gupta (@ankitvgupta) and Jonah Kallenbach (@jonahkall)
This repository contains the following important files.

## Algorithms
- [ParallelSpark-Fast.py](ParallelSpark-Fast.py) contains the spark-based implementation of the algorithm we developed to solve the National Residency Match in approximately O(log N) iterations.
- [ParallelSpark.py](ParallelSpark.py) contains the old, slower spark-based implementation which works very similarly to Gale-Shapley
- [GaleShapleySerial.py](GaleShapleySerial.py) contains the serial implementation of Gale-Shapley.

## Generators
- [generate_matchings.py](generate_matchings.py): contains code to generate preferences for give numbers of doctors, hospitals, and other preferences.
- [generate_graphs.py](generate_graphs.py) takes the data from the various experiments and plots the results


## Dependencies
Pyspark (we use Spark 1.5.0), numpy, scipy

## Instructions to Run
- Set parameters in [generate_matchings.py](generate_matchings.py) to the desired parameters. 
    - Recommended parameters are numDoctors = 41000, numHospitals = 5000, numPreferencesPerDoctor = 100
- run `python generate_matchings.py`
    - This may take a few moments to run.
- You should now see a `doctor_matchings.txt` and `hospital_matchings.txt` file created in the directory
- Run `time python ParallSpark-Fast.py`, or any of the other above algorithms
    - Alternatively, you can run this script on AWS using spark-submit
    - Change the labeled lines in each Spark file when running on AWS
- The code should execute and print the time it took to generate all of the matchings and verify their stability.
