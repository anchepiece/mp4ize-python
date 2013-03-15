# mp4ize, python, mp4ize-python (dev)

Welcome!
====================
This is the current development version of [mp4ize-python](http://github.com/anchepiece/mp4ize-python/).

Original Work
====================
This is a python implementation of the mp4ize ruby script available here:

[http://thomer.com/howtos/mp4ize](http://thomer.com/howtos/mp4ize)

[Convert any video file for an iPod or iPhone](http://thomer.com/howtos/ipod_video.html)

Copyright (C) 2007-2010 [Thomer M. Gil](http://thomer.com/)


mp4ize python
====================
This program converts video files to mp4, suitable to be played on an iPod
or an iPhone. It is careful about maintaining the proper aspect ratio.

Requirements
====================
 - python
 - python-argparse
 - ffmpeg
 - libavcodec-extra-52

Usage
====================
A simple script to provide a simple, easy to use interface to calculate a span
of time between two dates.  To be able to calculate a future date based on a
span of time.  To illustrate the difference in time using conventional methods
that are technically accurate.

    usage: mp4ize.py [-h] [--version] [-a RATE] [-b RATE] [-v] [-w WIDTH]
                     [-t HEIGHT] [-i] [-4] [-n THREADS] [-o dir] [-f]
                     file [file ...]

    encode videos to mp4 for an iPod or an iPhone

    positional arguments:
      file                  list of file names to process

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program verison
      -a RATE, --audio RATE
                            override default audio bitrate (128k)
      -b RATE, --video RATE
                            override default video bitrate (400k)
      -v, --verbose
      -w WIDTH, --width WIDTH
                            override default width (320)
      -t HEIGHT, --height HEIGHT
                            override default height (240)
      -i, --iphone          use default iphone height and width (480x320)
      -4, --iphone4         use default iphone4 height and width (960x640)
      -n THREADS, --threads THREADS
                            number of encoding threads
      -o dir, --outdir dir  write files to given directory
      -f, --force           overwrite .mp4 if it already exists


