# -*- coding: utf-8 -*-

import family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'innerwiki'
        self.langs = {
            'cs': 'wiki.wikimedia.cz'
        }
    def scriptpath(self, code):
        return '/mw'
