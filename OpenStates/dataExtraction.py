def urlArray(data):
    if len(data) == 0:
        return " "
    toReturn = []
    data = data[0]['links']
    for i in data:
        toReturn.append(i['url'])
    return  ', '.join(toReturn)

def sponsorships(data):
    if len(data) == 0:
        return " "
    toReturn = []
    for i in data:
        if i['person'] is not None:
            person = i['person']['givenName'] + " " + i['person']['familyName']
            toReturn.append(person)
    return ', '.join(toReturn)

def status(data):
    if len(data) == 0:
        return " "
    toReturn = []
    for i in data:
        toReturn.append(i['description'])
    return  ', '.join(toReturn)