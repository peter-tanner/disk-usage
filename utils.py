from datetime import date, timedelta

def nextWeek():
    __today = date.today()
    return __today + timedelta(days=-__today.weekday(), weeks=1)

def subtract(row1,row2,castmode=int):
    if (type(row1) == list and type(row2) == list):
        if (not len(row1) == len(row2)):
            True
            #throw or something
        for i in range(0,len(row1)):
            try:
                row1[i] = castmode(row1[i]) - castmode(row2[i])
            except:
                True    # keep first v if not a number type.
        return row1
    elif (type(row1) == dict and type(row2) == dict):
        if (row1.keys() == row2.keys()):
            for k in row1.keys():
                try:
                    row1.update({k : castmode(row1[k]) - castmode(row2[k])})
                except:
                    True    # keep first v if not a number type.
            return row1

def sumKV(rows,castmode=int):
    result = {}
    for row in rows:
        for k in row.keys():
            if not k in result.keys():
                try:
                    result.update({ k : castmode(row[k]) })
                except:
                    result.update({ k : row[k] })
            else:
                try:
                    result[k] += castmode(row[k])
                except:
                    True
    return result