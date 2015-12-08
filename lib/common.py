#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft
#


from config import *

import MySQLdb
import time
import random
import subprocess
import syslog

#
##
###

def logthis(message, stdout=1) :
    """Writes message to SYSLOG and prints it to STDOUT, if u want.
    """
    syslog.syslog(syslog.LOG_INFO, 'UFT | %s' % message )
    if stdout==1 :
        print "%s" % message


def random_wait() :
    """Random wait (ms).
    """
    random.seed()
    n = random.random()
    time.sleep(n)


def check_running_ps():
    """Checks how many processes are running for a given server_name.
       Returns max_ps_reached (int. binary)
    """
    db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor=db.cursor()
    cursor.execute("select servers_id, name, role, enabled, handicap, running_ps, max_ps from servers where name='%s';" % server_name )
    results=cursor.fetchall()
    cursor.close ()
    db.close ()
    for registry in results:
        servers_id=registry[0]
        name=registry[1]
        role=registry[2]
        enabled=registry[3]
        handicap=registry[4]
        running_ps=registry[5]
        max_ps=registry[6]
    if running_ps>=max_ps :
        max_ps_reached=1
        logthis("Max. allowed processes reachead.")
    else :
        max_ps_reached=0
    return max_ps_reached


def update_running_ps(operation):
    """Adds/Substracts 1 to/from running_ps for the given server_name.
    """
    db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor=db.cursor()
    if operation == "add" :
        cursor.execute("update servers set running_ps=running_ps+1 where name='%s';" % server_name )
    elif operation == "substract" :
        cursor.execute("update servers set running_ps=running_ps-1 where name='%s';" % server_name )
    cursor.close ()
    db.commit ()
    db.close ()
    #logthis("%s running_ps" % operation)


def spawn_process(process) :
    """Spawns a process like encode.py or ftp.py. It does not wait for the spawned process to finish.
    """
    if process=="encode":
        pid = subprocess.Popen(["%s/uft-encode.py" % core_root]).pid
        logthis('Spawned %s with PID %i' % (process, pid))
    elif process=="upload":
        pid = subprocess.Popen(["%s/uft-upload.py" % core_root]).pid
        logthis('Spawned %s with PID %i' % (process, pid))
    else:
        logthis('No process named %s !' % process)
    logthis("%s spawned" % process)

def update_vp_quantity(u_quantity, u_vp_status, u_vhash):
    """Increments or decrements the total of video profiles with for the vhash on the video_original table.
    """
    status_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor=db.cursor()
    cursor.execute("update video_original set %s=%s+(%i), status_time='%s' where vhash='%s';" % (u_vp_status, u_vp_status, u_quantity, status_time, u_vhash) )
    cursor.close ()
    db.commit ()
    db.close ()
