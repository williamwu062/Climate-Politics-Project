import requests
import json
import config
import pandas as pd

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
# query MyQuery {
#   bills(searchQuery: "climate change", first: 10) {
#     totalCount
#   }
# }

f = open("data.csv", "w")
f.truncate()
f.close()

cursor = ""

query = makeQuery(cursor)
r = requests.post('https://openstates.org/graphql', headers = headers, json={'query': query})
print(r.status_code)
print(r.text)

json_data = json.loads(r.text)['data']['bills']['edges']

df = pd.json_normalize(json_data)
df.columns = ['Cursor','Bill ID','State', 'Legislative Session', 'Bill Number', 'Bill Title', 'Bill', 'Database URL', 'Date of Intro', 'Chamber of Origin', 'Sponsors', 'List of Status', 'Votes']

cursor = json_data[-1]['cursor']

# check if data is already in here and check other search terms

# print(cursor)
# print(makeQuery(cursor))
df.to_csv("openStatesData.csv", index=False, mode = 'a')

while True:
    query = makeQuery(cursor)
    r = requests.post('https://openstates.org/graphql', headers = headers, json={'query': query})
    print(r.status_code)
    print(r.text)


    json_data = json.loads(r.text)['data']['bills']['edges']
    if(json_data == []):
        print('DONE')
        break

    df = pd.json_normalize(json_data)

    cursor = json_data[-1]['cursor']

    # check if data is already in here and check other search terms

    # print(cursor)
    # print(makeQuery(cursor))
    df.to_csv("data.csv", index=False, mode = 'a', header=False)
    # break

# print(json_data)


