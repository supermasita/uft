#!/usr/bin/env python
"""
        Quicktime/MP4 Fast Start
        ------------------------
        Enable streaming and pseudo-streaming of Quicktime and MP4 files by
        moving metadata and offset information to the front of the file.

        This program is based on qt-faststart.c from the ffmpeg project, which is
        released into the public domain, as well as ISO 14496-12:2005 (the official
        spec for MP4), which can be obtained from the ISO or found online.

        The goals of this project are to run anywhere without compilation (in
        particular, many Windows and Mac OS X users have trouble getting
        qt-faststart.c compiled), to run about as fast as the C version, to be more
        user friendly, and to use less actual lines of code doing so.

        Features
        --------

            * Works everywhere Python can be installed
            * Handles both 32-bit (stco) and 64-bit (co64) atoms
            * Handles any file where the mdat atom is before the moov atom
            * Preserves the order of other atoms
            * Can replace the original file (if given no output file)

        Installing from PyPi
        --------------------

        To install from PyPi, you may use easy_install or pip::

            easy_install qtfaststart

        Installing from source
        ----------------------

        Download a copy of the source, ``cd`` into the top-level
        ``qtfaststart`` directory, and run::

            python setup.py install

        If you are installing to your system Python (instead of a virtualenv), you
        may need root access (via ``sudo`` or ``su``).

        Usage
        -----
        See ``qtfaststart --help`` for more info! If outfile is not present then
        the infile is overwritten.

            $ qtfaststart infile [outfile]

        To run without installing you can use::

            $ bin/qtfaststart infile [outfile]

        History
        -------
            * 2011-11-01: Fix long-standing os.SEEK_CUR bug, version bump to 1.6
            * 2011-10-11: Packaged and published to PyPi by Greg Taylor
              <gtaylor AT duointeractive DOT com>, version bump to 1.5.
            * 2010-02-21: Add support for final mdat atom with zero size, patch by
              Dmitry Simakov <basilio AT j-vista DOT ru>, version bump to 1.4.
            * 2009-11-05: Added --sample option. Version bump to 1.3
            * 2009-03-13: Update to be more library-friendly by using logging module,
              rename fast_start => process, version bump to 1.2
            * 2008-10-04: Bug fixes, support multiple atoms of the same type,
              version bump to 1.1
            * 2008-09-02: Initial release

        License
        -------
        Copyright (C) 2008 - 2011  Daniel G. Taylor <dan@programmer-art.org>

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.

        https://github.com/danielgtaylor/qtfaststart
"""

"""
    Command line script for convenience. If this is in your path, you should
    be able to run it directly like this::

        qtfaststart
"""

import logging
import os
import shutil
import sys
import tempfile

# Add parent directory to sys.path so that running from dev environment works
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

from optparse import OptionParser
from qtfaststart import VERSION
from qtfaststart import processor
from qtfaststart.exceptions import FastStartException

log = logging.getLogger("qtfaststart")

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO, stream = sys.stdout,
                        format = "%(message)s")

    parser = OptionParser(usage="%prog [options] infile [outfile]",
                          version="%prog " + VERSION)

    parser.add_option("-d", "--debug", dest="debug", default=False,
                      action="store_true",
                      help="Enable debug output")
    parser.add_option("-l", "--list", dest="list", default=False,
                      action="store_true",
                      help="List top level atoms")
    parser.add_option("-s", "--sample", dest="sample", default=False,
                      action="store_true",
                      help="Create a small sample of the input file")

    options, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if options.list:
        index = processor.get_index(open(args[0], "rb"))

        for atom, pos, size in index:
            print atom, "(" + str(size) + " bytes)"

        raise SystemExit

    if len(args) == 1:
        # Replace the original file!
        if options.sample:
            print "Please pass an output filename when used with --sample!"
            raise SystemExit(1)

        tmp, outfile = tempfile.mkstemp()
        os.close(tmp)
    else:
        outfile = args[1]

    limit = 0
    if options.sample:
        # Create a small sample (4 MiB)
        limit = 4 * (1024 ** 2)

    try:
        processor.process(args[0], outfile, limit = limit)
    except FastStartException:
        # A log message was printed, so exit with an error code
        raise SystemExit(1)

    if len(args) == 1:
        # Move temp file to replace original
        shutil.move(outfile, args[0])
