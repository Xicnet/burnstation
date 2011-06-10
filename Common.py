#!/usr/bin/python
# -*- coding: utf-8 -*-

def Init(basedir):
    import sys
    
    sys.path.append(basedir)

    libdir = basedir + '/lib'
    sys.path.append(libdir)

    importdir = basedir + '/import'
    sys.path.append(importdir)

