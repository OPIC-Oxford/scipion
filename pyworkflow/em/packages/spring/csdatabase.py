# Author: Carsten Sachse 11-Sep-2011
# Copyright: EMBL (2010 - 2016)
# License: see license.txt for details
"""
Database table definitions for Spring parameters
"""
from collections import OrderedDict
from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean, create_engine, text, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, mapper
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.types import TIMESTAMP


class SpringDataBaseCommonMicrograph(object):
    def get_ctf_determined_hint(self):
        return 'CTF determined using'
    
    def define_defocus(self, ctfmethod, df1ordf2):
        defocus = Column(Float, info={'hints':'{0} defocus ({1} - maximum extension of Thon ellipse) in Angstrom'.\
                                      format(ctfmethod, df1ordf2)})
        
        return defocus
    
    
class SpringDataBaseCommonSegment(SpringDataBaseCommonMicrograph):
    def get_segment_center_on_micrograph_hint(self):
        return 'of segment center on micrograph'
    
    
class SpringDataBaseCommonRefinement(SpringDataBaseCommonSegment):
    def get_exp_sim_power_hint(self):
        return 'between experimental and simulated power spectrum.'
    
    def get_exp_sim_class_avg_hint(self):
        return 'between experimental and simulated class average.'
        
    def get_excluded_segment_count_hint(self, count_or_ratio='count'):
        return 'Excluded segment {0} based on '.format(count_or_ratio) 
    
    def define_fsc(self):
        fsc_0143 = Column(Float, info={'label':'FSC cutoff 0.143', 'hints':'Fourier shell correlation at 0.143 cutoff ' + \
                                       'Rosenthal/Henderson criterion in Angstrom.'})
        
        fsc_05 = Column(Float, info={'label':'FSC cutoff 0.5', 'hints':'Fourier shell correlation at 0.5 cutoff ' + \
                                     'criterion in Angstrom.'})
        
        return fsc_0143, fsc_05
    
    
    def define_helical_ccc(self):
        hint = 'from all asymmetric unit views with their corresponding reprojections.'
        helical_ccc_error = Column(Float, info={'label':'Helical CCC error', 'hints':'Mean of standard deviations ' + \
                                                'of CCC values ' + hint})
        mean_helical_ccc = Column(Float, info={'label':'Mean helical CCC', 'hints':'Mean of CCC values ' + \
                                               hint})
        out_of_planne_dev = Column(Float, info={'label':'Out of plane tilt deviation', 'hints':'Standard deviation' + \
                                                'of out-of-plane tilt angles '})
        
        return helical_ccc_error, mean_helical_ccc, out_of_planne_dev
    
    
    def define_amplitude_correlation(self):
        amp_correlation = Column(Float, info={'label':'Average amplitude correlation', 'hints': self.get_exp_sim_power_hint(),
                                              'min':0, 'max':1})
        
        amp_corr_quarter_nyquist = Column(Float, info={'label':'Average amplitude correlation up to quarter Nyquist ' + \
        'cutoff', 'hints': self.get_exp_sim_power_hint(), 'min':0, 'max':1})
        
        amp_corr_half_nyquist = Column(Float, info={'label':'Average amplitude correlation up to half Nyquist cutoff', 
        'hints': self.get_exp_sim_power_hint(), 'min':0, 'max':1})
        
        amp_corr_3quarter_nyquist = Column(Float, info={'label':'Average amplitude correlation up to three quarter ' + \
        'Nyquist cutoff', 'hints': self.get_exp_sim_power_hint(), 'min':0, 'max':1})
        
        return amp_correlation, amp_corr_quarter_nyquist, amp_corr_half_nyquist, amp_corr_3quarter_nyquist
    
    
    def define_additional_criteria(self):
        variance = Column(Float, info={'label':'Variance', 'hints':'of 3D reconstruction.'})
        
        mean_peak = Column(Float, info={'label':'Mean peak', 'hints':'of projection matching between experimental ' + \
                                        'images and reprojections.'})
        
        xshift_error = Column(Float, info={'label':'Shift error perpendicular to helix in Angstrom', 'hints':'derived ' + \
                                           'from RMS deviation of forward difference between successive segments.'})
        
        inplane_error = Column(Float, info={'label':'In-plane rotation error perpendicular to helix in degrees', 
                        'hints':'derived from RMS deviation of forward difference between successive segments.'})
        
        outofplane_error = Column(Float, info={'label':'Out-of-plane tilt error to helix in degrees', 
                        'hints':'derived from RMS deviation of forward difference between successive segments.'})

        return variance, mean_peak, xshift_error, inplane_error, outofplane_error
    
    
    def define_excluded_criteria(self, count_or_ratio='count'):
        excluded_out_of_plane_tilt_count = Column(Float, info={'label':'Excluded out-of-plane segment {0}'.\
                            format(count_or_ratio), 'hints':' based on out-of-plane tilt angle criterion'})
        
        excluded_inplane_count = Column(Float, info={'label':'Excluded inplane segment {0}'.format(count_or_ratio), 
                                                     'hints':' based on in-plane rotation angle criterion'})
        
        total_excluded_count = Column(Float, info={'label':'Excluded segment {0}'.format(count_or_ratio), 'hints':
                                                   ' based on applied refinement criteria'})
    
        return excluded_out_of_plane_tilt_count, excluded_inplane_count, total_excluded_count
    
    
    def define_azimuth_angle_statitistics(self):
        asym_unit_count = Column(Integer, info={'label':'Asymmetric unit count', 'hints': 'Number of asymmetric ' + \
                                                'units included in 3D reconstruction.'})
    
        avg_azimuth_sampling = Column(Float, info={'label':'Azimuthal sampling average', 'hints': 
                                    'Average of sampling of phi angles around helical axis', 'min':0, 'max':360})
    
        dev_azimuth_sampling = Column(Float, info={'label':'Azimuthal sampling standard deviation', 'hints': 
                                    'Standard deviation of sampling of phi angles around helical axis', 
                                    'min':0, 'max':360})
        
        return asym_unit_count, avg_azimuth_sampling, dev_azimuth_sampling
    
    
class SpringDataBaseCommon(SpringDataBaseCommonRefinement):
    pass 


base = declarative_base()
class CtfMicrographTable(base):
    __tablename__ = 'CtfMicrographs'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    dirname = Column(String)
    micrograph_name = Column(String) 
    pixelsize = Column(Float)
    spherical_aberration = Column(Float, info={'hints':'Spherical aberration (mm)'})
    voltage = Column(Float, info={'hints':'Voltage (kV)'})
    amplitude_contrast = Column(Float, info={'hints':'Amplitude contrast in percent'})
    ctffind_determined = Column(Boolean, info={'hints':SpringDataBaseCommon().get_ctf_determined_hint() + ' CTFFIND'})
    ctftilt_determined = Column(Boolean, info={'hints':SpringDataBaseCommon().get_ctf_determined_hint() + ' CTFTILT'})
    
    
class CtfFindMicrographTable(base):
    __tablename__ = 'CtfFindMicrographs'
    
    id = Column(Integer, ForeignKey('CtfMicrographs.id'), primary_key=True)

    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    dirname = Column(String)
    micrograph_name = Column(String) 
    pixelsize = Column(Float, info={'hints':'Pixel size in Angstrom'})
    
    defocus_avg = Column(Float, info={'hints':'Average CTFFIND defocus in Angstrom'})
    
    defocus1 = SpringDataBaseCommon().define_defocus('CTFFIND', 'DF1')
    defocus2 = SpringDataBaseCommon().define_defocus('CTFFIND', 'DF2')
    
    astigmation_angle = Column(Float, info={'hints':'CTFFIND astigmation angle in degrees'})
    cc_score = Column(Float, info={'hints':'CTFFIND cross-correlation value'})
    resolution_fit = Column(Float, info={'hints':'CTFFIND resolution fit value'})
    
    ctf_micrographs = relationship('CtfMicrographTable', backref='CtfFindMicrographs')
    

class CtfTiltMicrographTable(base):
    __tablename__ = 'CtfTiltMicrographs'
    
    id = Column(Integer, ForeignKey('CtfMicrographs.id'), primary_key=True)
    
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    ctffind_id = Column(Integer, ForeignKey('CtfFindMicrographs.id'))
    
    defocus_avg = Column(Float, info={'hints':'Average CTFTILT defocus in Angstrom'})
    
    defocus1 = SpringDataBaseCommon().define_defocus('CTFTILT', 'DF1')
    defocus2 = SpringDataBaseCommon().define_defocus('CTFTILT', 'DF2')
    
    astigmation_angle = Column(Float, info={'hints':'CTFTILT astigmation angle in degrees', 'min':0, 'max':360})
    
    tilt_angle = Column(Float, info={'hints':'CTFTILT tilt angle'})
    tilt_axis = Column(Float, info={'hints':'CTFTILT tilt axis'})
    center_x = Column(Float, info={'hints':'CTFTILT center x'})
    center_y = Column(Float, info={'hints':'CTFTILT center y'})
    cc_score = Column(Float, info={'hints':'CTFTILT cross-correlation value'})
    
    ctf_micrographs = relationship('CtfMicrographTable', backref='CtfTiltMicrographs')
    ctffind_ids = relationship('CtfFindMicrographTable', backref='CtfTiltMicrographs')

    
class HelixTable(base):
    __tablename__ = 'helices'

    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    mic_id = Column(Integer, ForeignKey('CtfMicrographs.id'))
    
    helix_name = Column(String, info={'hints':'Helix name according to base name of coordinate file'})
    dirname = Column(String, info={'hints':'Absolute directory of helix coordinate file'})
    
    avg_inplane_angle = Column(Float, info={'hints':'Overall average in-plane rotation angle of helix based on ' + \
    'coordinates', 'min':0, 'max':360})
    
    flip_inplane_angle = Column(Boolean, info={'hints':'In case of polar helices whether angle was flipped by 180 ' + \
    'degrees according to predominant in-plane rotation with respect to reference'})
    
    avg_curvature = Column(Float, info={'hints':'Overall average curvature of helix', 'min':0, 'max':1})
    avg_ccc_layer = Column(Float, info={'hints':'Overall average cross-correlation of layer-line at certain position'})
    ccc_layer_position_start = Column(Float, info={'hints':'Starting position of layer line in 1/Angstrom'})
    ccc_layer_position_end = Column(Float, info={'hints':'Ending position of layer line in 1/Angstrom'})
    avg_theta = Column(Float, info={'hints':'Overall average theta angle'})
    length = Column(Float, info={'hints':'Length of helix in Anstrom'})
    lavg_distance_A = Column(Float, info={'hints':'Local averaging distance in Angstrom'})
    
    micrographs = relationship('CtfMicrographTable', backref='helices')
    

class SegmentTable(base):
    __tablename__ = 'segments'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    stack_id = Column(Integer, info={'hints':'Image id on stack'})
    helix_id = Column(Integer, ForeignKey('helices.id'))
    class_id = Column(Integer, info={'label':'Class id', 'hints':'Assigned class id based on classification'})

    class_model_id = Column(Integer, info={'label':'Class model id', 
    'hints':'Assigned model id based on projection matching between models and classes'})

    mic_id = Column(Integer, ForeignKey('CtfMicrographs.id'))
    
    inplane_angle = Column(Float, info={'label':'in-plane rotation angle (degrees)', 'hints':'of segment based on ' + \
                                        'picked coordinates', 'min':0, 'max':360})
    curvature = Column(Float, info={'label':'curvature', 'hints':'of segment based on coordinates', 'min':0, 'max':360})
    second_order_fit = Column(Float, info={'label':'second-order fit', 'hints':'of polynomial against helix path ' + \
                                           'within segment'})
    
    x_coordinate_A = Column(Float, info={'label':'x-coordinate (Angstrom)',
    'hints':SpringDataBaseCommon().get_segment_center_on_micrograph_hint()})
    
    y_coordinate_A = Column(Float, info={'label':'y-coordinate (Angstrom)', 
    'hints':SpringDataBaseCommon().get_segment_center_on_micrograph_hint()})
    
    picked_x_coordinate_A = Column(Float, info={'label':'picked x-coordinate (Angstrom)', 
    'hints':SpringDataBaseCommon().get_segment_center_on_micrograph_hint()})
    
    picked_y_coordinate_A = Column(Float, info={'label':'picked y-coordinate (Angstrom)', 
    'hints':SpringDataBaseCommon().get_segment_center_on_micrograph_hint()})
    
    distance_from_start_A = Column(Float, info={'label':'distance along helix (Angstrom)', 'hints':'of segment ' + \
                                                'center from helix start'})
    phi = Column(Float)
    theta = Column(Float)
    psi = Column(Float)
    ccc_prj = Column(Float, info={'hints':'Peak of maximum correlation after five parameter search'})
    ccc_layer = Column(Float, info={'label': 'amplitude correlation', 'hints':'along layer-line region of segment'})
    
    lavg_inplane_angle = Column(Float, info={'hints':'Local average in-plane rotation angle of segment in degrees',
    'min':0, 'max':360})
    
    lavg_curvature = Column(Float, info={'hints':'Local average curvature of segment in degrees', 'min':0, 'max':360})
    lavg_ccc_layer = Column(Float, info={'hints':'Local amplitude correlation average'})
    lavg_theta = Column(Float, info={'hints':'Local average of Euler angle theta', 'min':0, 'max':360})
    
    ctffind_applied = Column(Boolean, info={'hints':'CTFFIND values applied to segments'})
    ctftilt_applied = Column(Boolean, info={'hints':'CTFTILT values applied to segments'}) 
    ctf_astigmatism_applied  = Column(Boolean, info={'hints':'Astigmatism applied to segments'}) 
    ctf_convolved = Column(Boolean, info={'hints':'CTF convoluted with segment'})
    ctf_phase_flipped = Column(Boolean, info={'hints':'CTF phase flipped on segment'})
    
    avg_defocus = Column(Float, info={'label':'average defocus (Angstrom)', 'hints':'determined by CTFFIND or CTFTILT'})
    astigmatism = Column(Float, info={'label':'astigmatism (Angstrom)', 'hints':'determined by CTFFIND or CTFTILT'})
    
    astigmation_angle = Column(Float, info={'label':'astigmatism angle (degrees)', 'hints':'determined by CTFFIND ' + \
                                            'or CTFTILT', 'min':0, 'max':360})
    
    helices = relationship('HelixTable', backref='segments')
    micrographs = relationship('CtfMicrographTable', backref='segments')
    
    
class SubunitTable(base):
    __tablename__ = 'subunits'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    segment_id = Column(Integer, ForeignKey('segments.id'))
    ref_cycle_id = Column(Integer, info={'hints':'Refinement cycle of five-orientation parameter assignment'})
    
    x_coordinate_A = Column(Float, info={'hints':'X-coordinate of subunit in Angstrom'})
    y_coordinate_A = Column(Float, info={'hints':'Y-coordinate of subunit in Angstrom'})
    phi = Column(Float, info={'hints':'Euler angle phi of subunit'})
    theta = Column(Float, info={'hints':'Euler angle theta of subunit'})
    psi = Column(Float, info={'hints':'Euler angle psi of subunit'})
    
    segments = relationship('SegmentTable', backref='subunits')
    

refine_base = declarative_base()
class RefinementCycleTable(refine_base):
    __tablename__ = 'cycles'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    iteration_id = Column(Integer, info={'hints':'Iteration cycle of refinement'})
    pixelsize = Column(Float, info={'hints':'Pixel size in Angstrom'})
    alignment_size_A = Column(Float, info={'hints':'Image size of alignment in Angstrom'})
    reconstruction_size_A = Column(Float, info={'hints':'Image size of reconstruction in Angstrom'})
    restrict_inplane = Column(Boolean, info={'hints':'Restrict in-plane rotation option'})
    delta_inplane = Column(Float, info={'hints':'Delta in-plane rotation angle 0 and 180 +/- degrees'})
    unbending = Column(Boolean, info={'hints':'Unbending option'})
    translation_step = Column(Float, info={'hints':'Translation step in pixels'})
    x_translation_range_A = Column(Float, info={'hints':'Translation range x direction in Angstrom'})
    y_translation_range_A = Column(Float, info={'hints':'Translation range y direction in Angstrom'})
    azimuthal_restraint = Column(Float, info={'hints':'Azimuthal restraint angle in degrees', 'min':0, 'max':360})
    out_of_plane_restraint = Column(Float, info={'hints':'Out-of-plane restraint angle in degrees', 'min':0, 'max':360})
    out_of_plane_min = Column(Float, info={'hints':'Minimum out-of-plane tilt in degrees'})
    out_of_plane_max = Column(Float, info={'hints':'Maximum out-of-plane tilt in degrees'})
    out_of_plane_count = Column(Integer, info={'hints':'Number of out-of-plane tilt angles'})
    azimuthal_count = Column(Integer, info={'hints':'Number of azimuthal angles'})
    helix_start = Column(Integer, info={'hints':'Helix start'})
    segment_count = Column(Integer, info={'hints':'Total segment count'})
    
    excluded_mic_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                               ' micrograph criterion'})
    
    excluded_class_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                 ' class criterion'})
    
    excluded_helix_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                 ' helix criterion'})
    
    excluded_curvature_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                     ' curvature criterion'})
    
    excluded_helix_shift_x_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                         ' shift perpendicular to helix'})
    
    excluded_prj_cc_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                  ' cross-correlation criterion'})
    
    excluded_layer_cc_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                    ' layer-line cross correlation criterion'})
    
    excluded_defocus_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                   ' defocus criterion'})
    
    excluded_astigmatism_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                       ' astigmatism criterion'})
    
    excluded_phi_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                               ' uneven phi distribution'})
    
    excluded_helix_ends_count = Column(Integer, info={'hints':SpringDataBaseCommon().get_excluded_segment_count_hint() + \
                                                      ' helix ends'})
    
    excluded_out_of_plane_tilt_count, excluded_inplane_count, total_excluded_count = \
    SpringDataBaseCommon().define_excluded_criteria()
    
    fsc = Column(PickleType, info={'hints':'Fourier shell correlation between two halves of the data.'})
    
    fsc_0143, fsc_05 = SpringDataBaseCommon().define_fsc()

    fsc_split = Column(Boolean, info={'hints':'FSC computed from independent half-sets'})
    
    amp_cc_line = Column(PickleType, info={'label':'Amplitude correlation', 'hints': 
                                           SpringDataBaseCommon().get_exp_sim_power_hint()})
        
    amp_correlation, amp_corr_quarter_nyquist, amp_corr_half_nyquist, amp_corr_3quarter_nyquist = \
    SpringDataBaseCommon().define_amplitude_correlation()
    
    variance, mean_peak, xshift_error, inplane_error, outofplane_error = \
    SpringDataBaseCommon().define_additional_criteria()
    
    helical_ccc_error, mean_helical_ccc, out_of_plane_dev = SpringDataBaseCommon().define_helical_ccc()
    
    asym_unit_count, avg_azimuth_sampling, dev_azimuth_sampling = \
    SpringDataBaseCommon().define_azimuth_angle_statitistics()
    
    
class RefinementCycleHelixTable(refine_base):
    __tablename__ = 'cycle_helices'

    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    cycle_id = Column(Integer, ForeignKey('cycles.id'))
    helix_id = Column(Integer)
    
    flip_inplane_angle = Column(Boolean, info={'hints':'Flip in-plane rotation angle with respect to previous ' + \
                                               'in-plane rotation angle'})
    
    segment_count_0_degree = Column(Integer, info={'hints':'Segment count of helix within 0 degrees of previous ' + \
                                                   'in-plane rotation angle of refinement cycle'})
    
    segment_count_180_degree = Column(Integer, info={'hints':'Segment count of helix within 180 degrees of previous ' +\
                                                     'in-plane rotation angle of refinement cycle'})
    
    
class RefinementCycleSegmentTable(refine_base):
    __tablename__ = 'cycle_segments'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    cycle_id = Column(Integer, ForeignKey('cycles.id'))
    stack_id = Column(Integer)
    local_id = Column(Integer, info={'hints':'Local stack id in temporary stack during refinement cycle'})
    rank_id = Column(Integer, info={'hints':'Local rank/CPU id of segment in mpi run during refinement cycle'})
    selected = Column(Boolean, info={'hints':'Segment selected during refinement cycle'})
    model_id = Column(Integer, info={'hints':'Model id found by competitive projection matching'})
    
    phi = Column(Float, info={'label':'phi (degree)', 'hints':'assigned Euler angle of segment', 'min':0, 'max':360})
    theta = Column(Float, info={'label':'theta (degree)', 'hints':'assigned Euler angle of segment', 'min':0, 'max':360})
    psi = Column(Float, info={'label': 'psi (degree)', 'hints':'assigned Euler angle of segment', 'min':0, 'max':360})
    
    inplane_angle = Column(Float, info={'label':'in-plane rotation angle (degrees)', 'hints':'of segment based on ' + \
                                        'projection matching', 'min':0, 'max':360})
    
    unbent_ip_angle = Column(Float, info={'label':'in-plane rotation angle for unbent helix (degrees)', 'hints':'of ' +\
                                          'segment based on projection matching', 'min':0, 'max':360})
    
    norm_inplane_angle = Column(Float, info={'label':'normalized in-plane rotation angle (degrees)', 'hints':'of ' + \
                                             'segment based on projection matching (orientation derived from picked ' +\
                                             'coordinates is zero)', 'min':0, 'max':360})
    
    unbending_angle = Column(Float, info={'hints':'Unbending angle required in addition to straightened unbending path'})
    out_of_plane_angle = Column(Float, info={'label':'out-of-plane rotation angle (degrees)', 'hints':'of segment ' + \
                                             'based on projection matching', 'min':0, 'max':360})
    
    shift_x_A = Column(Float, info={'label': 'x-shift (Angstrom)', 'hints':'of image required for transformation ' + \
                                    'and insertion of image into 3D reconstruction'})
    
    shift_y_A = Column(Float, info={'label': 'y-shift (Angstrom)', 'hints':'of image required for transformation ' + \
                                    'and insertion of image into 3D reconstruction'})
    
    unbent_shift_x_A = Column(Float, info={'label': 'x-shift for unbent helix (Angstrom)', 'hints':'of image ' + \
                                           'required for transformation and insertion of image into 3D reconstruction'})
    
    unbent_shift_y_A = Column(Float, info={'label': 'y-shift for unbent helix (Angstrom)', 'hints':'of image ' + \
                                           'required for transformation and insertion of image into 3D reconstruction'})
    
    helix_shift_x_A = Column(Float, info={'label': 'helix shift perpendicular (Angstrom)', 'hints':'of image ' + \
                                          'perpendicular to helix axis'})
    
    helix_shift_y_A = Column(Float, info={'label': 'helix shift parallel (Angstrom)', 'hints':'of image along ' + \
                                          'helix axis'})
    
    lavg_helix_shift_x_A = Column(Float, info={'label': 'local average helix shift perpendicular (Angstrom)',
                                               'hints':'of image perpendicular to helix axis'})
    
    lavg_inplane_angle = Column(Float, info={'label':'local average in-plane rotation angle (degrees)', 
                                             'hints':'of segment based on projection matching', 'min':0, 'max':360})
    
    lavg_out_of_plane = Column(Float, info={'label':'local average out-of-plane rotation angle (degrees)', 
                                            'hints':'of segment based on projection matching', 'min':0, 'max':360})
    
    forward_diff_x_shift_A = Column(Float, info={'label': 'forward difference (Angstrom)', 
                                                 'hints':'between neighboring segments'})
                                                 
    forward_diff_inplane = Column(Float, info={'label': 'forward difference inplane rotation (Degree)', 
                                                 'hints':'between neighboring segments'})
                                                 
    forward_diff_outofplane = Column(Float, info={'label': 'forward difference out-of-plane tilt (Degree)', 
                                                 'hints':'between neighboring segments'})
                                                 
    peak = Column(Float, info={'label': 'cross-correlation peak', 'hints':'of segment in refinement cycle'})
    mirror = Column(Boolean)
    
    cycles = relationship('RefinementCycleTable', backref='cycle_segments')
    
    
class RefinementCycleSegmentSubunitTable(refine_base):
    __tablename__ = 'cycle_subunits'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    ref_cycle_id = Column(Integer, ForeignKey('cycles.id'))
    ref_seg_id = Column(Integer, ForeignKey('cycle_segments.id'))
    
    stack_id = Column(Integer)
    phi = Column(Float)
    theta = Column(Float)
    psi = Column(Float)
    shift_x_A = Column(Float, info={'hints':'X-shift of image in Angstrom required for transformation and insertion ' +\
                                    'of image into 3D reconstruction'})
    
    shift_y_A = Column(Float, info={'hints':'Y-shift of image in Angstrom required for transformation and insertion ' +\
                                    'of image into 3D reconstruction'})
    
    refined_segments = relationship('RefinementCycleSegmentTable', backref='cycle_subunits')
     
    
grid_base = declarative_base()
class GridTable(grid_base):
    __tablename__ = 'grids'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    dirname = Column(String)
    primary_variable = Column(String)
    primary_min = Column(Float)
    primary_max = Column(Float)
    primary_inc = Column(Float)
    secondary_variable = Column(String)
    second_min = Column(Float)
    second_max = Column(Float)
    second_inc = Column(Float)
    completed_grid_id = Column(Integer)
    
    
class GridRefineTable(grid_base):
    __tablename__ = 'grid_refine'
    id = Column(Integer, primary_key=True) 
    datecreated = Column('datecreated', TIMESTAMP,                                  
                        server_default=text('CURRENT_TIMESTAMP'))
    datemodified = Column('datemodified', TIMESTAMP,                                 
                        onupdate=text('CURRENT_TIMESTAMP'))
    
    grid_id = Column(Integer, ForeignKey('grids.id'))
    dirname = Column(String)
    em_files_2d = Column(PickleType)
    em_files_3d = Column(PickleType)
    primary_value = Column(Float)
    secondary_value = Column(Float)
    
    fsc_0143, fsc_05 = SpringDataBaseCommon().define_fsc()
    
    variance, mean_peak, xshift_error, inplane_error, outofplane_error = \
    SpringDataBaseCommon().define_additional_criteria()
    
    excluded_out_of_plane_ratio, excluded_inplane_ratio, excluded_total_ratio = \
    SpringDataBaseCommon().define_excluded_criteria('ratio')
    
    amp_correlation, amp_corr_quarter_nyquist, amp_corr_half_nyquist, amp_corr_3quarter_nyquist = \
    SpringDataBaseCommon().define_amplitude_correlation()
    
    helical_ccc_error, mean_helical_ccc, out_of_plane_dev = SpringDataBaseCommon().define_helical_ccc()
    
    phase_residual = Column(Float, info={'label':'Phase residual', 'hints': 
                                         SpringDataBaseCommon().get_exp_sim_class_avg_hint(), 'min':-180, 'max':180})
    
    cross_correlation = Column(Float, info={'label':'Cross-correlation', 'hints': 
                                           SpringDataBaseCommon().get_exp_sim_class_avg_hint(), 'min':0, 'max':1})

    diff_noise_amp_ccc = Column(Float, info={'label':'Noise-corrected amplitude correlation', 'hints': 
                                             SpringDataBaseCommon().get_exp_sim_power_hint(), 'min':0, 'max':1})
    
    diff_noise_pr = Column(Float, info={'label':'Noise-corrected phase residual', 'hints':
                                        SpringDataBaseCommon().get_exp_sim_class_avg_hint(), 'min':-180, 'max':180})
    
    diff_noise_ccc = Column(Float, info={'label':'Noise-corrected cross-correlation', 'hints': 
                                         SpringDataBaseCommon().get_exp_sim_class_avg_hint(), 'min':0, 'max':1})
    
    noise_amp_ccc = Column(Float, info={'label':'Noise amplitude correlation', 'hints': 
                                        SpringDataBaseCommon().get_exp_sim_power_hint(), 'min':0, 'max':1})
    
    noise_pr = Column(Float, info={'label':'Noise phase residual', 'hints': 
                                   SpringDataBaseCommon().get_exp_sim_class_avg_hint(), 'min':-180, 'max':180})
    
    noise_ccc = Column(Float, info={'label':'Noise cross-correlation', 'hints': 
                                    SpringDataBaseCommon().get_exp_sim_class_avg_hint(), 'min':0, 'max':1})
    
    asym_unit_count, avg_azimuth_sampling, dev_azimuth_sampling = \
    SpringDataBaseCommon().define_azimuth_angle_statitistics()
    
    grid = relationship('GridTable', backref='grid_refine')
    

class SpringDataBaseSetup(object):
    def setup_sqlite_db(self, base, db_name='spring.db'):
        
        engine = create_engine('sqlite:///{0}'.format(db_name), echo=False)
        base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        return session
    
    
class SpringDataBaseAssist(SpringDataBaseSetup):
    def remove_all_previous_entries(self, session, column_name):
#        if session.query(column_name).count > 0:
        column = session.query(column_name).all()
        for each_item in column:
            session.delete(each_item)
        
        return session
    

    def get_columns_from_table(self, table):
        hel_columns = list(table.__table__.columns.keys())

        return hel_columns


    def get_data_from_entry(self, columns, each_entry):
        data = OrderedDict([(str(column), getattr(each_entry, column)) for column in columns if hasattr(each_entry, column)])
        
        return data


    def get_data_as_dict_and_add_to_target_session(self, table, target_session, all_entries_from_table, columns,
    merge_ids):
        for each_entry in all_entries_from_table:
            data = self.get_data_from_entry(columns, each_entry)
            if merge_ids:
                data.__delitem__('id')
            target_session.add(table(**data))

        return target_session


    def copy_search_result_to_another_database(self, table, target_session, all_entries_from_table,
    merge_ids=False):
        columns = self.get_columns_from_table(table)

        target_session = self.get_data_as_dict_and_add_to_target_session(table, target_session, all_entries_from_table,
        columns, merge_ids)
            
        return target_session


    def copy_all_table_data_from_one_session_to_another_session(self, table, target_session, source_session,
    merge_ids=False):
        all_entries_from_table = source_session.query(table).order_by(table.id).all()

        target_session = self.copy_search_result_to_another_database(table, target_session,
        all_entries_from_table, merge_ids)
        
        target_session.commit()
        
        return target_session


    def transfer_records_from_table(self, auto_table, target_table, auto_session, target_session):
        table_entries = auto_session.query(auto_table).all()
        columns = list(target_table.__table__.columns.keys())
        
        target_session = self.get_data_as_dict_and_add_to_target_session(target_table, target_session, table_entries,
        columns, merge_ids=False)

        print '{0} data was transferred and updated.'.format(target_table.__name__)

        return target_session


class SpringDataBaseInfo(SpringDataBaseAssist):

    def get_dictionary_of_labels_from_table(self, table):
        columns = [each_column.name for each_column in table.__table__.columns]
        labels = [each_column.info.get('label') for each_column in table.__table__.columns]
        segment_labels = dict(zip(columns, labels))
        
        return columns, segment_labels
    
    
    def get_dictionary_of_labels_and_hints(self, table):
        columns, segment_labels = self.get_dictionary_of_labels_from_table(table)
        hints = [each_column.info.get('hints') for each_column in table.__table__.columns]
        segment_hints = dict(zip(columns, hints))
        
        return segment_labels, segment_hints
    

    def construct_distance_hint(self, each_arg, hint_str, quantity, table_labels, table_hints, y_segment_key,
    distance_labels, distance_hints):
        if each_arg == quantity:
            distance_label = distance_labels['distance_from_start_A']
            distance_hint = distance_hints['distance_from_start_A']
            x_label = distance_label.title()
            y_label = table_labels[y_segment_key].title()
            x_hint = '{0} {1}'.format(distance_label.title(), distance_hint)
            y_hint = '{0} {1}'.format(table_labels[y_segment_key].title(), table_hints[y_segment_key])
            hint_str += '\'{0}\': {1} vs. {2} ({3}, {4})\n'.format(quantity, x_label, y_label, x_hint, y_hint)
            
        return hint_str
    
    
    def get_hints_from_grid_table(self, quanitities):
        labels, hints = self.get_dictionary_of_labels_and_hints(GridRefineTable)
        hint_str = 'Grid parameters to be analyzed:\n'
        for each_quant in quanitities:
            hint_str +='{0}: {1}\n'.format(labels[each_quant], hints[each_quant])
        
        return hint_str
    
    
    def get_hints_from_refinement_cycle(self, quanitities):
        labels, hints = self.get_dictionary_of_labels_and_hints(RefinementCycleTable)
        hint_str = 'Refinement criteria of refinement to be plotted: '
        for each_quant in quanitities:
            hint_str +='\'{0}\': {1} - {2}\n'.format(each_quant, labels[each_quant], hints[each_quant])
        
        return hint_str
    
                
    def get_hints_from_segment_table(self, quantities):
        segment_labels, segment_hints = self.get_dictionary_of_labels_and_hints(SegmentTable)
        
        quantity_column_pairs = [['in-plane_rotation', 'inplane_angle'], 
                                ['curvature', 'curvature'],
                                ['defocus', 'avg_defocus'],
                                ['astigmatism', 'astigmatism'], 
                                ['layer-line correlation', 'ccc_layer'], 
                                ['classes', 'class_id']]
            
        hint_str = 'Quantities to be plotted: '
        for each_quantity in quantities:
            if each_quantity == 'coordinates':
                hint_str += '\'coordinates\': {0} vs. {1}; {2} vs. {3}\n'.\
                format(segment_labels['x_coordinate_A'].title(), segment_labels['y_coordinate_A'].title(),
                segment_labels['picked_x_coordinate_A'].title(), segment_labels['picked_y_coordinate_A'].title())
                
            hint_str = self.construct_hints_based_on_quantity_column_pairs(segment_labels, segment_hints,
            segment_labels, segment_hints, quantity_column_pairs, hint_str, each_quantity)
                
        return hint_str
    
    

    def construct_hints_based_on_quantity_column_pairs(self, segment_labels, segment_hints, ref_segment_labels,
    ref_segment_hints, quantity_column_pairs, hint_str, each_quantity):
        for each_quantity_str, each_column in quantity_column_pairs:
            hint_str = self.construct_distance_hint(each_quantity, hint_str, each_quantity_str, ref_segment_labels,
            ref_segment_hints, each_column, segment_labels, segment_hints)
        
        return hint_str

    def get_hints_from_ref_segment_table(self, quantities):
        segment_labels, segment_hints = self.get_dictionary_of_labels_and_hints(SegmentTable)
        ref_segment_labels, ref_segment_hints = self.get_dictionary_of_labels_and_hints(RefinementCycleSegmentTable)
        
        quantity_column_pairs = [['in-plane_rotation', 'inplane_angle'],
                                ['normalized_in-plane_rotation', 'norm_inplane_angle'],
                                ['phi', 'phi'],
                                ['theta', 'theta'],
                                ['psi', 'psi'],
                                ['x_shift', 'shift_x_A'],
                                ['y_shift', 'shift_y_A'],
                                ['shift_perpendicular_to_helix', 'helix_shift_x_A'], 
                                ['shift_along_helix', 'helix_shift_y_A']]
        
        hint_str = 'Refinement quantities to be plotted: '
        for each_quantity in quantities:
            if each_quantity == 'coordinates':
                hint_str += '\'coordinates\': Refined {0} vs. Refined {1}; Picked {0} vs. Picked {0}\n'.\
                format(segment_labels['x_coordinate_A'].title(), segment_labels['y_coordinate_A'].title())
            if each_quantity == 'coordinates_subunit':
                hint_str += '\'coordinates_subunit\': ' 
                hint_str += 'Refined Subunit {0} vs. Refined Subunit {1}; Picked {0} vs. Picked {0}\n'.\
                format(segment_labels['x_coordinate_A'].title(), segment_labels['y_coordinate_A'].title())
                
            hint_str = self.construct_hints_based_on_quantity_column_pairs(segment_labels, segment_hints,
            ref_segment_labels, ref_segment_hints, quantity_column_pairs, hint_str, each_quantity)
            
        return hint_str
    
    
    def get_labels_from_table(self, table, *args):
        """
        >>> from spring.csinfrastr.csdatabase import SpringDataBase
        >>> s = SpringDataBase()
        >>> s.get_labels_from_table(SegmentTable, 'x_coordinate_A', 'y_coordinate_A') 
        ['X-Coordinate (Angstrom)', 'Y-Coordinate (Angstrom)']
        >>> s.get_labels_from_table(RefinementCycleSegmentTable, 'shift_x_A', \
'shift_y_A', 'phi') 
        ['X-Shift (Angstrom)', 'Y-Shift (Angstrom)', 'Phi (Degree)']
        >>> s.get_labels_from_table(RefinementCycleSegmentTable, 'inplane_angle', \
'lavg_inplane_angle')
        ['In-Plane Rotation Angle (Degrees)', 'Local Average In-Plane Rotation Angle (Degrees)']
        """
        columns, segment_labels = self.get_dictionary_of_labels_from_table(table)
        
        labels = [segment_labels[each_arg].title() for each_arg in args]
        
        return labels


class SpringDataBase(SpringDataBaseInfo):
    
    def autoload_tables_into_session(self, db_path, tables, autoclasses):
        engine = create_engine('sqlite:///{0}'.format(db_path), echo=False)
     
        for each_table, each_class in zip(tables, autoclasses):
            metadata = MetaData(engine)
            moz_bookmarks = Table(each_table, metadata, autoload=True)
            mapper(each_class, moz_bookmarks)
     
        Session = sessionmaker(bind=engine)
        session = Session()

        return session
