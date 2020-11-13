from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify,send_from_directory, session
from flask.helpers import make_response
from flask_login import login_required, current_user
from flask_session import Session
from numpy.core.fromnumeric import size
import os
import requests
from .forms import ConfigForm
# from spike import processing as proc_spike
from spike.NPKConfigParser import NPKConfigParser
from spike.FTICR import FTICRData
from spike.File import Solarix
from datetime import datetime
from form_2D.libs.EUFT_Spike import processing_4EU as proc_spike
from form_2D.libs.EUFT_Spike.Tools import FTICR_INTER as FI_tools

from form_2D.libs import custom_seafileapi
from form_2D.libs.custom_seafileapi.files import SeafDir
from form_2D.libs.custom_seafileapi.utils import seafile_token_require
import json
from form_2D.metadata.views import metadata
from datetime import datetime
import glob

server = "https://cloud.seafile.com"

seafile_client = Blueprint(
    "seafile_client",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@seafile_client.route('/')
@seafile_client.route('/index')
@seafile_token_require
def index():
    return render_template('seafile_client/index.html', message='this is a page of seafile api', current_user=session['current_user'])

@seafile_client.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        _password = request.form.get('password')
        request_token_url = server+"/api2/auth-token/"

        _data = {
            "username" : email,
            "password" : _password
        }
        _headers = {
            "Accept-Encoding":"gzip",
            "Accept-Language":"fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        response = requests.post(
            url=request_token_url,
            data=_data,
            headers=_headers
        )
        if response.status_code == 200:
            content = json.loads(response.text)
            session["seafile_token"] = content['token']
            session["current_user"] = email
            return redirect(url_for('seafile_client.index', current_user = session["current_user"]))
        else:
            flash(message="Login Fail", category="error")
    return render_template('seafile_client/login.html')


@seafile_client.route('/list_repositories')
@seafile_token_require
def list_repositories():
    server = "https://cloud.seafile.com"
    client = custom_seafileapi.connect(server, token=session['seafile_token'])
    list_repos = client.repos.list_repos()
    if len(list_repos) < 1:
        return "You dont have any repository"
    return render_template('seafile_client/list_repositories.html', data=list_repos)

@seafile_client.route('/repo_items')
@seafile_token_require
def repo_items():
    repo_id = request.args.get('repo_id')
    repo_name = request.args.get('repo_name')
    server = "https://cloud.seafile.com"
    client = custom_seafileapi.connect(server, token=session['seafile_token'])
    repo = client.repos.get_repo(repo_id)

    #return array of SeafDir objects
    items = repo.get_items(recursive=0, type='d')

    return render_template('seafile_client/repo_items.html', data=items, repo_name=repo_name)


@seafile_client.route('/dir_items')
def dir_items():
    repo_id = request.args.get('repo_id')
    oid = request.args.get('oid')
    dir_name = request.args.get('dir_name')
    parent_dir = request.args.get('parent_dir')
    client = custom_seafileapi.connect(server, token=session['seafile_token'])
    repo = client.repos.get_repo(repo_id)
    dir = SeafDir(repo, oid, dir_name, 'dir', parent_dir)
    dir.load_entries(type='f')
    data = []
    for item in dir.entries:
        if item.name.endswith('mscf'):
            parent_dir = item.parent_dir
            upstream_parent_dir = '/' + parent_dir.split('/')[1]
            if upstream_parent_dir == '/'+ dir_name:
                data.append(item)
    return render_template('seafile_client/dir_items.html', data=data, dir_name=dir_name, repo_id=repo_id)

def download_mscf_file(repo_id, file_full_path, parent_dir):
    tmp_folder_path = os.path.join(seafile_client.root_path, 'static/tmp', current_user.username, parent_dir.split('/')[1])

    if file_full_path == '':
        tmp_file_path = os.path.join(tmp_folder_path, 'new.mscf')
        default_conf_file = os.path.join(metadata.root_path, "static", "files", "process2D.default.mscf")
        with open(tmp_file_path, "w") as f:
            with open(default_conf_file,'r') as data:
                f.write(data.read())
    else:
        client = custom_seafileapi.connect(server, token=session['seafile_token'])
        repo = client.repos.get_repo(repo_id)
        if not os.path.exists(tmp_folder_path):
            os.makedirs(tmp_folder_path)

        file = repo.get_file(file_full_path, parent_dir)
        download_file_link = file._get_download_link()
        
        file_name = file.name
        tmp_file_path = os.path.join(tmp_folder_path, file_name)
        file_content = requests.get(url=download_file_link, stream=True)
        with open(tmp_file_path, "wb") as f:
            for chunk in file_content.iter_lines():
                f.write(chunk)
                f.write(("\n").encode())
    return tmp_file_path

def load_method_file(repo_id, parent_dir):
    tmp_folder_path = os.path.join(seafile_client.root_path, 'static/tmp', current_user.username, parent_dir.split('/')[1])
    if not os.path.exists(tmp_folder_path):
        os.makedirs(tmp_folder_path)

    L = glob.glob(os.path.join(tmp_folder_path,"*",".method"))
    if len(L) > 1:
        raise Exception( "You have more than 1 apexAcquisition.method file in the %s folder, using the first one"%parent_dir)
    elif len(L) == 1:
        return L[0]
    else:
        client = custom_seafileapi.connect(server, token=session['seafile_token'])
        repo = client.repos.get_repo(repo_id)
        method_files = repo.get_items(type='f', recursive=1)
        data = []
        for file in method_files:
            if file.name.endswith('.method') and file.type == 'file':
                data.append(file)
        if len(data) > 1:
            raise Exception( "You have more than 1 apexAcquisition.method file in the %s folder, using the first one"%parent_dir )
        elif len(data) < 1:
            raise Exception( "You don't have any apexAcquisition.method file in the %s folder"%parent_dir )
        else:
            download_file_link = data[0]._get_download_link()
            
            file_name = data[0].name
            tmp_file_path = os.path.join(tmp_folder_path, file_name)
            file_content = requests.get(url=download_file_link, stream=True)
            with open(tmp_file_path, "wb") as f:
                for chunk in file_content.iter_lines():
                    f.write(chunk)
                    f.write(("\n").encode())
            return tmp_file_path

@seafile_client.route('/edit_mscf', methods=['GET', 'POST'])
@seafile_token_require
def edit_mscf():
    repo_id = request.args.get("repo_id")
    file_full_path = request.args.get('file_full_path')
    # return file_full_path
    config_filename = request.args.get('config_filename')
    parent_dir = request.args.get('parent_dir')

    # load method file
    local_method_file = load_method_file(repo_id, parent_dir)

    # download mscf file to local for editting and return local file path
    local_config_file_path = download_mscf_file(repo_id, file_full_path, parent_dir)

    

    local_project_path, config_filename = os.path.split(local_config_file_path)
    

    """
    author: DMD - casc4de
    This function help us to modify an existed config file - mscf or also creates a new one.
    """
    # # get variable project short path: project_spath
    # project_spath = request.args.get('project_spath')
    # # get variable config file name
    

    # # create experiment config form
    form = ConfigForm()
    
    # # file_name = project_name + '.mscf'
    # # define the root path of all .d projects
    # projects_root_folder_path = user_SeaDrive_path()
    
    # # define config file path
    # config_file_path = os.path.join(projects_root_folder_path, project_spath, config_filename)

    # # define the chosen project path
    # project_full_path = os.path.join(projects_root_folder_path, project_spath)

    # #####Information about the chosen project######
    project_dict = {}

    _, project_name = os.path.split(parent_dir)

    # project_dict['name'] = project_name
    # # create object
    FTICR_Data = FTICRData(dim=2)
    # ser_file_path = os.path.join(project_full_path,"ser")
    # ser_file_date_aquisition = os.path.getmtime(ser_file_path)
    # project_dict["ser_date_aquisition"] = datetime.fromtimestamp(ser_file_date_aquisition)

    # # find method file
    # param_filename = Solarix.locate_acquisition(project_full_path)



    params_method_file = Solarix.read_param(local_method_file)

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
    # f1 =  float(params_method_file["IN_26"])    # IN_26 is used in 2D sequence as incremental time
    # if f1 < 1E-3 and f1>0.0:   # seems legit
    #     f1_specwidth = round(1.0/(2*f1),2)
    # else:
    #     f1_specwidth = 50000
    # project_dict["f1_specwidth"] = f1_specwidth

    # create processing params object base on Proc_Parameters() object in spike lib
    proc_params = proc_spike.Proc_Parameters()

    # check if the mscf config file is existed or not. If not, create new file with default values
    if os.path.isfile(local_config_file_path):
        config = NPKConfigParser()
        try:
            config.readfp(open(local_config_file_path, 'r'))
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
        config_dict['F1_specwidth'] = default_config['import']['F1_specwidth']
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
        save_file_path = os.path.join(local_project_path, save_file_name)

        # in case file name is changed during the modification
        file_full_path = os.path.join(parent_dir, save_file_name)

        # return save_file_path
        # return project_full_path
        with open(save_file_path, "w") as save:
            # write header of config file
            # save.write(
            #     "#Project folder: {} \n".format(project_dict['name']) +
            #     "#Date of acquisition: {} \n".format(project_dict['ser_date_aquisition']) +
            #     "#Estimate Bo from internal calibration: {}T \n".format(project_dict['Bo']) +
            #     "#Experiment size (F1 x F2): {}k x {}k \n".format(project_dict['sizeF1'], project_dict['sizeF2']) +
            #     "#Data size: {}MB \n".format(project_dict['data_size']) +
            #     "#Excitation pulses from {}Hz (m/z={}) to {}Hz (m/z={}) \n".format(project_dict['freqh'], project_dict['mzh'], project_dict['freql'], project_dict['mzl']) +
            #     "#Acquisition spectral width: {}Hz (low mass: {}) \n".format(project_dict['f2_specwidth'], project_dict['lowmass']) 
            # )
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
            save.write("\nEDITTED BY DO MANH DUNG at {}".format(datetime.now()))

        #upload file to seafile cloud
        upload_edited_file(repo_id, file_full_path, parent_dir, save_file_path)
        # allow user to download it
        return send_from_directory(directory=local_project_path, filename=save_file_name, as_attachment=True)



    return render_template(
        "seafile_client/edit_mscf.html",
        config_dict = config_dict,
        form = form, errors = form.errors,
        config_filename = config_filename,
        repo_id=repo_id,
        file_full_path = file_full_path,
        parent_dir=parent_dir
    )


    return render_template('seafile_client/edit_mscf.html')

def get_upload_link(_repo_id, parent_dir):
    if not _repo_id:
        return "repo_id is not found"
    request_upload_link = "https://cloud.seafile.com/api2/repos/{repo_id}/upload-link/?p={dir_path}".format(repo_id=_repo_id, dir_path=parent_dir)

    _headers = {
        'Authorization':'Token {}'.format(session['seafile_token'])
    }

    upload_link_response = requests.get(url=request_upload_link, headers=_headers)
    if upload_link_response.status_code == 200:
        upload_link = json.loads(upload_link_response.text)
        return upload_link
    else:
        return "something went wrong"


def upload_edited_file(repo_id, file_full_path, parent_dir, local_file_path):
    _, filename = os.path.split(file_full_path)

    # client = custom_seafileapi.connect(server, token=session['seafile_token'])
    # repo = client.repos.get_repo(repo_id)
    # current_file = repo.get_file(file_full_path, parent_dir)
    # upload_link = current_file._get_upload_link()
    upload_link = get_upload_link(repo_id, parent_dir)
    
    if not upload_link:
        return "something went wrong"

    _headers = {
        'Authorization':'Token {}'.format(session['seafile_token'])
    }
    # return tmp_file_path
    _data = {
        "filename":filename,
        "parent_dir":parent_dir,
        "replace":1
    }
    _files={
        "file":open(local_file_path, "r")
    }

    response = requests.post(url=upload_link, headers=_headers, data=_data, files=_files)
    if response.status_code == 200:
        return response.text
    else:
        return response.text

@seafile_client.route('/search_files')
def search_file():
    request_url = "https://cloud.seafile.com/api2/search/?q=a&search_repo=df6493cf-a426-44c3-ba8a-176aec98a72e"
    _headers = {
        'Authorization':'Token {}'.format(session['seafile_token']),
        'content-type': 'application/json ; indent=4; charset=utf-8',
    }

    response = requests.get(url=request_url, headers=_headers)
    return str(response.content)

@seafile_client.route('/logout')
def logout():
    session['current_user'] = ''
    session['seafile_token'] = ''
    return redirect(url_for('seafile_client.index'))