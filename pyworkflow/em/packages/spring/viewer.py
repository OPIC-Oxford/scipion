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

from pyworkflow.viewer import DESKTOP_TKINTER, WEB_DJANGO
from pyworkflow.em.viewer import Viewer, CommandView

from protocol_segclassreconstruct import SpringProtSegclassReconstruct
import spring

    
class SpringViewerSegGridExplore(Viewer):
    """ Wrapper to visualize different type of objects
    with the Xmipp program xmipp_showj. """
    
    _environments = [DESKTOP_TKINTER, WEB_DJANGO]
    _targets = [SpringProtSegclassReconstruct]
    _label = 'seggridexplore'

    def _visualize(self, obj, **args):
        baseOutput = 'seggridexplore_params.txt'
        outputTxt = obj._getPath(baseOutput)
        print("Writing parameters to: " + outputTxt)

        params = spring.Params()
        params['Grid database'] = 'output/grid.db'
        params['Batch mode'] = False
        params['EM name'] = 'recvol.hdf'
        params.write(outputTxt)
        cmd = spring.getCommand('seggridexplore')
        cmd += ' --f %s' % baseOutput
        return [CommandView(cmd,
                            env=spring.getEnviron(),
                            cwd=obj.getWorkingDir())]