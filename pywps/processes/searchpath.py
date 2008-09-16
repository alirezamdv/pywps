#!/usr/bin/python

import os,time,string,sys,shutil

class Process:
    def __init__(self):
        self.Identifier = "searchpath"
        self.processVersion = "0.1"
        self.storeSupported = "true"
        self.Title="Find the shortes path on the roads map"
        #self.grassLocation="/var/www/wps/spearfish60/"
        self.Inputs = [
                    {
                        'Identifier': 'streetmap',
                        'Title': """Street map""",
                        'Abstract': """Street map on which the shortest path
                        operation should be performed""",
                        'ComplexValue': {'Formats':["text/xml"]},
                        'value': None
                    },
                    {
                        'Identifier': 'x1',
                        'Title': 'Start x coordinate',
                        'LiteralData': {
                            'values':["*"],
                            },
                        'dataType': type(0.0),
                        'value': None
                    },
                    {
                        'Identifier': 'y1',
                        'Title': 'Start y coordinate',
                        'LiteralData': {
                            'values':["*"],
                        },
                        'dataType': type(0.0),
                        'value': None
                    },
                    {
                        'Identifier': 'x2',
                        'Title': 'End x coordinate',
                        'LiteralData': {
                            'values':["*"],
                        },
                        'dataType': type(0.0),
                        'value': None
                    },
                    {
                        'Identifier': 'y2',
                        'Title': 'End y coordinate',
                        'LiteralData': {
                            'values':["*"],
                        },
                        'dataType': type(0.0),
                        'value': None
                    }
                ]
        self.Outputs = [
                    {
                        'Identifier': 'outputReference',
                        'Title': 'Resulting output map',
                        'ComplexValueReference': {'Formats':["text/xml"]},
                        'value': None
                    },
                    {
                        'Identifier': 'outputData',
                        'Title': 'Resulting output map',
                        'ComplexValue': {'Formats':["text/xml"]},
                        'value': None
                    },
                ]

    # --------------------------------------------------------------------
    def execute(self):
        """
        This function serves like simple GRASS - python script

        It returns None, if process succeed or String if process failed
        """
        os.system("v.in.ogr dsn=%s out=roads 1>&2" %
                (self.DataInputs['value']))
        os.system("g.region -d")
        # FIXME: the program does print "Building topology to STDOUT!!
        # print  "echo '0 %s %s %s %s' | v.net.path in=roads out=path 1>&2" % \
        #         (self.DataInputs['x1'],
        #         self.DataInputs['y1'],
        #         self.DataInputs['x2'],
        #         self.DataInputs['y2'])

        os.system(
            "echo '0 %s %s %s %s' | v.net.path in=roads out=path 1>&2" % \
            (self.Inputs['x1'],
                self.Inputs['y1'],
                self.Inputs['x2'],
                self.Inputs['y2']))
        os.system("v.out.ogr format=GML input=path dsn=out.xml olayer=path.xml 1>&2")

        if "out.xml" in os.listdir(os.curdir):
            shutil.copy("out.xml","out2.xml")
            self.Outputs[0]['value'] = "out.xml"
            self.Outputs[1]['value'] = "out2.xml"
            return
        else:
            return "Ouput file not created!"