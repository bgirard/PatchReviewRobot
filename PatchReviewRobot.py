#!/usr/bin/python
#
# Do what you want! This is provided "AS IS".
# Not for use with nuclear and missile technology,
# because if you do you're drunk.
#

import json
import os

def CreateDefaultOptions():
  options = {
      "bzurl" : "https://api-dev.bugzilla.mozilla.org/test/latest/",
      "username" : "drivebyreviewer",
      "password" : "testing"
  }
  SaveOptions(options);

def SaveOptions(options):
  with open('./settings.json', 'w') as outfile:
      json.dump(options, outfile)

def LoadOptions():
  json_data=open("./settings.json").read()
  options = json.loads(json_data)

  return options

def main():
  CreateDefaultOptions();

  options = LoadOptions();

if __name__ == "__main__":
  main()
