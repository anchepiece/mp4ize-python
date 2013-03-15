#!/usr/bin/env python
# coding=utf-8
#
# This is a python implementation of the mp4ize ruby script available here:
#     http://thomer.com/howtos/mp4ize
#
# Original Work:
#
# Copyright (C) 2007-2010 Thomer M. Gil [http://thomer.com/]
#
# Thanks to Brian Moore, Justin Payne, Matt Spitz, Martyn Parker,
# Jean-Francois Macaud, Thomas Hannigan, Anisse Astier, Juanma HernÃ¡ndez,
# Trung Huynh, and Mark Ryan for bugfixes and suggestions.
#
# Oct. 14, 2008: show percentage progress. add -t and -w flags.
# Jan. 11, 2009: switch to bit/s bitrates for newer ffmpeg versions.
#                add --iphone option.
#                add -y option to ffmpeg (overwrite).
# Jan. 20, 2009: don't exit early when processing multiple files.
# Feb. 17, 2009: deal with "Invalid pixel aspect ratio" error.
# Apr.  1, 2009: new --outdir parameter.
# May  22, 2009: handle filenames with quotes and whitespace.
# Oct   6, 2009: fix bug where we forget to read stderr
# Nov.  5, 2009: fix -v, -t, and -w command line options
#                removed bogus 'here' debug statement
# Oct. 27, 2010: assume ffmpeg 0.6: use libxvid and libfaac by default,
#                add "k" to -bufsize, -ab, and -b parameters.
# May   2, 2011: added iphone4 option
#                use ffmpeg, not /usr/bin/ffmpeg
# May   3, 2011: changed codec from libfaac to aac
#
# This program is free software. You may distribute it under the terms of
# the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# mp4ize.py License:
#
# Copyright (c) 2010 anchepiece
# All rights reserved.
#
# This program is free software. You may distribute it under the terms of
# the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
#   http://www.gnu.org/licenses/gpl-2.0.html
#
##############################################################################
#
# This program converts video files to mp4, suitable to be played on an iPod
# or an iPhone. It is careful about maintaining the proper aspect ratio.
#
##############################################################################


# Please be careful that all syntax used in this file can be parsed on
# Python 1.5 -- this version check is not evaluated until after the
# entire file has been parsed.
import sys
if sys.hexversion < 0x02020000:
  print 'This script requires Python 2.2 or later.'
  print 'Currently run with version: %s' % sys.version
  sys.exit(1)

import os
import re
import time

try:
  # Replace md5 which is depreciated in Python2.5
  import hashlib
  md5_hash = hashlib.md5()
except ImportError:
  # Fallback to md5 to ensure Python2.4 compatibility
  import md5
  md5_hash = md5.new()

# True and False were introduced in Python2.2.2
try:
  testTrue=True
  del testTrue
except NameError:
  True=1
  False=0

# allow disabling of pyc generation. Only works on python >= 2.6
if os.getenv("PYTHON_NO_OPTIMIZE"):
    try:
        sys.dont_write_bytecode = True
    except:
        pass

if sys.platform == 'linux2':
    # Set process name.  Only works on Linux >= 2.1.57.
    try:
        import ctypes
        libc = ctypes.CDLL('libc.so.6')
        # 15 = PR_SET_NAME
        prog = sys.argv[0].strip('./')
        libc.prctl(15, prog, 0, 0, 0)
    except:
        pass


##############################################################################

import os, os.path, sys, socket, time, argparse, shlex, email, mailbox 
from subprocess import *
import fcntl, select

##############################################################################

DEFAULT_BIN = 'ffmpeg'
DEFAULT_ARGS = '-f mp4 -y -vcodec libxvid -maxrate 1000 -mbd 2' + \
               ' -qmin 3 -qmax 5 -g 300 '
#CODEC_AAC = '-acodec libfaac'
CODEC_AAC = '-acodec aac -strict experimental'
DEFAULT_ARGS += CODEC_AAC

DEFAULT_BUFSIZE = '4096k'
DEFAULT_AUDIO_BITRATE = '128k'
DEFAULT_VIDEO_BITRATE = '400k'
DEFAULT_OUTDIR = './'
IPOD_WIDTH = 320.0
IPOD_HEIGHT = 240.0
IPHONE_WIDTH = 480.0
IPHONE_HEIGHT = 320.0
IPHONE4_WIDTH = 960.0
IPHONE4_HEIGHT = 640.0
    
_prog = sys.argv[0]
__version__ = '1.0'
__usage__ = \
"""
    Usage: mp4ize file1.avi [file2.mpg [file3.asf [...]]]   
"""

##############################################################################

def process(options):
 
 
    print 'Using options:'
    print '    %s' % options    
    if type(options.outdir).__name__ == 'list':
        options.outdir = options.outdir[0]

    if os.path.isdir(options.outdir):
        print 'Have a verified output directory: %s' % options.outdir
    else:
        print 'Error: NOT A VALID output directory: %s' % options.outdir
        # TODO resort to default dir?
        sys.exit(1)
        return

    files = []
    for f in options.input:
        try:
            path = f
            if type(f).__name__ == 'list':
                path = f[0]        
            if os.path.isfile(path):
                files.append(path)
            else:
                raise RuntimeError('Input path must be a file: %s' % path)
        except RuntimeError as (strerror):
            print "Error:", (strerror)                      
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    #ok we checked the status of inputs, lets process them
    process_files(files, options)
    
    
def process_files(files, options):

    if len(files) == 0:
        print 'Error: no valid files could be found.'
        sys.exit(1)
        return

    print 'Found %s files to be processed' % len(files)
    for f in files:
        print '    processing: %s' % f    
        outfile = os.path.splitext(os.path.basename(f))[0] + '.mp4'
        outfile = os.path.join(options.outdir, outfile)
        print '    outfile:', outfile        

        # open the file to figure out the aspect ratio
        duration, time_f, w, h = 0.0, 0.0, 0, 0
        cmd = DEFAULT_BIN + ' -i "%s" ' % f
        print cmd
        print ''
        returncode, output = encode(cmd)

        pattern = re.compile('.*Invalid data.*')
        m = pattern.search(output)
        if not m:
            pattern = re.compile( r'Video:.+ (\d+)x(\d+)' )        
            m = pattern.search(output)
            if m:
                w = float(m.group(1))
                h = float(m.group(2))
            
            pattern = re.compile( r'Duration:\s+(\d+):(\d+):(\d+)\.(\d+)' )              
            m = pattern.search(output)
            if m:                
                duration += float(m.group(1))*3600
                duration += float(m.group(2))*60
                duration += float(m.group(3))
                duration += float(m.group(4)) / 10                                             
            
            print 'Got values from input: w=%s h=%s duration=%s' % (
                w, h, duration)

        if duration == 0 or w == 0 or h == 0:
            print output
            print 'Error: Could not interpret file as proper video: %s' % f
            continue

        aspect = w/h
        user_width = options.width
        user_height = options.height

        width = int(options.width)
        height = int(width/float(aspect))    
        height -= (height % 2)
      
        pad = int((user_height - float(height)) / 2.0)
        pad -= (pad % 2)
        pad = abs(pad)
        padarg1, padarg2 = "padtop", "padbottom"
        
        #print aspect, user_width, user_height, width, height, pad
        #print ''
        
        if os.path.exists(outfile):
            print 'Removing existing output: %s' % outfile
#             val = raw_input('File exists. Overwrite [N/y]: ')
#             if val != 'y':
#                 sys.exit(1)            
            os.remove(outfile)
            
        cmd = ('{0} -i "{1}" {2} -bufsize {3} -s {4}x{5} -{6} {7}' + \
            ' -{8} {7} -ab {9} -b {10} "{11}"').format(
            DEFAULT_BIN, f, DEFAULT_ARGS, DEFAULT_BUFSIZE, 
            width, height, padarg1, pad, padarg2, 
            options.audio, options.video, outfile)
        print cmd
        print ''
        returncode, output = encode(cmd, duration)
        if returncode == 0:
            time_f = verify_output(output)                
        else: 
            pattern = re.compile('.*Invalid pixel aspect ratio.*')
            if pattern.search(output):
                # lets try again while forcing an aspect ratio
                print 'Invalid pixel aspect ratio, ' + \
                    'running again with source ratio'
                cmd = ('{0} -i "{1}" {2} -bufsize {3} -s {4}x{5} -{6} {7}' + \
                    ' -{8} {7} -aspect {12} -ab {9} -b {10} "{11}"').format(
                     DEFAULT_BIN, f, DEFAULT_ARGS, DEFAULT_BUFSIZE, 
                     width, height, padarg1, pad, padarg2, 
                     options.audio, options.video, outfile, aspect)
                print cmd
                print ''
                returncode, output = encode(cmd, duration)
                if returncode == 0:
                    print 'Complete.'
                    time_f = verify_output(output)   
                else:
                    print output  
                    print 'Error: Video encoding failed' + \
                            ' (with forced aspect ratio)'                
            else:
                print output
                print 'Error: Video encoding failed'

        duration = float(duration)
        time_f = float(time_f)
        print "source duration: %s" % duration
        print "destination duration: %s" % time_f
        if ((time_f <= duration * 1.01) and (time_f >= duration * 0.99)):
            print 'Good result!'
            sys.exit(0)       
        else: 
            print 'Error: Got bad result!'
            sys.exit(1)
    
def encode(cmd, duration=0):
    result = ''
    time_f = 0
    args = shlex.split(cmd)
    p = Popen (args, stdout=PIPE, stderr=PIPE, shell=False)

    fcntl.fcntl(
        p.stderr.fileno(),
        fcntl.F_SETFL,
        fcntl.fcntl(p.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
    )
    while True:
        # wait for I/O completion
        readx = select.select([p.stderr.fileno()], [], [])[0]
        if readx:
            chunk = p.stderr.read()
            if chunk == '':
                break
            result = chunk                
            tmp_time_f = verify_output(chunk)
            if tmp_time_f:
                time_f = tmp_time_f
                if duration:
                    percent = (float(time_f)/float(duration))*100
                    sys.stderr.write('  %2d%% Completed [position %ss] \r'
                         % (percent, time_f))                    
                else:
                    sys.stderr.write(' time=%s \r' % time_f)
        time.sleep(.1)
    p.wait()
    return p.returncode, result
    
def verify_output(output):
    time_f = 0
    pattern = re.compile( r'time=([^\s]+)' )
    if type(output).__name__ == 'tuple':            
        m = pattern.search(output[0])
        if m:
            print 'got result in stdout'
            time_f = m.group(1)
        m = pattern.search(output[1])
        if m:
            print 'got result in stderr'        
            time_f = m.group(1)
    else:
        pattern = re.compile( r'time=([^\s]+)' )                                 
        for line in output.split('\n'):
            m = pattern.search(line)
            if m:
                time_f = m.group(1)
    return time_f

##############################################################################

def main(argv):
    usage = __usage__    
    description=usage


    def valid_dir(string):
        value = str(string)
        if not os.path.isabs(value):
            value = os.path.abspath(value)
        if not os.path.exists(value):
            msg = "Nonexistent path: %s" % value
            raise argparse.ArgumentTypeError(msg)
        return value    

    parser = argparse.ArgumentParser(
        description='encode videos to mp4 for an iPod or an iPhone')

    parser.add_argument('--version', action='version', 
        version='%s %s' % (_prog, __version__),
        help='show program verison')
    parser.add_argument('input', metavar=('file'), type=str, nargs='+', 
        help='list of file names to process')
        # setting defaults creates a value in args, 
        #   otherwise the value passed will be None
    parser.add_argument('-a', '--audio', metavar='RATE', type=str, 
        default=DEFAULT_AUDIO_BITRATE,
        help='override default audio bitrate (%(default)s)' )    
    parser.add_argument('-b', '--video', metavar='RATE', type=str,  
        default=DEFAULT_VIDEO_BITRATE,
        help='override default video bitrate (%(default)s)' )    
    parser.add_argument('-v', '--verbose', action='store_true')   
    parser.add_argument('-w', '--width', type=int, 
        default=int(IPOD_WIDTH),
        help='override default width (%(default)s)')    
    parser.add_argument('-t', '--height', type=int, 
        default=int(IPOD_HEIGHT),
        help='override default height (%(default)s)' )
    parser.add_argument('-i', '--iphone', action='store_true', 
        default='%dx%d' % (IPHONE_WIDTH, IPHONE_HEIGHT),
        help='use default iphone height and width (%(default)s)') 
    parser.add_argument('-4', '--iphone4', action='store_true', 
        default='%dx%d' % (IPHONE4_WIDTH, IPHONE4_HEIGHT),
        help='use default iphone4 height and width (%(default)s)')     

    parser.add_argument('-o', '--outdir', metavar='dir', type=valid_dir, 
        default=DEFAULT_OUTDIR,
        help='write files to given directory')        

    args = parser.parse_args()
    if args.iphone:
        args.width = IPHONE_WIDTH
        args.height = IPHONE_HEIGHT
    if args.iphone4:
        args.width = IPHONE4_WIDTH
        args.height = IPHONE4_HEIGHT        
    process(args)

##############################################################################

if __name__ == '__main__':
    main(sys.argv)

##############################################################################
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
