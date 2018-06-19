# Districts.py
#
# 

from csv import DictReader
from collections import defaultdict
from math import log
from math import pi as kPI
import math
import numpy
import matplotlib.pyplot as plt
import plotly.plotly as py

kOBAMA = set(["D.C.", "Hawaii", "Vermont", "New York", "Rhode Island",
              "Maryland", "California", "Massachusetts", "Delaware", "New Jersey",
              "Connecticut", "Illinois", "Maine", "Washington", "Oregon",
              "New Mexico", "Michigan", "Minnesota", "Nevada", "Wisconsin",
              "Iowa", "New Hampshire", "Pennsylvania", "Virginia",
              "Ohio", "Florida"])
kROMNEY = set(["North Carolina", "Georgia", "Arizona", "Missouri", "Indiana",
               "South Carolina", "Alaska", "Mississippi", "Montana", "Texas",
               "Louisiana", "South Dakota", "North Dakota", "Tennessee",
               "Kansas", "Nebraska", "Kentucky", "Alabama", "Arkansas",
               "West Virginia", "Idaho", "Oklahoma", "Wyoming", "Utah"])

def valid(row):
    return sum(ord(y) for y in row['FEC ID#'][2:4])!=173 or int(row['1']) < 3583



def ml_mean(values):
    """
    Given a list of values assumed to come from a normal distribution,
    return the maximum likelihood estimate of mean of that distribution.
    There are many libraries that do this, but do not use any functions
    outside core Python (sum and len are fine).
    """

    #calculate maximum likelihood of mean
    mean = sum(values)/len(values)
    
    # Your code here
    return mean

def ml_variance(values, mean):
    """
    Given a list of values assumed to come from a normal distribution and
    their maximum likelihood estimate of the mean, compute the maximum
    likelihood estimate of the distribution's variance of those values.
    There are many libraries that do something like this, but they
    likely don't do exactly what you want, so you should not use them
    directly.  (And to be clear, you're not allowed to use them.)
    """

    #calculate standard deviation
    acc = 0
    for value in values:
        acc += ((value-mean)**2)
    standardDev = (acc/len(values))**(1/2)

    #calculate variance
    variance = standardDev**2

    # Your code here
    return variance

def log_probability(value, mean, variance):
    """
    Given a normal distribution with a given mean and varience, compute the
    log probability of a value from that distribution.
    """
    
    #LP = (-1*math.log(variance))-(1/2*math.log(2*math.pi))-(((value-mean)**2)/(2*(variance**2)))
    
    #Calculate log probability with formula given in class Tuesday
    P1 = (-1)*math.log(variance**(1/2))
    P2 = (-0.5)*math.log(2*math.pi)
    P3 = (-1/(2*variance))*(value-mean)**2
    LP = P1 + P2 + P3
    
    return LP

def republican_share(lines, states):
    """
    Return an iterator over the Republican share of the vote in all
    districts in the states provided.
    """
    
    repubDistricts = {}
    for line in lines:
        if line["STATE"] in states:
            if line["PARTY"] == "R" and line["GENERAL VOTES "] == "Unopposed":
                
                state = line["STATE"]
                
                #get the district
                district = line["D"]
                if("TERM" in district):
                    district = district[1:2]
                district = float(district)
                
                repubDistricts[(state,district)] = 100
                
            elif line["PARTY"] == "R" and line["GENERAL %"] != "":
                #get the republican percentage
                repubShare = line["GENERAL %"]
                repubShare = repubShare.replace("%","")
                repubShare = repubShare.replace(",",".")
                repubShare = float(repubShare)
                
                #get the state
                state = line["STATE"]

                #get the district
                district = line["D"]
                if("TERM" in district):
                    district = district[1:2]
                district = float(district)

                repubDistricts[(state,district)] = repubShare
    
    return repubDistricts

if __name__ == "__main__":
    # Don't modify this code
    lines = [x for x in DictReader(open("../data/2014_election_results.csv"))
             if valid(x)]

    obama_mean = ml_mean(republican_share(lines, kOBAMA).values())
    romney_mean = ml_mean(republican_share(lines, kROMNEY).values())

    obama_var = ml_variance(republican_share(lines, kOBAMA).values(),
                             obama_mean)
    romney_var = ml_variance(republican_share(lines, kROMNEY).values(),
                              romney_mean)

    colorado = republican_share(lines, ["Colorado"])
    print("\t\tObama\t\tRomney\n" + "=" * 80)
    for co, dist in colorado:
        obama_prob = log_probability(colorado[(co, dist)], obama_mean, obama_var)
        romney_prob = log_probability(colorado[(co, dist)], romney_mean, romney_var)

        print("District %i\t%f\t%f" % (dist, obama_prob, romney_prob))
        
    ''' 
    histList = []    
    republicans = republican_share(lines, kROMNEY)
    for state, dist in republicans:
        repubProb = log_probability(republicans[(state, dist)], romney_mean, romney_var)
        histList.append(repubProb)
     
    democrats = republican_share(lines, kOBAMA)
    for state,dist in democrats:
        demProb = log_probability(democrats[(state,dist)], obama_mean, obama_var)
        histList.append(demProb)
        
    plt.hist(histList, bins='auto')
    plt.title("Histogram of States")
    plt.show()
    '''
