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
import sys

from pyworkflow.em import ImageHandler
from pyworkflow.em.data import Micrograph

from spring import SPRING_HOME


class SpringDb:
    """
    Class wrapping the Spring db and how to write different
    type of data (Micrographs, CTF, Filaments, etc).
    """
    def __init__(self, dbName):
        # Put the SPRING_HOME in the sys.path to make sure we can use
        # its Python API
        #sys.path.insert(0, SPRING_HOME)
        import csdatabase as csdb
        from csdatabase import SpringDataBase, base
        self._csdb = csdb
        self._session = SpringDataBase().setup_sqlite_db(base, dbName)

    def commit(self):
        self._session.commit()
        #sys.path.remove(SPRING_HOME)

    def _writeMic(self, mic):
        micFn = mic.getFileName()
        acq = mic.getAcquisition()
        springMic = self._csdb.CtfMicrographTable()
        springMic.dirname = os.path.dirname(micFn)
        springMic.micrograph_name = os.path.basename(micFn)
        springMic.voltage = acq.getVoltage()
        springMic.spherical_aberration = acq.getSphericalAberration()
        springMic.amplitude_contrast = acq.getAmplitudeContrast()
        springMic.ctffind_determined = False
        springMic.pixelsize = mic.getSamplingRate()
        self._session.add(springMic)
        return springMic

    def _pixelsToAngs(self, pxValue, nDigits=3):
        """ Converts from pixels to Anstrongs using the self._pixelSize. """
        return round(pxValue * self._pixelSize, ndigits=nDigits)

    def _writeSegment(self, particle, helix):
        """ Write a segment from a given particle.
        Params:
            particle: the particle that need to be written.
            mic: Spring micrograph object related to the segment.
            helix: Spring """
        segment = self._csdb.SegmentTable()
        segment.helices = helix
        segment.micrographs = helix.micrographs
        segment.stack_id = particle.getIndex() - 1 # counting starts at 0
        coord = particle.getCoordinate()
        segment.x_coordinate_A = self._pixelsToAngs(coord.getX())
        segment.y_coordinate_A = self._pixelsToAngs(coord.getX())
        self._session.add(segment)

    def _writeHelixSegments(self, filamentDict):
        """ Write the Helix and its Segments as expected by Spring
        """
        helix = self._csdb.HelixTable()
        p = filamentDict['segments'][0]
        helixId = p.getCoordinate().filamentId.get()
        helix.helix_name = "mic%03d_helix%03d" % (p.getMicId(), helixId)
        helix.micrographs = filamentDict['mic']
        helix.dirname = None
        helix.avg_inplane_angle = None
        helix.avg_curvature = None

        for segment in filamentDict['segments']:
            self._writeSegment(segment, helix)

    def writeSetOfMicrographs(self, inputMics):
        """ Create a CtfMicrographTable into this Spring db. """
        for mic in inputMics:
            self._writeMic(mic)

    def writeSetOfParticles(self, inputParts, outputStackFn):
        """ Write a set of particles (segments) into a new
        hdf stack file and spring.db database.
        """
        self._pixelSize = inputParts.getSamplingRate()
        lastMicId = None
        filamentDict = {'mic': None, 'segments': []}

        orderLabels = ['_micId', '_coordinate.filamentId', 'id']
        ih = ImageHandler()
        i = 1

        for p in inputParts.iterItems(orderBy=orderLabels):
            micId = p.getMicId()
            coord = p.getCoordinate()
            filamentId = coord.filamentId.get()

            # Write the particle into the new stack and update its location
            newLoc = (i, outputStackFn)
            ih.convert(p, newLoc)
            p.setLocation(newLoc)
            i += 1

            # Recreate micrograph info from particles
            if micId != lastMicId:
                mic = Micrograph()
                mic.setSamplingRate(self._pixelSize)
                mic.setAcquisition(p.getAcquisition())
                mic.setMicName(coord.getMicName())
                mic.setFileName(coord.getMicName())
                springMic = self._writeMic(mic)
                lastMicId = micId
                lastFilamentId = None

            if filamentId != lastFilamentId:
                if filamentDict['segments']:
                    self._writeHelixSegments(filamentDict)
                    filamentDict['segments'] = []
                filamentDict['mic'] = springMic
                lastFilamentId = filamentId

            filamentDict['segments'].append(p.clone())


def make_new_micrograph_entry_with_ctffind_parameters(self, current_mic, micrograph_file, ori_pixelsize,
                                                      ctf_parameters,
                                                      ctffind_parameters):
    if current_mic is None:
        current_mic = CtfMicrographTable()
    current_mic.dirname = os.path.dirname(micrograph_file)
    current_mic.micrograph_name = os.path.basename(micrograph_file)
    current_mic.voltage = ctf_parameters.voltage
    current_mic.spherical_aberration = ctf_parameters.spherical_aberration
    current_mic.amplitude_contrast = ctf_parameters.amplitude_contrast
    current_mic.ctffind_determined = True
    current_mic.pixelsize = ori_pixelsize

    current_mic_find = CtfFindMicrographTable()
    current_mic_find.dirname = os.path.dirname(micrograph_file)
    current_mic_find.micrograph_name = os.path.basename(micrograph_file)
    current_mic_find.pixelsize = ctf_parameters.pixelsize
    current_mic_find.ctf_micrographs = current_mic
    current_mic_find = self.update_determined_ctffind_values_for_micrograph(current_mic_find, ctffind_parameters,
                                                                            ctf_parameters.pixelsize)

    current_mic_tilt = CtfTiltMicrographTable()
    current_mic_tilt.ctf_micrographs = current_mic

    return current_mic_find, current_mic_tilt


def enter_parameters_into_segment_table(self, session, stack_id, each_helix, current_mic, helix, distances,
                                        lavg_inplane_angles, lavg_curvatures):
    if self.ctfcorrect_option:
        matched_mic_find = SegmentCtfApply().get_micrograph_from_database_by_micname(session, each_helix.micrograph,
                                                                                     self.spring_path)
    for each_segment_index, each_helix_coordinate in enumerate(each_helix.coordinates):
        if self.stepsize == 0 and each_segment_index == 0 or self.stepsize != 0:
            segment = SegmentTable()
            segment.helices = helix
            segment.micrographs = current_mic
            segment.stack_id = stack_id
            x_coordinate = self.round_and_calculate_coordinate_in_Angstrom(each_helix_coordinate[0], self.pixelsize)
            y_coordinate = self.round_and_calculate_coordinate_in_Angstrom(each_helix_coordinate[1], self.pixelsize)
            segment.x_coordinate_A = x_coordinate
            segment.y_coordinate_A = y_coordinate

            picked_x_coordinate = \
                self.round_and_calculate_coordinate_in_Angstrom(
                    each_helix.picked_coordinates[each_segment_index][0],
                    self.pixelsize)

            picked_y_coordinate = \
                self.round_and_calculate_coordinate_in_Angstrom(
                    each_helix.picked_coordinates[each_segment_index][1],
                    self.pixelsize)

            segment.picked_x_coordinate_A = picked_x_coordinate
            segment.picked_y_coordinate_A = picked_y_coordinate
            segment.distance_from_start_A = distances[each_segment_index]
            segment.inplane_angle = each_helix.inplane_angle[each_segment_index]
            segment.curvature = each_helix.curvature[each_segment_index]
            segment.lavg_inplane_angle = lavg_inplane_angles[each_segment_index]
            segment.lavg_curvature = lavg_curvatures[each_segment_index]

            segment_info = self.make_segment_info_named_tuple()
            each_segment = segment_info._make([current_mic.id, x_coordinate, y_coordinate])
            if self.ctfcorrect_option:
                ctf_params, avg_defocus, astigmatism, astig_angle = \
                    SegmentCtfApply().get_ctfparameters_from_database(self.ctffind_or_ctftilt_choice,
                                                                      self.astigmatism_option, self.pixelsize,
                                                                      session, each_segment, matched_mic_find,
                                                                      self.spring_path)

                session, segment = \
                    SegmentCtfApply().update_ctfparameters_in_database(self.ctffind_or_ctftilt_choice,
                                                                       self.convolve_or_phaseflip_choice,
                                                                       self.astigmatism_option, session, segment,
                                                                       avg_defocus,
                                                                       astigmatism, astig_angle)

            if len(each_helix.coordinates) >= 3 and self.stepsize != 0:
                polyfit, filtered_x, filtered_y = self.fit_square_function_path_of_coordinates(self.segsizepix * \
                                                                                               1.5,
                                                                                               each_helix.coordinates,
                                                                                               each_helix_coordinate,
                                                                                               each_helix_coordinate,
                                                                                               each_helix.inplane_angle[
                                                                                                   each_segment_index])

                segment.second_order_fit = polyfit[0] * self.pixelsize
            else:
                segment.second_order_fit = 0
            session.add(segment)
            stack_id += 1

    return session, stack_id