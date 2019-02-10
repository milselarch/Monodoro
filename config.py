import uuid
import hashlib
import os

import yaml

"""
load config data from gitignored config.yml file
access by using conf[key] where conf is instance of config
"""

MAC_ADDR = hex(uuid.getnode()).replace('0x', '')
MAC_HASH = hashlib.sha256(MAC_ADDR.encode('utf-8')).hexdigest()

class config(object):
    data = {
        'text-file': None,
        'sqlite-file': None,
        'cheaklist-file': None,
        'ID': MAC_HASH
    }

    filename = 'data/config.yml'

    def __init__(self, open = True):
        try:
            self.open()
        except FileNotFoundError:
            self.makeDefaults()


    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        assert (key in self.data)
        self.data[key] = value

    def update(self):
        try:
            self.open()
        except FileNotFoundError:
            print("ERR: CONFIG FILE NOT FOUND")

        for key in self.data:
            #print(self.data)
            current = self.data[key]

            if current == None:
                self.data[key] = input(key + ": ")
            else:
                param = input(key + " [%s]" % current + ": ")

                if param == "": self.data[key] = current
                else: self.data[key] = param

        self.writeOut()

    def open(self):
        fileData = open(self.filename).read()
        fileData = fileData.replace('\t', ' ' * 4)
        data = yaml.load(fileData)

        if data is not None:
            for key in data:
                if key in self.data:
                    self.data[key] = data[key]

        print(self.data)

    def makeDefaults(self):
        print("KEY IN CONFIGS")

        for key in self.data:
            current = self.data[key]
            self.data[key] = input(key + " [%s]" % current + ": ")

        self.writeOut()

    def writeOut(self):
        with open(self.filename, 'w') as outfile:
            yaml.dump(self.data, outfile, default_flow_style=False)

    def getDefaultFile(self):
        filename = self['text-file']

        if filename == None:
            filename = __file__.replace('/', os.sep)
            filename = filename[:filename.rindex(os.sep)+1]
            filename += 'slot history.txt'
        else:
            filename = filename.replace('/', os.sep)

        return filename


if __name__ == '__main__':
    conf = config()
    conf.update()
