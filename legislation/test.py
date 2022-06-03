from Legiscan import *
import configparser


read_config = configparser.ConfigParser()
read_config.read('private.ini')
api_key = read_config.get('API KEY', 'key')

legis_worker = MoreLegiscan(api_key)

# raw_search = legis_worker.searchRaw(year=1, query='climate change', state='CA')
bills = legis_worker.getSearchIds(search_type=1, state='cA', query='climate change')
print(bills)

#print(json.dumps(raw_search, indent=2))