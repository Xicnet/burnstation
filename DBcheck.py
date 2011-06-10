#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import MySQLdb
import LoadConfig
config = LoadConfig.LoadConfig()

import urllib
import os.path

#--------------------------------------------------------------------
def validate_media_files():
    """Get the path for every media file and check if exists on filesystem.
       Flag it as excluded = 't' if found or excluded = 't' otherwise
    """

    print "[*] Validating media files in %s ..." % config.musicPath

    db = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpass, db=config.DB)
    db.set_character_set('utf8')

    found     = 0
    not_found = 0

    sql = "SELECT id, location FROM netjuke_tracks ORDER BY id"
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        invalid = flag_media( urllib.url2pathname( row[1] ) )

        sql = "UPDATE netjuke_tracks SET exclude = '%s' WHERE id = '%i'" % (invalid, row[0])
        cursor = db.cursor()
        cursor.execute(sql)

        if   invalid == 'f': found    += 1
        elif invalid == 't': not_found += 1

    db.close()
    print "[*] Finished!"
    print "[*] %i valid files" % found
    print "[*] %i invalid files (not found)" % not_found

#--------------------------------------------------------------------
def flag_media(location):
    f = config.musicPath + location
    exclude = os.path.isfile(f)
    if exclude:
        #print "File from DB found on local filesystem: %s" % f
        return 'f'
    else:
        #print "File from DB *NOT* found on local filesystem: %s" % f
        return 't'

#--------------------------------------------------------------------
def exists():
    try:
        db = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpass, db=config.DB)
        db.set_character_set('utf8')
        db.close()
        return True
    except Exception, e:
        # MySQL error code 1045 is 'access denied'
        if e[0] == 1045 or e[0] == 1049:
            print 
            print "ERROR ! MySQL said: " + e[1]
            print
            print "Your burnstation config file /etc/burnstation/burnstation2.conf has the following MySQL settings:"
            print "DB     ( DataBase name )     : " + config.DB
            print "DBuser ( DataBase user )     : " + config.DBuser
            print "DBpass ( DataBase password ) : " + config.DBpass
            print
            print "It seems that user or password does not exist or has no permissions to access the database."
            print "You can enter your DataBase admin user and password here"
            print "to create the user, password and database specified in your config file."
            print
            print " Press [enter] to abort and check your settings"
            print

            DBadmin_user = raw_input("DB admin user: ")
            if DBadmin_user == '': sys.exit(0)
            else:
                DBadmin_pass = raw_input("DB admin pass: ")
                return DB_admin_create(DBadmin_user, DBadmin_pass)
        else:
            print "DBcheck.exists() EXCEPTION: %s " % str(e)

#--------------------------------------------------------------------
def DB_admin_create(DBadmin_user, DBadmin_pass):
    try:
        db = MySQLdb.connect(host=config.DBhost, user=DBadmin_user, passwd=DBadmin_pass, db='mysql')
        db.set_character_set('utf8')

        sql = "GRANT ALL PRIVILEGES ON `%s`.* to '%s'@'localhost' IDENTIFIED BY '%s'" % (config.DB, config.DBuser, config.DBpass)
        cursor = db.cursor()
        cursor.execute(sql)

        sql = "FLUSH PRIVILEGES"
        cursor = db.cursor()
        cursor.execute(sql)

        sql = "CREATE DATABASE `%s`" % config.DB
        cursor = db.cursor()
        cursor.execute(sql)

        DB_autoimport()
        validate_media_files()

        db.close()

        return True

    except Exception, e:
        print "DBcheck.DB_admin_create() EXCEPTION: " + str(e)
        if e[0] == 1045:
            print
            print "ERROR: invalid MySQL admin user or password.. Try again."
            print

#--------------------------------------------------------------------
def DB_autoimport():
    DBfile = '/usr/share/doc/burnstation-server-2.0/burnstation-2.0.sql.gz'

    """
    cmd = 'mysqladmin -u%s create %s' % (config.DBuser, config.DB)
    if config.DBpass != '': cmd += ' -p"%s"' % config.DBpass
    print "[*] Creating '%s' database ..." % config.DB
    os.system(cmd)
    """

    cmd = 'zcat %s | mysql -u%s %s' % (DBfile, config.DBuser, config.DB)
    if config.DBpass != '': cmd += ' -p"%s"' % config.DBpass
    print "[*] Importing SQL schema & data from '%s' into database" % DBfile
    os.system(cmd)

