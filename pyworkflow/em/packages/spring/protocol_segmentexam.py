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

import pyworkflow.protocol.params as params
import pyworkflow.em as em
import pyworkflow.utils as pwutils

import spring
from convert import SpringDb



class SpringProtSegmentExam(em.ProtInitialVolume):
    """
    Protocol based on Spring's program *segmentexam*
    to examine all excised in-plane rotated segments and
    compute their collapsed (1D) and 2D power spectrum
    and width profile of helices.

    More info:
    http://www.sachse.embl.de/emspring/programs/segmentexam.html
    """
    _label = 'segmentexam'

    #--------------------------- DEFINE param functions ----------------------
    
    def _defineParams(self, form):
        form.addSection('Input')
        form.addParam('inputParticles', params.PointerParam,
                      pointerClass='SetOfParticles',
                      label="Input particles (segments)", important=True,
                      help='')
        form.addParam('estimatedHelixWidth', params.IntParam, default=1,
                      label='Estimated helix width (A)',
                      help="Generous width measure of helix required for "
                           "rectangular mask (accepted values min=0, "
                           "max=1500).")

        form.addParallelSection(threads=0, mpi=1)
    
    # --------------------------- INSERT steps functions ----------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep('convertInputStep')
        self._insertFunctionStep('runSegmentexam')
        self._insertFunctionStep('createOutputStep')

    # --------------------------- STEPS functions -----------------------------

    def convertInputStep(self):
        inputParts = self.inputParticles.get()

        # ---------- Write particles stack as hdf file ---------
        outputBase = "input_particles.hdf"
        outputFn = self._getPath(outputBase)
        tmpStk = outputFn.replace('.hdf', '.stk')
        self.info("Writing hdf stack to: " + outputFn)

        # --------- Write the spring.db database file -----------
        dbBase = 'spring.db'
        springDb = SpringDb(self._getPath(dbBase))
        springDb.writeSetOfParticles(inputParts, tmpStk)
        springDb.commit()
        from pyworkflow.em.packages.eman2.convert import convertImage
        convertImage(tmpStk, outputFn)
        #pwutils.cleanPath(tmpStk)

        # ---------- Write txt files with parameters values -----
        outputTxt = self.getInputParamsFn()
        self.info("Writing parameters to: " + outputTxt)
        params = spring.Params()
        params['Image input stack'] = outputBase
        params['Diagnostic plot'] = 'segmentexam_diag.pdf'
        params['Power spectrum output image'] = 'power.hdf'
        params['Pixel size in Angstrom'] = inputParts.getSamplingRate()
        params['Estimated helix width in Angstrom'] = self.estimatedHelixWidth.get()
        params['spring.db file'] = dbBase
        nMpi = self.numberOfMpi.get()
        params['MPI option'] = str(nMpi > 1)
        params['Number of CPUs'] = nMpi
        params.write(outputTxt)
            
    def runSegmentexam(self):
        cmd = spring.getCommand("segmentexam")
        args = ' --f %s' % os.path.basename(self.getInputParamsFn())
        args += ' --d output'
        # The program is executed in the run folder
        # MPI=1 because the program will take care of parallelization
        # given in the input_params.txt
        self.runJob(cmd, args, cwd=self._getPath(), numberOfMpi=1)

    def createOutputStep(self):
        pass

    # --------------------------- INFO functions ------------------------------

    def _validate(self):
        errors = []
        environ = spring.getEnviron()
        springHome = os.environ['SPRING_HOME']
        if not os.path.exists(springHome):
            errors.append('Missing %s' % springHome)
        return errors

    def _summary(self):
        summary = []
        return summary
    
    def _methods(self):
        return []

    def getInputParamsFn(self):
        return self._getPath("input_params.txt")