# -*- coding: utf-8 -*-
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

_bibtexStr = """

@article{Desfosses2014,
title = "SPRING – An image processing package for single-particle based helical reconstruction from electron cryomicrographs",
journal = "JSB",
volume = "185",
number = "1",
pages = "15 - 26",
year = "2014",
note = "",
issn = "1047-8477",
doi = "http://dx.doi.org/10.1016/j.jsb.2013.11.003",
url = "http://www.sciencedirect.com/science/article/pii/S104784771300302X",
author = "Ambroise Desfosses and Rodolfo Ciuffa and Irina Gutsche and Carsten Sachse",
keywords = "Helical assembly",
keywords = "Electron cryomicroscopy",
keywords = "Software",
keywords = "Image processing",
keywords = "3D reconstruction",
keywords = "Helical symmetry",
abstract = "Helical reconstruction from electron cryomicrographs has become a routine technique for macromolecular structure determination of helical assemblies since the first days of Fourier-based three-dimensional image reconstruction. In the past decade, the single-particle technique has had an important impact on the advancement of helical reconstruction. Here, we present the software package SPRING that combines Fourier based symmetry analysis and real-space helical processing into a single workflow. One of the most time-consuming steps in helical reconstruction is the determination of the initial symmetry parameters. First, we propose a class-based helical reconstruction approach that enables the simultaneous exploration and evaluation of many symmetry combinations at low resolution. Second, multiple symmetry solutions can be further assessed and refined by single-particle based helical reconstruction using the correlation of simulated and experimental power spectra. Finally, the 3D structure can be determined to high resolution. In order to validate the procedure, we use the reference specimen Tobacco Mosaic Virus (TMV). After refinement of the helical symmetry, a total of 50,000 asymmetric units from two micrographs are sufficient to reconstruct a subnanometer 3D structure of TMV at 6.4Å resolution. Furthermore, we introduce the individual programs of the software and discuss enhancements of the helical reconstruction workflow. Thanks to its user-friendly interface and documentation, SPRING can be utilized by the novice as well as the expert user. In addition to the study of well-ordered helical structures, the development of a streamlined workflow for single-particle based helical reconstruction opens new possibilities to analyze specimens that are heterogeneous in symmetries."
}

"""

from pyworkflow.utils import parseBibTex

_bibtex = parseBibTex(_bibtexStr)  
