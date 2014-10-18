#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
#                Laura del Cano         (ldelcano@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
import os, sys

import pyworkflow as pw
from tests import *
from pyworkflow.utils.path import makeFilePath
import model

try:
    from unittest.runner import _WritelnDecorator # Python 2.7+
except ImportError:
    from unittest import _WritelnDecorator # Python <2.6

    
DataSet(name='xmipp_tutorial', folder='xmipp_tutorial', 
        files={
               'aligned_particles': 'gold/aligned_particles.sqlite',
               'allMics': 'micrographs/*.mrc',
               'boxingDir': 'pickingEman',
               'boxingFile': 'pickingEman/info/BPV_1386_info.json',
               'coordsGoldSqlite': 'gold/coordinates_gold.sqlite',
               'ctfGold': 'gold/xmipp_ctf.ctfparam',
               'images10': 'gold/images10.xmd',
               'mic1': 'micrographs/BPV_1386.mrc',
               'mic2': 'micrographs/BPV_1387.mrc',
               'mic3': 'micrographs/BPV_1388.mrc',
               'micsGoldSqlite': 'gold/micrographs_gold.sqlite',
               'micsGoldSqlite2': 'gold/micrographs2_gold.sqlite',
               'micsGoldXmd': 'gold/micrographs_gold.xmd',
               'micsSqlite': 'micrographs/micrographs.sqlite',
               'particles': 'particles/*.hdf',
               'particles1': 'particles/BPV_1386_ptcls.hdf',
               'posAllDir': 'pickingXmipp/pickedAll',
               'posSupervisedDir': 'pickingXmipp/pickedSupervised',
               'rctCoords': 'rct/pickingXmipp',
               'rctMicsT': 'rct/micrographs/*T.mrc',
               'rctMicsU': 'rct/micrographs/*U.mrc',
               'vol1': 'volumes/BPV_scale_filtered_windowed_64.vol',
               'vol2': 'volumes/volume_1_iter_002.mrc',
               'vol3': 'volumes/volume_1_iter_002.mrc',
               'volumes': 'volumes/*.mrc',
               })


DataSet(name='mda', folder='hemoglobin_mda', 
        files={
               'particles': 'particles/*.spi',
               'volumes': 'volumes/*.spi'})


DataSet(name='tomo', folder='xmipp_tomo_test', 
        files={
               'vol1': 'volumes/subvols_6E6.001.mrc.spi',
               'vol2': 'volumes/subvols_6E6.002.mrc.spi',
               'vol3': 'volumes/subvols_6E6.003.mrc.spi',
               'volumes': 'volumes/*.spi',
        })


DataSet(name='relion_tutorial', folder='relion_tutorial', 
        files={
               'allMics': 'micrographs/*.mrc',
               'boxingDir': 'pickingEman',
               'input_particles': 'gold/input_particles.star',
               'particles': 'gold/particles.sqlite',
               'posAllDir': 'pickingXmipp',
               'relion_it020_data': 'gold/relion_it020_data.star',
               'volume': 'volumes/reference.mrc',
               'import1_data_star': 'import/case1/classify3d_small_it038_data.star',
               'import2_data_star': 'import/case2/relion_it015_data.star',
        })


DataSet(name='ribo_movies', folder='ribo_movies', 
        files={
               'movies': 'movies/1??_*.mrcs',
               'posAllDir': 'pickingXmipp',
        })


DataSet(name='model',  folder='model',
        files={
               'classesSelection': 'gold/classes_selection.sqlite',
               'modelGoldSqlite': 'gold/model_gold.sqlite',
               'modelGoldXml': 'gold/model_gold.xml',
        })

DataSet(name='rct',  folder='rct', 
        files={
               'classes': 'classes/classes2D_stable_core.sqlite',
               'positions': 'positions',
               'tilted': 'micrographs/F_rct_t*.tif',
               'untilted': 'micrographs/F_rct_u*.tif',
        })

DataSet(name='emx',  folder='emx', 
        files={
               'alignShiftOnly': 'alignment/align_shift_only.mrcs',
               'alignRotOnly': 'alignment/align_rot_only.mrcs',
               'alignShiftRot': 'alignment/align_shift_rot.mrcs',
               'alignRotShift': 'alignment/align_rot_shift.mrcs',
               'alignRotOnly3D': 'alignment/align_rot_only_3d.mrcs',
               'coordinatesGoldT1': 'coordinates/Test1/coordinates_gold.sqlite',
               'coordinatesT1': 'coordinates/Test1/coordinates.emx',
               'defocusParticleT2': 'defocusParticle/particles.emx',
               'emxMicrographCtf1':'MicrographsCTF/ctfindCTFEstimation.emx',
               'emxMicrographCtf1Gold':'MicrographsCTF/ctfindCTFEstimation.sqlite',
               'micrographsGoldT2': 'defocusParticle/micrographs_gold.sqlite',
               'particlesGoldT2': 'defocusParticle/particles_gold.sqlite',
              })
               
               
DataSet(name='CTFDiscrepancy',  folder='CTFDiscrepancy',
        files={
               'emxMicrographCtf1':'ctfindCTFEstimation.emx',
               'emxMicrographCtf2':'xmipp3CTFEstimation.emx',
               'emxMicrographCtf3':'xmipp3CTFEstimation2.emx',
               'ctfsGold':'ctfs.sqlite',
              })

DataSet(name='movies',  folder='movies',
        files={'movie1':'Falcon_2012_06_12-14_33_35_0_movie.mrcs',
               'movie2':'Falcon_2012_06_12-16_55_40_0_movie.mrcs',
               'movie3':'Falcon_2012_06_12-17_26_54_0_movie.mrcs',
                })             
               
               
