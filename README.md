# FastGeneralizedMatching
A repository for an implementation of Matching with Contracts. Initial work will be applied to CS 205 Final Project at Harvard University.
Contributors: Ankit Gupta (@ankitvgupta) and Jonah Kallenbach (@jonahkall)


This repository contains the following important files, that should be evaluated for grading purposes.

## Algorithms
- [ParallelSpark-Fast.py](ParallelSpark-Fast.py) contains the spark-based implementation of the algorithm we developed to solve the National Residency Match in approximately O(log N) iterations. This is the primary part of our project, as the algorithm we designed for this has, to the best of our knowledge, never been used before.
- [ParallelSpark.py](ParallelSpark.py) contains the old, slower spark-based implementation which works very similarly to Gale-Shapley
- [GaleShapleySerial.py](GaleShapleySerial.py) contains the serial implementation of Gale-Shapley.
- [ParallelKnapsack.py](ParallelKnapsack.py) contains our first implementation of a type of matching with contracts problem. We wrote a knapsack solver using dynamic programming, and parallelized the technique using Spark. This was one of the "extension" components of our project.

## Generators
- [generate_matchings.py](generate_matchings.py): contains code to generate preferences for give numbers of doctors, hospitals, and other preferences.
- [generate_graphs.py](data/generate_graphs.py) takes the data from the various experiments and plots the results

## Dependencies
Pyspark (we use Spark 1.5.0 and findspark), numpy, scipy

## Instructions to Run
- Set parameters in [generate_matchings.py](generate_matchings.py) to the desired parameters. 
    - Recommended parameters are numDoctors = 4100, numHospitals = 500, numPreferencesPerDoctor = 100
- run `python generate_matchings.py`
    - This will output save two files with lists of preferences
    - This may take a few minutes to run.
- You should now see a `doctor_preferences.txt` and `hospital_preferences.txt` file created in the directory
- Run `time python ParallelSpark-Fast.py doctor_preferences.txt hospital_preferences.txt`, or any of the other above algorithms
- The code should execute and print the time it took to generate all of the matchings and verify their stability.
