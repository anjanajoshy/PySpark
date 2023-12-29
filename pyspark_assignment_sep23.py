# -*- coding: utf-8 -*-
"""PySpark_Assignment_Sep23.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tOv_tPv7OiGs7DAOvNTiSxZv5Rknvy8d

# ADS2 - Assignment 1 - Data Handling and Processing with PySpark

**STUDENT NAME -** **Anjana Joshy**

**STUDENT ID -** **22022447**

In this assignment, you will be analysing the popularity of films and TV shows on the streaming platform, Netflix. Using your knowledge of PySpark DataFrames and Spark SQL, you will produce a number of "downstream" data products to analyse trends in global streaming habits.

Download the dataset from this [Kaggle](https://www.kaggle.com/dhruvildave/netflix-top-10-tv-shows-and-films) page. A copy of the `all_weeks_countries.csv` file is also available on the canvas page for this assignment.

Your task is to load in the data and produce a number of "downstream" data products and plots as described below.

The PySpark installation and setup is provided below for conveinience.

IMPORTANT: DO NOT EDIT OR REMOVE THE COMMENT TAGS IN THE CODE CELLS
"""

from google.colab import drive
drive.mount('/content/drive')

# CodeGrade Tag Init1

# Apache Spark uses Java, so first we must install that
!apt-get install openjdk-8-jdk-headless -qq > /dev/null

# CodeGrade Tag Init2
# Mount Google Drive and unpack Spark
from google.colab import drive
drive.mount('/content/drive')
!tar xzf /content/drive/MyDrive/spark-3.3.0-bin-hadoop3.tgz

# CodeGrade Tag Init3
# Set up environment variables
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.3.0-bin-hadoop3"

# CodeGrade Tag Init4
# Install findspark, which helps python locate the pyspark module files
!pip install -q findspark
import findspark
findspark.init()

# Finally, we initialse a "SparkSession", which handles the computations
from pyspark.sql import SparkSession
spark = SparkSession.builder\
        .master("local")\
        .appName("Colab")\
        .config('spark.ui.port', '4050')\
        .getOrCreate()

# Load the all_weeks_countries.csv into your Colab Notebook as a DataFrame.
netflixcsvpath = '/content/all-weeks-countries.csv'

# Data is loaded with header: True and an inferred schema
netflixDF = (spark
           .read
           .option('header', 'True')
           .option('inferSchema', 'True')
           .csv(netflixcsvpath)
          )

# pyspark.sql.functions countains all the transformations and actions you will
# need
from pyspark.sql import functions as F

"""# Exercise 1 - Data Preparation


1.   Create two separate DataFrames for Films and TV.
2.   For the Films data, drop the column containing the season names.
3.   For the TV data, replace any null values in the season name column with the show name.
"""

# CodeGrade Tag Ex1a

### Display the table and its schema
netflixDF.show()
netflixDF.printSchema()

# CodeGrade Tag Ex1b

### Seperate the data into two DataFrames for Films and TV
### Call the dataframes tvDF and filmsDF

filmsDF = netflixDF.filter("category = 'Films'")
filmsDF.show()
tvDF = netflixDF.filter("category = 'TV'")
tvDF.show()

# CodeGrade Tag Ex1c

### Drop the 'season_title' column from the Films DataFrame, display the table


filmsDF = filmsDF.drop('season_title')
filmsDF.show()

# CodeGrade Tag Ex1d

### Use the F.isnull function to create a column showing where there are null
### values in the 'season_title' column. Replace the null values with the
### corresponding value from the 'show_title' column, then replace the
### 'season_title' column in the tvDF DataFrame.

tvDF = tvDF.withColumn('seasontitle',F.when(F.isnull(tvDF['season_title']),tvDF['show_title'])\
                       .otherwise(tvDF['season_title'])).drop('season_title')\
                       .withColumnRenamed('seasontitle','season_title')

tvDF.show()

"""# Exercise 2

Making use of the "groupBy" and "where" methods, find the number of weeks the show "Stranger Things" was in the Top 10 for the United Kingdom across all seasons. Store your result in a variable named "STWeeks"

"""

# CodeGrade Tag Ex2
### Use the "where" method to create a new dataframe containing the data for
### the show Stranger Things in the Uniter Kingdom. Call this dataframe STDF.
STDF = tvDF.where((tvDF['show_title'] == 'Stranger Things') &\
                  (tvDF['country_name'] == 'United Kingdom'))

### Using "groupBy" method and "F.count_distinct" function, find the total number of weeks
### Stranger Things spent in the top 10 of the UK, across all seasons. Show the
### result.
STWeeks = STDF.groupBy('show_title').agg(F.count_distinct('week'))
STWeeks.show()

"""# Exercise 3

Produce a dataframe containing only the Top 25 TV seasons in the UK, based on the number of weeks they spent in the Top 10.
"""

# CodeGrade Tag Ex3
### Produce a dataframe containing the top 25 seasons by number of weeks in the
### top 10 of the United Kingdom, sorted by number of weeks. Store the dataframe
### in a variable called Top25
Top25 = tvDF.filter(tvDF['country_name'] == 'United Kingdom')\
            .groupBy('season_title').agg(F.max('cumulative_weeks_in_top_10').alias('ALL_WEEKS'))\
            .sort('ALL_WEEKS', ascending = False)\
            .limit(25)

Top25.show(25, truncate= False)

"""# Exercise 4

For the show "Young Sheldon", find the country where each season spent the most time in the Top 10.
"""

# CodeGrade Tag Ex4
### For each season of the show "Young Sheldon" find the countries where it spent
### the most time in the Top 10
weekper = netflixDF.filter(netflixDF['show_title'] == 'Young Sheldon')\
            .groupBy('season_title', 'country_name')\
            .agg(F.max('cumulative_weeks_in_top_10').alias('maximumweek'))\
            .sort('maximumweek', ascending = False)
topCountrys = weekper.groupBy('season_title')\
                     .agg(F.first('country_name').alias('Top_Country'),F.max('maximumweek').alias('Top_Week'))

topCountrys.show(truncate = False)

"""# Exercise 5

For each country, find the film that spent the most time in the Top 10.
"""

# CodeGrade Tag Ex5
### For each country, find the film that spent the most time in the Top 10
### Display the results in a Dataframe ordered by country name.
Dfilms = filmsDF.groupBy('country_name','show_title')\
       .agg(F.max('cumulative_weeks_in_top_10').alias('maximumweek'))\
       .sort('maximumweek', ascending = False)
films_watched = Dfilms.groupBy('country_name')\
                      .agg(F.first('show_title').alias('films_watched'),\
                           F.max('maximumweek').alias('maximumweek'))\
                      .orderBy('country_name')

films_watched.show(truncate = False)

"""# Exercise 6

Calculate the number of weeks each film spent at the number 1 spot of each country's Top 10 list. Then find the films that spent the most time in the number 1 spot for each country.
"""

# CodeGrade Tag Ex6a

### Create a column using the F.when function to calculate the number of weeks a
### films spens in the number 1 spot of the Top 10. Use the .otherwise method to
### set rows with no number 1 spots to zero. Use the .alias metod to call this
### column "weeks_at_1"
Film = filmsDF.withColumn('weeks_at_1',F.when(filmsDF['weekly_rank'] == 1,filmsDF['cumulative_weeks_in_top_10']).otherwise(0).alias('weeks_at_1'))
Film.show(truncate = False)

# CodeGrade Tag Ex6b

### Group by country name and sow title, and use the .agg method and your new
### column to find the number of weeks each film spent in the top spot for each
### country.

topfilm = Film.groupBy('country_name','show_title')\
                 .agg(F.count('weeks_at_1').alias('count_weeks'))\
                 .sort('count_weeks', ascending = False)

topfilm.show(truncate = False)

# CodeGrade Tag Ex6c

### Produce a dataframe grouped by country name that contains the show title and
### number of weeks at the number 1 spot of the top performing film in each
### country.
outfilm = Film.groupBy('country_name','show_title')\
             .agg(F.sum('weeks_at_1').alias('Week_1'))\
             .orderBy('Week_1',ascending = False)
outfilm.show(truncate= False)