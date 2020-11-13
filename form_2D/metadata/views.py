from flask import Blueprint, render_template, request, redirect, url_for, jsonify,send_from_directory
from flask.helpers import make_response
from flask_login import login_required, current_user
from numpy.core.fromnumeric import size
import os
from sys import platform as _platform
from .forms import ConfigForm
# from spike import processing as proc_spike
from spike.NPKConfigParser import NPKConfigParser
from spike.FTICR import FTICRData
from spike.File import Solarix
from datetime import datetime
from form_2D.libs.EUFT_Spike import processing_4EU as proc_spike
from form_2D.libs.EUFT_Spike.Tools import FTICR_INTER as FI_tools

metadata = Blueprint(
    "metadata",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@metadata.route('/')
@metadata.route('/index')
@metadata.route('/home')
def index():
    return redirect(url_for('metadata.create_metadata'))
######################## PROCESSING CONFIGURATION ##############################################
def user_SeaDrive_path():

    username = current_user.username
    
    user_path = os.path.join('/home',username)
    if not os.path.exists(user_path):
        os.makedirs(user_path, mode = 0o777)
    # change cwd path
    os.chdir(user_path)
    user_seaDrive_path = os.path.join(os.getcwd(),"FTICR_DATA")
    return user_seaDrive_path
    
@metadata.route('/select_project', methods=["POST","GET"])
@login_required
def select_project():
    # user_identity = get_jwt_identity()
    try:
        user_SeaDrive = user_SeaDrive_path()
        # check if user has Seafile folder or not
        if not os.path.isdir(user_SeaDrive):
            return render_template("errors/404.html", message="You don't have Seafile folder or Seafile folder not found")

        obj_ser_paths = FI_tools.build_list(base=user_SeaDrive, accept=('ser'))
        # check if in Seafile folder has ser files or not
        if not obj_ser_paths:
            return render_template("errors/404.html", message="You don't have any ser file")
        project_json = {}
        for obj in obj_ser_paths:
            if isinstance(obj, tuple):
                fullpath = str(obj.fullpath)
                shortpath = str(obj.spath)
                
                _, projet_folder_name = os.path.split(fullpath)
                files = os.scandir(fullpath)
                conf_list = {}
                for conf_file in files:
                    if os.path.isfile(conf_file.path) and conf_file.path.endswith(".mscf"):
                        conf_list[conf_file.name] = conf_file.path
                
                project_json[projet_folder_name] = {"name":projet_folder_name, "shortpath":shortpath, "mscfpaths":conf_list}

        return render_template("metadata/select_project.html", data = project_json)
    except:
        return render_template("errors/404.html", message="You don't have Seafile folder or Seafile folder not found")

@metadata.route("/config", methods = ["POST", "GET"])
@login_required
def config():
    """
    author: DMD - casc4de
    This function help us to modify an existed config file - mscf or also creates a new one.
    """
    # get variable project short path: project_spath
    project_spath = request.args.get('project_spath')
    # get variable config file name
    config_filename = request.args.get('config_filename')

    # create experiment config form
    form = ConfigForm()
    
    # file_name = project_name + '.mscf'
    # define the root path of all .d projects
    projects_root_folder_path = user_SeaDrive_path()
    
    # define config file path
    config_file_path = os.path.join(projects_root_folder_path, project_spath, config_filename)

    # define the chosen project path
    project_full_path = os.path.join(projects_root_folder_path, project_spath)

    #####Information about the chosen project######
    project_dict = {}

    _, project_name = os.path.split(project_spath)

    project_dict['name'] = project_name
    # create object
    FTICR_Data = FTICRData(dim=2)
    ser_file_path = os.path.join(project_full_path,"ser")
    ser_file_date_aquisition = os.path.getmtime(ser_file_path)
    project_dict["ser_date_aquisition"] = datetime.fromtimestamp(ser_file_date_aquisition)

    # find method file
    param_filename = Solarix.locate_acquisition(project_full_path)
    params_method_file = Solarix.read_param(param_filename)

    # find Bo
    FTICR_Data.axis1.calibA = float(params_method_file["ML1"])
    FTICR_Data.axis2.calibA = float(params_method_file["ML1"])
    project_dict["Bo"] = round(FTICR_Data.Bo,2)

    # Import parameters : size in F1 and F2    
    sizeF1 = Solarix.read_scan(os.path.join(project_full_path,"scan.xml"))
    sizeF2 = int(params_method_file["TD"])
    project_dict["sizeF1"] = sizeF1//1024
    project_dict["sizeF2"] = sizeF2//1024
    project_dict["data_size"] = 4*sizeF1*sizeF2//(1024*1024) 
    
    # determine excitation window
    try:  #CR for compatibility with Apex format as there is no EXciteSweep file
        fl,fh = Solarix.read_ExciteSweep(Solarix.locate_ExciteSweep(project_full_path))
        freql, freqh = fl[0], fh[0]
    except:
        freqh = float(params_method_file["EXC_hi"])
        freql = float(params_method_file["EXC_low"])
    mzl = round(FTICR_Data.axis2.htomz(freql), 2)
    mzh = round(FTICR_Data.axis2.htomz(freqh), 2)

    project_dict["freqh"] = freqh
    project_dict["freql"] = freql
    project_dict["mzh"] = mzh
    project_dict["mzl"] = mzl

    # show f2_specwidth
    f2_specwidth = float(params_method_file["SW_h"])
    lowmass = FTICR_Data.axis2.htomz(f2_specwidth)
    project_dict["f2_specwidth"] = f2_specwidth
    project_dict["lowmass"] = round(lowmass,2)
    #####END Information about the chosen project######
    

    # default config file
    default_conf_file = os.path.join(metadata.root_path, "static", "files", "process2D.default.mscf")

    default_config = NPKConfigParser()
    default_config.readfp(open(default_conf_file,'r'))

    # ['import', 'processing', 'peak_picking']
    default_sections = default_config.sections()

    # set f1_specwidth default value
    # determine f1_specwidth
    f1 =  float(params_method_file["IN_26"])    # IN_26 is used in 2D sequence as incremental time
    if f1 < 1E-3 and f1>0.0:   # seems legit
        f1_specwidth = round(1.0/(2*f1),2)
    else:
        f1_specwidth = None
    project_dict["f1_specwidth"] = f1_specwidth

    # create processing params object base on Proc_Parameters() object in spike lib
    proc_params = proc_spike.Proc_Parameters()

    # check if the mscf config file is existed or not. If not, create new file with default values
    if os.path.isfile(config_file_path):
        config = NPKConfigParser()
        try:
            config.readfp(open(config_file_path, 'r'))
        except Exception:
            return render_template("errors/404.html", message="There are some attributes which are duplicated. Check again.")
        # load config data into proc_params object
        proc_params.load(config)
        # convert proc_params to dictionary
        config_dict = proc_params.__dict__
        # highmass and F1_specwidth are not in Proc_Parameters object so add them in config_dict manually.
        config_dict['highmass'] = config['import']['highmass']
        # set config_dict['F1_specwidth'] = F1_specwidth in the the existed config file
        config_dict['F1_specwidth'] = config['import']['F1_specwidth']
        config_dict['sizemultipliers'] = config['processing']['sizemultipliers']
        # return config_dict
    else:
        proc_params.load(default_config)
        # convert proc_params to dictionary
        config_dict = proc_params.__dict__
        # set config_dict['F1_specwidth'] = F1_specwidth from the estimate of project data
        config_dict['F1_specwidth'] = f1_specwidth
        config_dict['sizemultipliers'] = default_config['processing']['sizemultipliers']
    
    # return config_dict['sizemultipliers']

    # return config_dict
    if request.method == "GET":

        # Set value for select forms
        form.compress_outfile.data = str(config_dict["compress_outfile"])
        form.do_sane.data = str(config_dict.get("do_sane", "False"))
        form.format.data = str(config_dict.get("format", "solarix"))
        form.samplingfile.data = str(config_dict.get("samplingfile"))
        # by default, N.U.S field is False
        form.nus.data = str(False)
        form.save_file.data = str(config_filename.split(".")[0])
        
    if form.validate_on_submit():
        
        # get form data
        data = request.form.to_dict()
        # fill up config_dict with data from form
        
        for key, val in data.items():
            config_dict[key] = val

        config_dict["format"] = data["format"].capitalize()

        # defind output file
        save_file_name = data['save_file'].split('.')[0] + ".mscf"

        ### SET DEFAULT VALUES FOR OUTPUT CONFIG FILE###
        # do_F2 = True
        config_dict['do_F2'] =True
        # do_F1 = True
        config_dict['do_F1'] =True
        # do_f1demodu = True
        config_dict['do_f1demodu'] =True
        # do_modulus = True
        config_dict['do_modulus'] =True
        # do_rem_ridge = True
        config_dict['do_rem_ridge'] =True
        # urqrd_rank = 30
        config_dict['urqrd_rank'] =30
        # urqrd_iterations = 1
        config_dict['urqrd_iterations']= 1

        config_dict['tempdir'] = "/tmp/processing/"
        config_dict['infile'] = "ser.msh5"
        config_dict['outfile'] = "{project_name}/{config_filename}_mr.msh5".format(
            project_name = project_name,
            config_filename = save_file_name.split(".")[0]
        )

        #NUS - Non Uniform Sampled
        if data["nus"] == False:
            config_dict["do_pgsane"] = False
        else:
            config_dict["do_pgsane"] = True

        # create a new config file
        save_file_path = os.path.join(project_full_path, save_file_name)
        # return project_full_path
        with open(save_file_path, "w") as save:
            # write header of config file
            save.write(
                "#Project folder: {} \n".format(project_dict['name']) +
                "#Date of acquisition: {} \n".format(project_dict['ser_date_aquisition']) +
                "#Estimate Bo from internal calibration: {}T \n".format(project_dict['Bo']) +
                "#Experiment size (F1 x F2): {}k x {}k \n".format(project_dict['sizeF1'], project_dict['sizeF2']) +
                "#Data size: {}MB \n".format(project_dict['data_size']) +
                "#Excitation pulses from {}Hz (m/z={}) to {}Hz (m/z={}) \n".format(project_dict['freqh'], project_dict['mzh'], project_dict['freql'], project_dict['mzl']) +
                "#Acquisition spectral width: {}Hz (low mass: {}) \n".format(project_dict['f2_specwidth'], project_dict['lowmass']) 
            )
            for section in default_sections:
                # config_key and its value which are got from submited form
                for config_key, val in config_dict.items():
                    try: 
                        # if config section match with sections in default config file, then change value in default file
                        if default_config.get(section, config_key):
                            default_config.set(section, config_key, val)
                    except Exception:
                        pass
            
            # save the new config file
            default_config.write(save)
        # allow user to download it
        return send_from_directory(directory=project_full_path, filename=save_file_name, as_attachment=True)

    # return config_dict
    return render_template(
        "metadata/config_2.html",
        config_dict = config_dict,
        form = form, errors = form.errors,
        project_spath = project_spath,
        config_filename = config_filename,
        project_dict = project_dict
    )

@metadata.route("/comp_sizes", methods=["GET", "POST"])
def comp_sizes():

    if request.method == 'POST':
        return make_response('method must be GET', 400)

    post_data = request.get_json()
    sizeF1 = int(post_data.get("sizeF1"))
    sizeF2 = int(post_data.get("sizeF2"))
    m1 = float(post_data.get("m1"))
    m2 = float(post_data.get("m2"))
    if not sizeF1 or not sizeF2 or not m1 or not m2:
        return make_response(jsonify({"msg":"Make sure you filled up sizemultipliers field", "status":"fail"}), 400)
    
    dd = FTICRData(dim=2)
    dd.axis1.size = sizeF1
    dd.axis2.size = sizeF2
    szmul = [m1, m2]

    allsizes = proc_spike.comp_sizes(d0=dd, szmlist=szmul)
    sizes = allsizes[0]
    somme = 0
    for a, b in allsizes:
        somme += a*b
    return make_response(jsonify({
        "msg":"Success", 
        "status":"success", 
        "spec_size":{"sizeF1":sizes[0], "sizeF2":sizes[1]}, 
        "uncompressed_size":str(somme//1024//1024*8)}), 
        201
    )


