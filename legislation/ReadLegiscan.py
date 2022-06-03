from Legiscan import *
from BillData import *
import configparser
import pandas as pd
import pickle
from pathlib import Path
import time

"""
Assign all CA searches to a pandas dataframe and a pickle file. Also store in a CSV file. Keep set data in a separate pickle file.

Next time, find way to add data to a pandas dataframe and pickle file.
"""

STATES = [ 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'] #, 'CA', 'IN' removed CA and IN  'AK', 'AL', 'CO', 'CT', 'DC', 'DE', 'FL','AR', 'AZ',

SET_PATH = Path('sets/')
DATA_PATH = Path('data/')

def addToFrame(dataframe, data_list):
  return pd.concat([dataframe, pd.DataFrame(data_list)], ignore_index=True)

def addToList(data_list, getData, data_set=None):
  def do_add(id, info):
    l = len(data_set)
    data_set.add(info[id])
    return len(data_set) != l

  if data_set is None: data_set=set()
  id, info = getData()
  already_found = []
  if isinstance(info, dict) and (data_set is None or info[id] not in data_set):
    if not do_add(id, info):
      already_found.append(id)
    else:
      data_list.append(info)
  elif isinstance(info, list):
    for ele in info:
      if ele[id] not in data_set:
        if not do_add(id, ele):
          already_found.append(id)
        data_list.append(ele)
  else:
    raise TypeError('Did not give a list or dictionary to add to a list')
  return already_found


if __name__ == '__main__':
  # Lists to hold data to eventually transform into a pandas dataframe all at once. Doing this should save time
  data_lists = {'bill_list': [], 'sponsor_list': [], 'bill_sponsor_list': [], 'votes_list': []}

  # Get API Key
  read_config = configparser.ConfigParser()
  read_config.read('private.ini')
  api_key = read_config.get('API KEY', 'key')

  legis_worker = MoreLegiscan(api_key)

  # set used to check for duplicate bills
  found = {'found_bills': set(), 'found_people': set()}

  for _set in found.keys():
    file = _set + '.pickle'
    file = SET_PATH / file
    if file.is_file():
      with open(file, 'rb') as pickle_in:
        found[_set] = pickle.load(pickle_in)

  queries = ['climate change', 'renewable energy']
  state = 'AZ'

  # bill_ids = legis_worker.getSearchIds(state=state, query=queries[0])
  # print(bill_ids)
  # bill = legis_worker.get_bill(bill_id=bill_ids[1][0])
  # data_finder = None
  # try:
  #   data_finder = BillData(bill)
  # except IndexError:
  #   print('found empty information')
  # json_formatted = json.dumps(bill, indent=2)
  # print(json_formatted)

  # search for bills with revelance=90

  for state in STATES:
    bills = legis_worker.getSearchIds(state=state, query=queries[0])

    for id, relevance in bills:
      if relevance < 90: break
      
      while True:
        try:
          bill = legis_worker.get_bill(bill_id=id)
          print('bill id : ', id)
          break
        except LegiScanError:
          print(f"Error with bill {id}")
          continue
        except requests.exceptions.ReadTimeout:
          print('timeout error... retrying')
      try:
        data_finder = BillData(bill)
      except IndexError:
        print('found empty information')
        continue

      if bill['bill_id'] not in found['found_bills'] and bill['bill_type'] == 'B':
        found['found_bills'].add(bill['bill_id'])
        former_sponsor_len = len(data_lists['sponsor_list'])
        addToList(data_lists['bill_list'], lambda: data_finder.getBillData())
        repeated_sponsors = addToList(data_lists['sponsor_list'], lambda: data_finder.getSponsorData(), found['found_people'])
        addToList(data_lists['votes_list'], lambda: data_finder.getVoteData())
        for sponsor in data_lists['sponsor_list'][former_sponsor_len:]:
          data_lists['bill_sponsor_list'].append(
            {'bill_id': data_lists['bill_list'][-1]['bill_id'], 
            'people_id': sponsor['people_id']
            })
        for sponsor in repeated_sponsors:
          data_lists['bill_sponsor_list'].append([data_lists['bill_list'][-1]['bill_id'], sponsor['people_id']])

    SET_PATH.mkdir(parents=True, exist_ok=True)
    for _set in found.keys():
      file = _set + '.pickle'
      with open(SET_PATH / file, 'wb') as pickle_out:
        pickle.dump(found[_set], pickle_out)

    # Create panda dataframes (will be converted to sql table)
    frames = {
      'bill_frame': pd.DataFrame(columns=BillData.BILL_ATTR).drop(columns='STOP'), 
      'sponsor_frame': pd.DataFrame(columns=BillData.SPONSOR_ATTR).drop(columns='STOP'), 
      'bill_sponsor_frame': pd.DataFrame(columns=['bill_id', 'people_id']), 
      'votes_frame': pd.DataFrame(columns=BillData.VOTE_ATTR).drop(columns='STOP')
    }

    frames['bill_frame'] = addToFrame(frames['bill_frame'], data_lists['bill_list'])
    frames['sponsor_frame'] = addToFrame(frames['sponsor_frame'], data_lists['sponsor_list'])
    frames['bill_sponsor_frame'] = addToFrame(frames['bill_sponsor_frame'], data_lists['bill_sponsor_list'])
    frames['votes_frame'] = addToFrame(frames['votes_frame'], data_lists['votes_list'])

    STATE_PATH = DATA_PATH / state
    STATE_PATH.mkdir(parents=True, exist_ok=True)

    for frame in frames.keys():
      csv_file = state + '_' + frame + '.csv'
      path = STATE_PATH / csv_file
      if path.is_file():
        frames[frame].to_csv(path, index=False, mode='a', header=False)
      else:
        frames[frame].to_csv(path, index=False)
    
    time.sleep(20)


  # print(json.dumps(bill, indent=2))


# bills = legis_worker.searchRaw(state='CA', query='climate change')
# print(type(bills))
# json_formatted = json.dumps(bills, indent=2)
# print(type(json_formatted))
#print(json_formatted) # how many results did we get?