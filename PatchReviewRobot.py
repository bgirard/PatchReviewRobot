#!/usr/bin/python
#
# Do what you want! This is provided "AS IS".
# Not for use with nuclear and missile technology,
# because if you do you're drunk.
#

import base64
import json
import os
import urllib2

JSON_HEADERS = {"Accept": "application/json",
                "Content-Type": "application/json"}

def CreateDefaultOptions():
  options = {
      "bzurl" : "https://api-dev.bugzilla.mozilla.org/test/latest/",
      "username" : "drivebyreviewer@fantasytalesonline.com",
      "password" : "testing",
      "lastattachment" : 337
  }
  SaveOptions(options);

def SaveOptions(options):
  with open('./settings.json', 'w') as outfile:
      json.dump(options, outfile)

def LoadOptions():
  json_data=open("./settings.json").read()
  options = json.loads(json_data)

  return options

def urlopen(req):
  try:
    return urllib2.urlopen(req)
  except urllib2.HTTPError, e:
    msg = ''
    try:
      err = json.load(e)
      msg = err['message']
    except:
      msg = e 
      pass

    if msg:
      ui.warn('Error: %s\n' % msg)
    raise

def PostComment(bugid, comment):
  global options
  print "Post comment: " + comment
  url = options["bzurl"] + "bug/" + str(bugid) + "/comment?username=" + options["username"] + "&password=" + options["password"]
  print url

  comment = {
    "text" : comment,
  };

  commentStr = json.dumps(comment)
  print commentStr
  request = urllib2.Request(url, commentStr, JSON_HEADERS)

  #urlopen(request)

def FetchAttachment(id):
  print "Download attachment: " + str(id)
  url = options["bzurl"] + "attachment/" + str(id) + "?attachmentdata=1"
  try:
    body = urllib2.urlopen(url).read()
  except urllib2.HTTPError:
    print "Failed to download attachment: " + str(id)
    return False

  response = json.loads(body)
  attachmentData = base64.b64decode(response['data'])
  with open("/tmp/reviewbot.patch", "w") as text_file:
    text_file.write(attachmentData)
  PostComment(response['bug_id'], "Review result for: attachment " + str(id) + "\n" + response['description'] + "\n\nPENDING")
  return True

def ProcessAttachment(id):
  print "Getting attachment: " + str(id)
  url = options["bzurl"] + "attachment/" + str(id)

  try:
    body = urllib2.urlopen(url).read()
  except urllib2.HTTPError:
    print "doesn't exist"
    return False

  response = json.loads(body)
  
  if not response['is_patch']:
    print "Not patch"
    return True
  if response['is_obsolete']:
    print "Obsolete"
    return True

  FetchAttachment(id)
  return True
  

def ScanAttachment():
  global options

  failuresInARow = 0
  while failuresInARow < 5:
    foundAttachment = ProcessAttachment(options["lastattachment"])
    options["lastattachment"] = options["lastattachment"] + 1
    if not foundAttachment:
      failuresInARow = failuresInARow + 1
    else:
      SaveOptions(options)

def main():
  global options
  #CreateDefaultOptions();

  options = LoadOptions();

  ScanAttachment();

if __name__ == "__main__":
  main()
