
from ast import Assert


class BillData():
  """
  Holds functions that work with data from a bill. This bill should be a JSON format bill from the Legiscan API.
  """
  #attributes have a STOP point. This STOP value indicates that all attributes after this index will need a more complex query than just using the attribute name to scrape the JSON. The very first index HAS to be the id of the set of attributes.
  BILL_ATTR = ['bill_id', 'state', 'bill_number', 'title', 'STOP', 'date of introduction', 'chamber of origin', 'final status', 'date of final', 'text']
  SPONSOR_ATTR = ['people_id', 'party', 'role', 'name', 'STOP']
  VOTE_ATTR = ['roll_call_id', 'yea', 'nay', 'absent', 'nv', 'passed', 'chamber', 'desc', 'date', 'STOP', 'bill_id']

  def __init__(self, bill):
    self.bill = bill
    if not (bill['progress'] and bill['history'] and bill['texts'] and bill['sponsors']):
      raise IndexError('empty information in bill')

  def getVoteData(self):
    """
    Uses VOTE_ATTR to find to construct a dictionary of attributes of a bill.

    Returns
      1. the VOTE_ATTR key/id
      2. a list of dictionaries containing bill attributes according to VOTE_ATTR.
    """
    bill = self.bill
    votes = bill['votes']
    all_vote_info = []
    for vote in votes:
      vote_info = {}
      for attr in self.__iterAttrs(BillData.VOTE_ATTR):
        vote_info[attr] = vote[attr]
      vote_info['bill_id'] = bill['bill_id']
      all_vote_info.append(vote_info)
    return BillData.VOTE_ATTR[0], all_vote_info
      
  def getBillData(self):
    """
    Uses BILL_ATTR to find to construct a dictionary of attributes of a bill.

    Returns 
      1. the BILL_ATTR key/id
      2. a dictionary containing bill attributes according to BILL_ATTR.
    """
    bill_info = {}
    bill = self.bill
    for attr in self.__iterAttrs(BillData.BILL_ATTR):
        bill_info[attr] = bill[attr]
    bill_info['date of introduction'] = bill['progress'][0]['date']
    bill_info['chamber of origin'] = bill['history'][0]['chamber']
    bill_info['final status'] = bill['history'][-1]['action']
    bill_info['date of final'] = bill['history'][-1]['date']
    bill_info['text'] = bill['texts'][-1]['url']
    return BillData.BILL_ATTR[0], bill_info

  def __iterAttrs(self, attributes):
    i = 0
    attr = attributes[i]
    while attr != "STOP":
      yield attr
      i += 1 
      attr = attributes[i]

  def getSponsorData(self):
    """
    Uses SPONSOR_ATTR to construct a list of dictionaries (for all sponsors) containing attributes of a sponsor for a bill.

    Returns 
      1. the SPONSOR_ATTR key/id
      2. a list containing dictionaries of each sponsor's data with attributes according to SPONSOR_ATTR.
    """
    bill = self.bill
    sponsors = bill['sponsors']
    all_sponsor_info = []

    for sponsor in sponsors:
      sponsor_info = {}
      for attr in self.__iterAttrs(BillData.SPONSOR_ATTR):
        sponsor_info[attr] = sponsor[attr]
      all_sponsor_info.append(sponsor_info)
    return BillData.SPONSOR_ATTR[0], all_sponsor_info