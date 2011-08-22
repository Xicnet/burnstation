import os, sys

import Database
from MiscTools import *


class Infopanel:
    '''
    The browser object returns an array of items, typically to be used
    by the scroller object from the Burn Station.

    It should also provide a series of methods to browse back and forth
    through the child/parent items.
    '''
    def __init__(self, text):
        """
        self.text = [
                        {'name': "linea uno"},
                        {'name': "linea dos"},
                        {'name': "linea 3"},
                        {'name': "linea 4"},
                        {'name': "linea 5"},
                        {'name': "linea 6"},
                        {'name': "linea 6"},
                        {'name': "linea 6"},
                        {'name': "linea 6"},
                        {'name': "linea 6"},
                        {'name': "linea 6"},
                    ]
        """
        self.level = None
        self.itemID = None
        self.text = text

    def SetType(self, type):
        self.level = type

    def getList(self, text=None, b=None):
        self.text = text
        try: return self.text
        except: return "No hay nada"
