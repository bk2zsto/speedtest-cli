import logging
import logging.config
import logging.handlers
import json
import urllib
import datetime
import socket
import re
import os

class StatelessHTTPHandler(logging.handlers.HTTPHandler):
  def mapLogRecord(self,record):
    r = {}
    if type(record.msg) == type({}):
      r = record.msg
    elif type(record.msg) == type(""):
      r = {'data': record.msg}
    else:
      r = super(StatelessHTTPHandler,self).mapLogRecord(record)

    return r

class JSONFormatter(logging.Formatter):
  def format(self,record):
    r = None
    r = json.dumps(record.msg)
    return r

class QueryStringFormatter(logging.Formatter):
  def format(self,record):
    print "QueryStringFormatter"
    r = None
    r = urllib.urlencode(record.msg)
    return r

class ResultLogger():
  def __init__(self, testconfig=None, bestserver=None, testresult=None):
    self._logger = logging.getLogger()
    
    self._logconfig = logging.config.fileConfig(re.sub('\.pyc*$','.ini',os.path.abspath(__file__)))
    
    self.testconfig = {}
    if (testconfig): self.testconfig = testconfig
    self.bestserver = {}
    if (bestserver): self.bestserver = bestserver
    self.testresult = {}
    if (testresult): self.testresult = testresult

  def logresult(self):
    logquery = {}
    ### HTTPHandler doesnt use a Formatter so we dont have %(asctime)s, etc.
    logquery['date'] = datetime.date.strftime(datetime.datetime.now(),"%m-%d-%Y")
    logquery['time'] = datetime.date.strftime(datetime.datetime.now(),"%H:%M:%S")
    logquery['srcip'] =  socket.getaddrinfo(socket.getfqdn(),80)[0][4][0] ### 1st IP only!
    logquery['srcname'] = socket.getfqdn()

    for k in ['dlspeed','dlmbits','ulspeed','ulmbits']:
      try:
        logquery[k] = self.testresult[k]
      except KeyError as e:
        pass

    for k in ['host','name','sponsor','id']:
      try:
        logquery['dst' + k] = self.bestserver[k]
      except KeyError:
        pass

    for k in ['ip','isp']:
      try:
        logquery['wan' + k] = self.testconfig['client'][k]
      except KeyError as e:
        pass

    self._logger.info(logquery)

    
    
if __name__ == "__main__":
  l = logging.getLogger()
  c = logging.config.fileConfig("logformat.ini")

  l.info({'a':1,'b':2})

