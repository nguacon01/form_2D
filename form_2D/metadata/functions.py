import os, json, glob,calendar
import numpy as np
from dateutil.relativedelta import *
from scipy.constants import N_A as Avogadro
from scipy.constants import e as electron
import shutil as sh
import spike
from spike.File import Solarix, Apex
from datetime import datetime
from dateutil.parser import parse
from pathlib import Path
from sys import platform as _platform

def clear(direc):
    if os.path.exists(direc):
        print("Clearing directory:",direc)
        sh.rmtree(direc)

def brucker_read(param_file):
    """
    reads a *.d Bruker FTICR dataset and generate a dictionary
    """
    print("*** Generating base dico ***")
    # read all params
    print("*** Param file is:",param_file,"***")

    params = Apex.read_param(str(param_file))
    # determine file type
    with open(param_file) as param_read:
            lines = param_read.readlines()
    #print(lines)
    spectrometer_type = "Apex"
    for l in lines:
        if "solari" in l:
            spectrometer_type = "Solarix"

    # build meta data
    reduced_params = {}
    reduced_params['MetaFileType'] = "EUFTICRMS v 1.0"
    reduced_params['MetaFileVersion'] = "1.0.0"
    reduced_params['MetaFileCreationDate'] = datetime.now().isoformat()

    reduced_params['FileName'] = str(Path(param_file).parent.parent.parent).split('/')[-1]
    reduced_params['SpectrometerType'] = spectrometer_type
    acquisition_date = parse(params['CLDATE'])
    reduced_params['AcqDate'] = acquisition_date.strftime('%Y-%m-%d')
    reduced_params['EndEmbargo'] = (acquisition_date + relativedelta(months=18)).strftime('%Y-%m-%d')

    reduced_params['ExcHighMass'] = params['EXC_hi']
    reduced_params['ExcLowMass'] = params['EXC_low']
    reduced_params['SpectralWidth'] = params['SW_h']
    reduced_params['AcqSize'] =  params['TD']
    reduced_params['CalibrationA'] = params['ML1']
    reduced_params['CalibrationB'] = params['ML2']
    reduced_params['CalibrationC'] = params['ML3']
    reduced_params['PulseProgam'] = params['PULPROG']
    reduced_params['MagneticB0'] = str(round(float(params['ML1'])*2*np.pi/(electron*Avogadro)*1E-3,1))

    if spectrometer_type == "Solarix":
        excfile = Path(param_file).parent/"ExciteSweep"
        print(excfile)
        if excfile.exists():
            with open(excfile,'r') as excfile_read: 
                lines = excfile_read.readlines()
            NB_step = len(lines[6:])
            reduced_params['ExcNumberSteps'] = str(NB_step)
            reduced_params['ExcSweepFirst'] = str(lines[6]).strip('\n')
            reduced_params['ExcSweepLast'] = str(lines[len(lines)-1]).strip('\n')
        else:
            reduced_params['ExcNumberSteps'] = "NotDetermined"
            reduced_params['ExcSweepFirst'] = "NotDetermined"
            reduced_params['ExcSweepLast'] = "NotDetermined"
    print("Loaded parameters are:", reduced_params)
    return reduced_params

def generate_reduced_params(param_file, param_file_type):
    reduced_params={}
    print("*** Generating reduced params ***")
    if param_file and param_file_type == "brukermethod_file":
        print('address paramfile is ', param_file)
        reduced_params = brucker_read(param_file)
    elif param_file and param_file_type == "meta_file":
        with open(param_file) as f:
            reduced_params = json.load(f)
            reduced_params['MetaFileEditionDate'] = datetime.now().isoformat()
    else:
        print("PARAM_FILE NONE, using reduced_params.")
    return reduced_params

