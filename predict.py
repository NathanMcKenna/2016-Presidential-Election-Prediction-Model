import pandas
from sklearn import linear_model, feature_extraction

stateList = set(["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"])

def average_poll(full_data):
    """
    Create feature from last poll in each state
    """
    
    # Only care about republicans
    repub = full_data[full_data["PARTY"] == "Rep"]
   
    # Sort by date
    chron = repub.sort_values(by="DATE", ascending=False)
    '''
    for state in stateList:
        statePolls = chron[chron["STATE"] == state]
        if(state == "OK"):
            print(statePolls)
      
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!NEW LINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    '''
    # Only keep the last one
    dedupe = chron.drop_duplicates(subset="STATE", keep="last")
    
    # Remove national polls
    return dedupe[dedupe["STATE"] != "US"]
    
    
if __name__ == "__main__":
    # Read in the X data
    all_data = pandas.read_csv("data.csv")
    
    # Remove non-states
    all_data = all_data[pandas.notnull(all_data["STATE"])]
    
    # split between testing and training
    train_x = average_poll(all_data[all_data["TOPIC"] == '2012-president'])
    train_x.set_index("STATE")
    
    test_x = average_poll(all_data[all_data["TOPIC"] == '2016-president'])
    test_x.set_index("STATE")
    
    # Read in the Y data
    y_data = pandas.read_csv("../data/2012_pres.csv", sep=';')
    y_data = y_data[y_data["PARTY"] == "R"]
    y_data = y_data[pandas.notnull(y_data["GENERAL %"])]
    y_data["GENERAL %"] = [float(x.replace(",", ".").replace("%", ""))
                           for x in y_data["GENERAL %"]]
    y_data["STATE"] = y_data["STATE ABBREVIATION"]
    y_data.set_index("STATE")
    
    backup = train_x
    train_x = y_data.merge(train_x, on="STATE",how='left')
    
    #add custom features
    medianIncome2012 = pandas.read_csv("MedianIncome2012.csv", sep=';')
    medianIncome2012.set_index("STATE")
    
    medianIncome2015 = pandas.read_csv("MedianIncome2015.csv", sep=';')
    medianIncome2015.set_index("STATE")
    
    train_x = medianIncome2012.merge(train_x, on="STATE",how='left')
    test_x = medianIncome2015.merge(test_x, on="STATE", how='left')
    
    religiousPopulation2012 = pandas.read_csv("ReligiousPopulation2012.csv", sep=';')
    religiousPopulation2012.set_index("STATE")
    
    religiousPopulation2016 = pandas.read_csv("ReligiousPopulation2016.csv", sep=';')
    religiousPopulation2016.set_index("STATE")
    
    train_x = religiousPopulation2012.merge(train_x, on="STATE", how='left')
    test_x = religiousPopulation2016.merge(test_x, on="STATE", how='left')
    
    medianAge2010 = pandas.read_csv("MedianAge2010.csv", sep=';')
    medianAge2010.set_index("STATE")
    
    medianAge2015 = pandas.read_csv("MedianAge2015.csv", sep=';')
    medianAge2015.set_index("STATE")
    
    train_x = medianAge2010.merge(train_x, on="STATE", how='left')
    test_x = medianAge2015.merge(test_x, on="STATE", how='left')
    
    # make sure we have all states in the test data
    for ii in set(y_data.STATE) - set(test_x.STATE):
        new_row = pandas.DataFrame([{"STATE": ii}])
        test_x = test_x.append(new_row)
    
    
    # format the data for regression
    train_x = pandas.concat([train_x.STATE.astype(str).str.get_dummies(),
                             train_x], axis=1)
    test_x = pandas.concat([test_x.STATE.astype(str).str.get_dummies(),
                             test_x], axis=1)
    
    # handle missing data
    for dd in train_x, test_x:                
        dd["NOPOLL"] = pandas.isnull(dd["VALUE"])
        dd["VALUE"] = dd["VALUE"].fillna(0.0)
    #print(train_x)    
    # create feature list
    features = list(y_data.STATE)
    features.append("VALUE")
    features.append("NOPOLL")   
    features.append("MEDIAN_INCOME")
    features.append("RELIGIOUS_POPULATION")
    features.append("MEDIAN_AGE")
    
    # fit the regression
    mod = linear_model.LinearRegression()
    mod.fit(train_x[features], train_x["GENERAL %"])

    # Write out the model
    with open("model.txt", 'w') as out:
        out.write("BIAS\t%f\n" % mod.intercept_)
        for jj, kk in zip(features, mod.coef_):
            out.write("%s\t%f\n" % (jj, kk))
    
   # print(test_x[features])
    # Write the predictions
    pred_test = mod.predict(test_x[features])
    with open("pred.txt", 'w') as out:
        for ss, vv in sorted(zip(list(test_x.STATE), pred_test)):
            out.write("%s\t%f\n" % (ss, vv))
