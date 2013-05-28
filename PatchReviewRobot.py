#!/usr/bin/python
#
# Do what you want! This is provided "AS IS".
# Not for use with nuclear and missile technology,
# because if you do you're drunk.
#

import base64
import json
import subprocess
import os
import urllib2

JSON_HEADERS = {"Accept": "application/json",
                "Content-Type": "application/json"}

class ScriptError(Exception):
    pass

def run_command(args, cwd=None, input=None, raise_on_failure=True, return_exit_code=False, return_stderr=False):
    stdin = subprocess.PIPE if input else None
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=stdin, cwd=cwd)
    if return_stderr:
      output = process.communicate(input)[1].rstrip()
    else:
      output = process.communicate(input)[0].rstrip()
    exit_code = process.wait()
    if raise_on_failure and exit_code:
        raise ScriptError('Failed to run "%s"  exit_code: %d  cwd: %s' % (args, exit_code, cwd))
    if return_exit_code:
        return exit_code
    print "Command out: " + output
    return output

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

def CheckPatch():
  cwd = os.path.abspath('tree')
  result = run_command(["hg", "qimport", "/tmp/reviewbot.patch"], cwd)
  try:
    result = run_command(["hg", "qpush"], cwd)
  except ScriptError:
    result = run_command(["hg", "qpop"], cwd)
    result = run_command(["hg", "qdel", "reviewbot.patch"], cwd)
    return "Patch failed to apply on tip (Might be part of patch queue or against another branch/repo)"
    
  output = run_command(["../check-style/checkmozstyle"], cwd, return_stderr=True, raise_on_failure=False)
  result = run_command(["hg", "qpop"], cwd)
  result = run_command(["hg", "qdel", "reviewbot.patch"], cwd)
  return output

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

  urlopen(request)

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

  review_result = CheckPatch()
  print "Review result: " + review_result
  PostComment(response['bug_id'], "Automated patch review result for: attachment " + str(id) + "\n" + response['description'] + "\n\n" + review_result)
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
  while failuresInARow < 20:
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
