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

# Constants about the helical parameters type
HELICAL_RISE_ROT = 0
HELICAL_PITCH_UNIT = 1
HELICAL_PARAMS_TYPE = ["rise/rotation", "pitch/unit_number"]


class SpringProtSegclassReconstruct(em.ProtInitialVolume):
    """
    Protocol based on Spring's program *segclassreconstruct*
    to compute 3D reconstruction from a single class average
    using a range of different helical symmetries

    More info:
    http://www.sachse.embl.de/emspring/programs/segclassreconstruct.html
    """
    _label = 'segclassreconstruct'

    #--------------------------- DEFINE param functions ----------------------
    
    def _defineParams(self, form):
        form.addSection('Input')
        form.addParam('inputAverages', params.PointerParam,
                      pointerClass='SetOfAverages',
                      label="Input averages", important=True,
                      help='')

        form.addParam('classNumber', params.IntParam, default=1,
                      label='Class number to be analyzed',
                      help='Class number to be analyzed (1st class is 1).'
                           'This protocol internally change to 0 starting index'
                           'in Spring.')

        line = form.addLine('Estimated helix width (A)',
                            help="Generous inner and outer diameter of helix "
                                 "required for cylindrical mask in Angstrom "
                                 "(accepted values min=0, max=1500).")

        line.addParam('innerHelixWidth', params.IntParam, default=1,
                      label='inner')
        line.addParam('outerHelixWidth', params.IntParam, default=190,
                      label='outer')

        form.addParam('helicalParamsType', params.EnumParam,
                      choices=HELICAL_PARAMS_TYPE,
                      default=HELICAL_PITCH_UNIT,

                      label='Helical params type',
                      help='Choose whether helical *rise/rotation* or '
                           '*pitch/unit_number* of units per turn pairs '
                           'are given for generating the helical lattice.'
                      )

        riseRotCond = "helicalParamsType==%s" % HELICAL_RISE_ROT
        pitchUnitCond = "helicalParamsType==%s" % HELICAL_PITCH_UNIT

        line = form.addLine('Rise range (A)', condition=riseRotCond,
                            help="Helical rise range (in Angstrom) to be "
                                 "reconstructed. "
                                 "(accepted values min=0, max=1000).")
        line.addParam('riseRangeFrom', params.FloatParam, default=1, label='from')
        line.addParam('riseRangeTo', params.FloatParam, default=10, label='to')
        line.addParam('riseStep', params.FloatParam, default=1, label='step')

        line = form.addLine('Rotation range (deg)', condition=riseRotCond,
                            help="Helical rotation range (in degrees) to be "
                                 "reconstructed. "
                                 "(accepted values min=-360, max=360).")
        line.addParam('rotRangeFrom', params.FloatParam, default=1, label='from')
        line.addParam('rotRangeTo', params.FloatParam, default=300, label='to')
        line.addParam('rotStep', params.FloatParam, default=1, label='to')

        line = form.addLine('Pitch range (A)', condition=pitchUnitCond,
                            help="Helical pitch range (in Angstrom) to be "
                                 "reconstructed. "
                                 "(accepted values min=0, max=1000).")
        line.addParam('pitchRangeFrom', params.FloatParam, default=1, label='from')
        line.addParam('pitchRangeTo', params.FloatParam, default=10, label='to')
        line.addParam('pitchStep', params.FloatParam, default=0.1, label='step')

        line = form.addLine('N. units per turn range (deg)',
                            condition=pitchUnitCond,
                            help="'Number of units per turn' range  to be "
                                 "reconstructed. "
                                 "(accepted values min=-360, max=360).")
        line.addParam('unitRangeFrom', params.FloatParam, default=1, label='from')
        line.addParam('unitRangeTo', params.FloatParam, default=300, label='to')
        line.addParam('unitStep', params.FloatParam, default=0.1, label='step')

        form.addParallelSection(threads=0, mpi=1)
    
    # --------------------------- INSERT steps functions ----------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep('convertInputStep')
        self._insertFunctionStep('runSegclassReconstruct')
        self._insertFunctionStep('createOutputStep')

    # --------------------------- STEPS functions -----------------------------

    def convertInputStep(self):
        inputAvgs = self.inputAverages.get()

        # ---------- Write particles stack as hdf file ---------
        outputBase = "input_averages.hdf"
        outputFn = self._getPath(outputBase)
        tmpStk = outputFn.replace('.hdf', '.stk')
        self.info("Writing hdf stack to: " + outputFn)
        inputAvgs.writeStack(tmpStk)
        from pyworkflow.em.packages.eman2.convert import convertImage
        convertImage(tmpStk, outputFn)
        pwutils.cleanPath(tmpStk)

        # ---------- Write txt files with parameters values -----
        outputTxt = self.getInputParamsFn()
        self.info("Writing parameters to: " + outputTxt)

        params = spring.Params()
        params['Class average stack'] = outputBase
        params['Volume name'] = 'recvol.hdf'
        params['Class number to be analyzed'] = self.classNumber.get()
        params['Pixel size in Angstrom'] = inputAvgs.getSamplingRate()
        params['Helical rise/rotation or pitch/number of units per turn '
               'choice'] = HELICAL_PARAMS_TYPE[self.helicalParamsType.get()]
        params['Estimated helix inner and outer '
               'diameter in Angstrom'] = self._getHelixWidthRange()
        params['Range of helical rise or pitch '
               'search in Angstrom'] = self._getRisePitchRange()
        params['Range of helical rotation in degrees or '
               'number of units per turn search'] = self._getRotUnitRange()
        params['Increments of helical symmetry steps in Angstrom or '
               'degrees'] = self._getStepRange()

        nMpi = self.numberOfMpi.get()
        params['MPI option'] = str(nMpi > 1)
        params['Number of CPUs'] = nMpi
        params.write(outputTxt)
            
    def runSegclassReconstruct(self):
        cmd = spring.getCommand("segclassreconstruct")
        args = ' --f %s' % os.path.basename(self.getInputParamsFn())
        args += ' --d output'
        # The program is executed in the run folder
        # MPI=1 because the program will take care of parallelization
        # given in the input_params.txt
        self.runJob(cmd, args, cwd=self._getPath(), numberOfMpi=1)

    def createOutputStep(self):
        pass

    # --------------------------- INFO functions -----------------------------

    def _validate(self):
        errors = []
        environ = spring.getEnviron()
        springHome = os.environ['SPRING_HOME']
        if not os.path.exists(springHome):
            errors.append('Missing %s' % springHome)

        classNumber = self.classNumber.get()
        n = self.inputAverages.get().getSize()
        if classNumber < 1 or classNumber > n:
            errors.append("Class number should be between 1 and %s" % n)
        return errors

    def _summary(self):
        summary = []
        return summary
    
    def _methods(self):
        return []

    def getInputParamsFn(self):
        return self._getPath("input_params.txt")

    # --------------------------- UTILS functions -----------------------------
    def _getRange(self, labelFrom, labelTo):
        """ Helper function to retrieve a range from a couple
        of label related to protocol attributes.
        """
        return (self.getAttributeValue(labelFrom),
                self.getAttributeValue(labelTo))

    def _getHelixWidthRange(self):
        return self._getRange('innerHelixWidth', 'outerHelixWidth')

    def _getRisePitchRange(self):
        if self.helicalParamsType == HELICAL_RISE_ROT:
            return self._getRange('riseRangeFrom', 'riseRangeTo')
        else:
            return self._getRange('pitchRangeFrom', 'pitchRangeTo')

    def _getRotUnitRange(self):
        if self.helicalParamsType == HELICAL_RISE_ROT:
            return self._getRange('rotRangeFrom', 'rotRangeTo')
        else:
            return self._getRange('unitRangeFrom', 'unitRangeTo')

    def _getStepRange(self):
        if self.helicalParamsType == HELICAL_RISE_ROT:
            return self._getRange('riseStep', 'rotStep')
        else:
            return self._getRange('pitchStep', 'unitStep')
