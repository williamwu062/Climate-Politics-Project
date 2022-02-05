import requests
import json
import dataExtraction as de
import scipy as sp
import config
import pandas as pd
import uuid

def makeQuery(cursor):
    query = """
    query MyQuery {
    bills(first: 100, searchQuery: "Climate Change", after: \"""" + f"{cursor}" + """") {
        edges {
        node {
            id
            legislativeSession {
            jurisdiction {
                name
            }
            name
            }
            identifier
            title
            documents {
            links {
                url
            }
            }
            openstatesUrl
            createdAt
            fromOrganization {
            name
            }
            sponsorships {
            person {
                familyName
                givenName
            }
            }
            actions {
            description
            order
            date
            }
            votes {
            edges {
                node {
                result
                counts {
                    option
                    value
                }
                }
            }
            }
        }
        cursor
        }
    }
    }
    """
    return query

headers = {
    'X-API-KEY': config.api_key
}


f = open("openStatesData.csv", "w")
f.truncate()
f.close()

f = open("openStatesVotes.csv", "w")
f.truncate()
f.close()


cursor = ""

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
    "United States" : "USA"
}

df = pd.DataFrame(columns = ['Bill ID','State', 'Legislative Session', 'Bill Number', 'Bill Title', 'Bill', 'Database URL', 'Date of Intro', 'Chamber of Origin', 'Sponsors', 'List of Status'])

votesDf = pd.DataFrame(columns = ['Vote ID', 'Bill ID', 'Yae', 'Nay', 'Absent', 'Not Voting', 'Result'])

df.to_csv("openStatesData.csv", index=False, mode = 'a')

votesDf.to_csv("openStatesVotes.csv", index = False, mode = 'a')

while True:
    query = makeQuery(cursor)
    r = requests.post('https://openstates.org/graphql', headers = headers, json={'query': query})

    json_data = json.loads(r.text)['data']['bills']['edges']
    if(json_data == []):
        print('DONE')
        break

    cursor = json_data[-1]['cursor']
    print(len(json_data))
    for data in json_data:
        data = data['node']
        print(data)
        billId = data['id']
        state = us_state_to_abbrev[data['legislativeSession']['jurisdiction']['name']]
        legislativeSession = data['legislativeSession']['name']
        billNum = data['identifier']
        billTitle = data['title']
        billURL = de.urlArray(data['documents'])
        databaseURL = data['openstatesUrl']
        dateOfIntro = data['createdAt']
        chamberOfOrigin = data['fromOrganization']['name']
        sponsors = de.sponsorships(data['sponsorships'])
        listOfStatus = de.status(data['actions'])

        dict = {"Bill ID" : [billId],
        "State" :[state],
        "Legislative Session" : [legislativeSession],
        "Bill Number" : [billNum],
        "Bill Title" : [billTitle],
        "Bill": [billURL],
        "Database URL" : [databaseURL],
        "Date of Intro" : [dateOfIntro],
        "Chamber of Origin": [chamberOfOrigin],
        "Sponsors": [sponsors],
        "List of Status" : [listOfStatus]}

        df2 = pd.DataFrame(dict)
        df = pd.concat([df, df2])

        votes = data['votes']['edges']
        if len(votes) != 0:
            result = votes[0]['node']['result']
            yes = votes[0]['node']['counts'][0]['value']
            no = votes[0]['node']['counts'][1]['value']
            notVoting = votes[0]['node']['counts'][2]['value']
            voteId = str(uuid.uuid4())

            voteDict = {"Vote ID" : [voteId],
                "Bill ID" : [billId],
                "Yae" :[yes],
                "Nay" : [no],
                "Absent" : [0],
                "Not Voting" : [notVoting],
                "Result": [result]}
            voteDf2 = pd.DataFrame(voteDict)
            votesDf = pd.concat([votesDf, voteDf2])


    df = df.drop_duplicates(subset = "Bill ID", keep = "first")
    df.to_csv("openStatesData.csv", index=False, mode = 'a', header=False)
    votesDf = votesDf.drop_duplicates(subset = "Bill ID", keep = "first")
    votesDf.to_csv("openStatesVotes.csv", index=False, mode='a', header=False)



