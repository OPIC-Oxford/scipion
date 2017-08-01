# **************************************************************************
# *
# * Authors:        J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *
# *  [1] SciLifeLab, Stockholm University
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
from collections import OrderedDict

from pyworkflow.utils import Environ

SPRING_HOME = os.environ.get('SPRING_HOME',
                             os.path.join(os.environ['EM_ROOT'], 'spring'))


def getEnviron():
    """ Create the needed environment for Xmipp programs. """
    environ = Environ(os.environ)

    SPRING_BIN = os.path.join(SPRING_HOME, 'bin')

    environ.update({'PATH': SPRING_BIN},
                   position=Environ.BEGIN
                   )
    return environ


class Params(OrderedDict):
    """ Handler class to store parameters list
     as key = value pairs for Spring.
     Parameters can be written to a text file
     to be used in the command line.
     """

    def write(self, fileName):
        with open(fileName, 'w') as f:
            maxWidth = max(len(k) for k in self.keys()) + 1
            for k, v in self.iteritems():
                print >> f, "%s = %s" % (k.ljust(maxWidth), v)