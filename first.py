import findspark
findspark.init()

import pyspark
sc = pyspark.SparkContext(appName="Spark1")


import numpy as np 
import itertools

# Reduce the amount that Spark logs to the console.
logger = sc._jvm.org.apache.log4j
logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

