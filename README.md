# FastGeneralizedMatching
A repository for an implementation of Matching with Contracts. Initial work will be applied to CS 205 Final Project at Harvard University.

This repository contains the following important files.

## Algorithms
- ParallelSpark-Fast.py contains the spark-based implementation of the algorithm we developed to solve the National Residency Match.
- ParallelSpark.py contains the old, slower spark-based implementation which works very similarly to Gale-Shapley
- GaleShapleySerial.py contains the serial implementation of Gale-Shapley.

## Genators
- generate_matchings.py: contains code to generate preferences for give numbers of doctors, hospitals, and other preferences.

- generate_graphs.py takes the data from the various experiments and plots the results
