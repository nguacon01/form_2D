from flask import Blueprint, render_template, request, redirect
from flask import flash, url_for, jsonify, session
# from flask_session import Session
from flask.helpers import make_response
from flask_login import login_required, current_user
import os
import requests
from .forms import ConfigForm
from spike.NPKConfigParser import NPKConfigParser
from spike.FTICR import FTICRData
from spike.File import Solarix, Apex
from datetime import datetime
from form_2D.libs.EUFT_Spike import processing_4EU as proc_spike

from form_2D.libs.seafile_api import custom_seafileapi
from form_2D.libs.seafile_api.custom_seafileapi.files import SeafDir, SeafFile
from form_2D.libs.seafile_api.custom_seafileapi.utils import seafile_token_require
from form_2D.libs.seafile_api.custom_seafileapi.repo import Repo

import json
from form_2D.metadata.views import metadata
from datetime import datetime
import glob
from urllib.parse import urlparse
from pathlib import Path
import json

from form_2D.libs.seafile_api import custom_seafileapi
from form_2D.libs.seafile_api.custom_seafileapi.files import SeafDir, SeafFile
from form_2D.libs.seafile_api.custom_seafileapi.utils import seafile_token_require
from form_2D.metadata.views import metadata
from .helpers import predict

import shutil

server = "https://10.18.0.2"
# server = 'https://seafile.fticr-ms.eu'
# server = 'https://dung.casc4de.fr'

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
    return redirect(url_for('seafile_client.dir_items'))

@seafile_client.route('/login', methods = ['POST', 'GET'])
def login():
    """
    Login page
    param required: username: user email
    param required: password
    return login token from seafile server
    """
    if 'seafile_token' in session and session['seafile_token'] != '':
        return redirect(url_for('seafile_client.dir_items'))

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
            headers=_headers,
            verify=False
        )
        if response.status_code == 200:
            content = json.loads(response.text)
            session["seafile_token"] = content['token']
            session["current_user"] = email

            # get client username
            client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
            client_prof = client.get_user_profile()
            session["username"] = client_prof['name']

            # get user profile here

            # create user temp folder
            tmp_folder_path = os.path.join(seafile_client.root_path, 'static/tmp', session['current_user'])
            if not os.path.exists(tmp_folder_path):
                os.makedirs(tmp_folder_path)
            return redirect(url_for('seafile_client.dir_items'))
        else:
            flash(message="Login Fail", category="error")
    return render_template('seafile_client/login.html')


@seafile_client.route('/list_repositories')
@seafile_token_require
def list_repositories():
    """
    get list of all repositories in seafile server

    """
    client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
    list_repos = client.repos.list_repos(type="mine")
    
    if len(list_repos) < 1:
        return "You dont have any repository"
    return render_template('seafile_client/list_repositories.html', data=list_repos)

@seafile_client.route('/repo_items')
@seafile_token_require
def repo_items():
    """ 
    get list of items in a repository.
    param required: repo_id: id of repository
    """
    # repo_id = request.args.get('repo_id')
    # repo_name = request.args.get('repo_name')
    client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
    list_repos = client.repos.list_repos(type="mine")
    if len(list_repos) < 1:
        return "You dont have any repository"
    data = []
    repo_name=''
    for repo in list_repos:
        repo_item = client.repos.get_repo(repo.id)
        #return array of SeafDir objects
        items = repo.get_items(recursive=0, type='d')
        for item in items:
            if item.name == 'FTICR_DATA':
                data.append(item)
                repo_name = repo.name

    return render_template('seafile_client/repo_items.html', data=data, repo_name=repo_name)

@seafile_client.route('/get_link_download_zip', methods=['GET', 'POST'])
def get_link_download_zip():
    if request.method == 'GET':
        args = request.args
        repo_id = args['repo_id']
        repo_name = args['repo_name']
        parent_dir = args['parent_dir']
        folder_name = args['name']
        folder_fullpath = args['fullpath'][:-1]

        request_upload_link = server+f"/api/v2.1/repos/{repo_id}/zip-task/?parent_dir={parent_dir}&dirents={folder_name}"

        _headers = {
            'Authorization':'Token {}'.format(session['seafile_token'])
        }

        response = requests.get(url=request_upload_link, headers=_headers, verify=False)
        if response.status_code == 200:
            zip_token = response.json()['zip_token']
            return make_response(jsonify({
                "url":server + f"/seafhttp/zip/{zip_token}"
            })), 200
        else:
            return make_response("File is too large to download"), 400

        

@seafile_client.route('/dir_items')
@seafile_token_require
def dir_items():
    """
    get list of .d downstream directories in a FTICR_DATA directory
    """

    client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
    list_repos = client.repos.list_repos(type="mine", nameContains='My Library')
    if len(list_repos) != 1:
        return "You dont have any repository named'My Library'"
    
    my_library_repo = list_repos[0]
    repo_id = my_library_repo.id

    dir_name='FTICR_DATA'

    # # create FTICR_DATA dir object. It is a upstream directory of My Library, so parent_dir is '/' and we no need to declare in object
    # FTICR_DATA_dir = SeafDir(repo=my_library_repo, name=dir_name, type='dir')
    # # load dir items
    # FTICR_DATA_dir.load_entries(recursive=1, type='d')
    directories = my_library_repo.get_items(type="d", recursive=True)
    data = []
    # for item in FTICR_DATA_dir.entries:
    for item in directories:
        # if item['name'].endswith('.d'):
        if item.name.endswith('.d'):
            # sub_dir = SeafDir(repo=my_library_repo, name=item['name'], type='dir', parent_dir=item['parent_dir'])
            # check if in .d folder has ser file or not
            try:
                # check if sub directory of FTICR_DATA has ser file or not
                # re = my_library_repo.get_file(path=sub_dir.full_path+'ser', parent_dir=sub_dir.full_path)
                # re = my_library_repo.get_file(path=item.full_path+'ser', parent_dir=item.full_path)
                # if 'FTICR_DATA' in sub_dir.full_path:
                #     data.append(sub_dir)
                data.append(item)
            except:
                # return render_template("errors/general_error.html", message="There is not a project in which has a ser file.")
                pass
            
    return render_template('seafile_client/dir_items.html', data=data, dir_name=dir_name, repo_id=repo_id)

@seafile_client.route('/sub_dir', methods=['POST', 'GET'])
@seafile_token_require
def sub_dir():
    repo_id = request.args.get('repo_id')
    dir_name = request.args.get('dir_name')

    parent_dir = request.args.get('parent_dir')
    dir_fullpath = request.args.get('dir_fullpath')

    # connect to seafile server
    client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
    # get repository data
    repo = client.repos.get_repo(repo_id)

    dir = SeafDir(repo=repo, name=dir_name, type='dir', parent_dir=parent_dir)
    
    dir.load_entries(recursive=1, type='f')
    data = []
    for item in dir.entries:
        if item['name'].endswith('.mscf') and item['parent_dir'] in dir_fullpath:
            mscf_file = SeafFile(repo=repo, name=item['name'], type='file', parent_dir=item['parent_dir'])
            if dir_name in mscf_file.full_path:
                data.append(mscf_file)
    # for go back button or go back link in edit_mscf page
    # session['prev_url'] = request.referrer
    # return session['prev_url']
    return render_template(
        'seafile_client/sub_dir.html', 
        data=data, 
        dir_name=dir_name, 
        repo_id=repo_id, 
        dir_fullpath=dir_fullpath,
        job_email=session['current_user'],
        job_username=session['username']
    )

def download_mscf_file(repo_id, file_full_path, parent_dir):
    """
    Download mscf file to a temporary local directory
    """
    # create temp local dir path
    tmp_folder_path = os.path.join(seafile_client.root_path, 'static/tmp', session['current_user'])
    if not os.path.exists(tmp_folder_path):
            os.makedirs(tmp_folder_path)
    # if file doesnt exist in seafile server, file_full_path is None, then we create a default mscf file in temp local dir
    if file_full_path == '':
        tmp_file_path = os.path.join(tmp_folder_path, 'new.mscf')
        default_conf_file = os.path.join(seafile_client.root_path, "static", "files", "process2D.default.mscf")
        with open(tmp_file_path, "w") as f:
            with open(default_conf_file,'r') as data:
                f.write(data.read())
    # else, mscf file exists in seafile server
    else:
        # connect to seafile server
        client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
        # get repo
        repo = client.repos.get_repo(repo_id)
        # check if temp local folder existed or not. if not, creat temp local folder

        # get mscf file
        file = repo.get_file(file_full_path, parent_dir)
        # get mscf file download link
        download_file_link = file._get_download_link()
        # return download_file_link

        # in dev: fix bug can not connect to host: 
        # urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='seafile.fticr-ms.eu', port=443)
        download_path = urlparse(download_file_link).path
        re_download_file_link = server + download_path
        
        file_name = file.name
        tmp_file_path = os.path.join(tmp_folder_path, file_name)
        file_content = requests.get(url=re_download_file_link, stream=True, verify=False)
        # write mscf file into local file
        with open(tmp_file_path, "wb") as f:
            for chunk in file_content.iter_lines():
                f.write(chunk)
                f.write(("\n").encode())
    return tmp_file_path

def load_corresponse_files(repo_id, parent_dir):
    """
    Get .method, ExciteSweep and scan.xml files in a directory
    """
    # create temporary local folder to contain method file. Method local file should be in same folder with mscf file
    tmp_folder_path = os.path.join(seafile_client.root_path, 'static/tmp', session['current_user'], parent_dir)
    if not os.path.exists(tmp_folder_path):
        os.makedirs(tmp_folder_path)

    # check if .method file has already existed in temp local folder
    met = glob.glob(os.path.join(tmp_folder_path,"*",".method"))
    exc = glob.glob(os.path.join(tmp_folder_path,"*","ExciteSweep"))
    scanxml = glob.glob(os.path.join(tmp_folder_path,"*","scan.xml"))
    corresponse_files = {}
    if len(met) > 1 or len(exc) > 1 or len(scanxml) >1:
        # if there are more than 1 file, raise exeption
        return render_template("errors/general_error.html", message="You have more than 1 apexAcquisition.method or ExciteSweep or scan.xml file in the %s folder, using the first one"%parent_dir)
    elif len(met) == 1 and len(exc) == 1 and len(scanxml) == 1:
        corresponse_files["method"] = met
        corresponse_files["excitesweep"] = exc
        corresponse_files["scanxml"] = scanxml
        # if there is just one file, return file path
        return corresponse_files
    else:
        # if there is not a file, then we load it from seafile server
        client = custom_seafileapi.connect(server, token=session['seafile_token'], verify_ssl=False)
        repo = client.repos.get_repo(repo_id)
        method_files = repo.get_items(type='f', recursive=1)
        data = []
        # check number of method files in seafile server
        for file in method_files:
            if parent_dir in file.full_path:
                # return (file.full_path, parent_dir, file.path + '\n')
            
                if (file.name.endswith('.method') or file.name == 'ExciteSweep' or file.name == 'scan.xml') and file.type == 'file' and (parent_dir in file.full_path):
                    data.append(file)
        # return data
        # if len(data) > 3:
        #     return render_template("errors/400.html", message="You have more than 1 apexAcquisition.method or ExciteSweep or scan.xml file in the %s folder, using the first one"%parent_dir)
        # if len(data) < 3:
        #     return render_template("errors/400.html", message="You don't have any apexAcquisition.method or ExciteSweep or scan.xml file in the %s folder"%parent_dir)
        # else:
            
        for item in data:
            download_file_link = item._get_download_link()

            # in dev: fix bug can not connect to host: 
            # urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='seafile.fticr-ms.eu', port=443)
            download_path = urlparse(download_file_link).path
            re_download_file_link = server + download_path
            
            file_name = item.name
            tmp_file_path = os.path.join(tmp_folder_path, file_name)
            file_content = requests.get(url=re_download_file_link, stream=True, verify=False)
            with open(tmp_file_path, "wb") as f:
                for chunk in file_content.iter_lines():
                    f.write(chunk)
                    f.write(("\n").encode())
            corresponse_files[item.name] = tmp_file_path
            # return path of temporary method file in local folder
        return corresponse_files

def mscf_header_info(repo_id, file_full_path, parent_dir):
    """
        download .method, ExciteSweep and scan.xml file
        return project_dict, a dictionary in which contain infomation about chosen mscf file.
        project_dict will be writen in header of output mscf file
    """

    # load method file
    local_corresponse_files = load_corresponse_files(repo_id, parent_dir)
    local_method_file = local_corresponse_files['apexAcquisition.method']
    params_method_file = Solarix.read_param(local_method_file)
    # Check if it is Apex or Solarix. 
    # if it is Apex, params_method_file = Solarix.read_param(local_method_file) will return empty dictionary
    project_format='Solarix'
    if len(params_method_file) < 2:
        project_format='Apex'
        params_method_file = Apex.read_param(local_method_file)

    project_dict = {}

    project_name = parent_dir.strip('/').split('/')[-1]

    project_dict['name'] = project_name
    # # create object
    FTICR_Data = FTICRData(dim=2)
    # ser_file_path = os.path.join(project_full_path,"ser")
    # ser_file_date_aquisition = os.path.getmtime(ser_file_path)
    # project_dict["ser_date_aquisition"] = datetime.fromtimestamp(ser_file_date_aquisition)

    # find Bo
    FTICR_Data.axis1.calibA = float(params_method_file["ML1"])
    FTICR_Data.axis2.calibA = float(params_method_file["ML1"])
    project_dict["Bo"] = round(FTICR_Data.Bo,2)

    # Import parameters : size in F1 and F2 
    try:
        local_scan_file = local_corresponse_files['scan.xml']   
        sizeF1 = Solarix.read_scan(local_scan_file)
    except:
        sizeF1 = 0
    sizeF2 = int(params_method_file["TD"])
    project_dict["sizeF1"] = sizeF1//1024
    project_dict["sizeF2"] = sizeF2//1024
    project_dict["data_size"] = 4*sizeF1*sizeF2//(1024*1024) 
    
    # determine excitation window
    try:  #CR for compatibility with Apex format as there is no EXciteSweep file
        local_excitesweep_file = local_corresponse_files['ExciteSweep']
        fl,fh = Solarix.read_ExciteSweep(local_excitesweep_file)
        freql, freqh = fl[0], fh[0]
    except:
        freqh = float(params_method_file["EXC_hi"])
        freql = float(params_method_file["EXC_low"])
    mzl = round(FTICR_Data.axis2.htomz(freql), 2)
    mzh = round(FTICR_Data.axis2.htomz(freqh), 2)

    if (project_format=='Apex'):
        project_dict["freqh"] = mzh
        project_dict["freql"] = mzl
        project_dict["mzh"] = freqh
        project_dict["mzl"] = freql
    else:
        project_dict["freqh"] = freqh
        project_dict["freql"] = freql
        project_dict["mzh"] = mzh
        project_dict["mzl"] = mzl

    # show f2_specwidth
    f2_specwidth = float(params_method_file["SW_h"])
    lowmass = FTICR_Data.axis2.htomz(f2_specwidth)
    project_dict["f2_specwidth"] = f2_specwidth
    project_dict["lowmass"] = round(lowmass,2)

    # set f1_specwidth default value
    # determine f1_specwidth
    f1 =  float(params_method_file["IN_26"])    # IN_26 is used in 2D sequence as incremental time
    if f1 < 1E-3 and f1>0.0:   # seems legit
        f1_specwidth = round(1.0/(2*f1),2)
    else:
        f1_specwidth = 50000.0000
    project_dict["F1_specwidth"] = f1_specwidth
    return project_dict

@seafile_client.route('/edit_mscf', methods=['GET', 'POST'])
@seafile_token_require
def edit_mscf():
    """
    author: DMD - casc4de
    This function help us to modify an existed config file - mscf or also creates a new one.
    """
    repo_id = request.args.get("repo_id")
    file_full_path = request.args.get('file_full_path')
    config_filename = request.args.get('config_filename')
    parent_dir = request.args.get('parent_dir')
    project_name = parent_dir.strip('/').split('/')[-1]
    # create experiment config form
    form = ConfigForm()

    # create a dictionary in which contain information of mscf file. it will be writen in header of output mscf file
    project_dict = mscf_header_info(repo_id, file_full_path, parent_dir)

    # download mscf file to local for editting and return local file path
    local_config_file_path = download_mscf_file(repo_id, file_full_path, parent_dir)
    # extract local path of chosen project and its name
    local_project_path, config_filename = os.path.split(local_config_file_path)

    # default config file
    default_conf_file = os.path.join(metadata.root_path, "static", "files", "process2D.default.mscf")

    # read mscf defaut file
    default_config = NPKConfigParser()
    # disale Configparser converts all options into lowercase
    default_config.optionxform = str
    default_config.readfp(open(default_conf_file,'r'))
    # ['import', 'processing', 'peak_picking']
    default_sections = default_config.sections()

    # create processing params object base on Proc_Parameters() object in spike lib
    proc_params = proc_spike.Proc_Parameters()

    # create preveous link. This is for go back button
    session['prev_url'] = request.referrer
    # check if the mscf config file is existed or not. If not, create new file with default values
    if os.path.isfile(local_config_file_path):
        config = NPKConfigParser()
        # disable Configparser converts all options into lowercase
        config.optionxform = str
        try:
            config.readfp(open(local_config_file_path, 'r'))
            proc_params.load(config, verif=False)
        except Exception as e:
            return render_template("errors/general_error.html", message=repr(e))

        # get all sections in existed config file
        config_sections = config.sections()
        # fetch sections in defaut sections list
        for section in default_sections:
            # if defaut section is in config sections list, get its options list
            if section not in config_sections:
                config_options = default_config.options(section)
                for option in config_options:
                    setattr(proc_params, option, default_config.get(section, option))
    else:
        proc_params.load(default_config)
    # highmass and F1_specwidth are not in Proc_Parameters object so add them in config_dict manually.
    setattr(proc_params, 'highmass', config.getfloat( "import", 'highmass', 0.0))
    setattr(proc_params, 'F1_specwidth', config.getfloat( "import", 'F1_specwidth', 50000))
    setattr(proc_params, 'sizemultipliers', config.get( "processing", 'sizemultipliers', '1.0 1.0'))
    setattr(proc_params, 'peakpicking', config.getboolean( "peak_picking", 'peakpicking', True))
    setattr(proc_params, 'peakpicking_noise_level', config.getfloat( "peak_picking", 'peakpicking_noise_level', 10))
    setattr(proc_params, 'centroid', config.getboolean("peak_picking", 'centroid', True))
    setattr(proc_params, 'erase', config.getboolean("peak_picking", 'erase', True))
    
    
    ### SET DEFAULT VALUES FOR OUTPUT CONFIG FILE###
    # do_F2 = True
    setattr(proc_params,'do_F2', 'True')
    # do_F1 = True
    setattr(proc_params,'do_F1', 'True')
    # do_f1demodu = True
    setattr(proc_params,'do_f1demodu', 'True')
    # do_modulus = True
    setattr(proc_params,'do_modulus', 'True')
    # do_rem_ridge = True
    setattr(proc_params,'do_rem_ridge', 'True')
    # urqrd_rank = 30
    setattr(proc_params,'urqrd_rank', 30)
    # urqrd_iterations = 1
    setattr(proc_params,'urqrd_iterations', 1)

    setattr(proc_params, 'tempdir', "/tmp")
    setattr(proc_params, 'infile', "ser.msh5")

    # Set value for select forms
    form.compress_outfile.data = str(getattr(proc_params, 'compress_outfile', True))
    form.peakpicking.data = str(getattr(proc_params, 'peakpicking', True))
    form.centroid.data = str(getattr(proc_params, 'centroid', True))
    form.erase.data = str(getattr(proc_params, 'erase', True))
    form.do_sane.data = str(getattr(proc_params, 'do_sane', True))
    form.format.data = str(getattr(proc_params, 'format', 'Solarix'))
    form.samplingfile.data = getattr(proc_params, 'samplingfile', None)
    if proc_params.samplingfile == 'None' or proc_params.samplingfile is None:
        # by default, N.U.S field is False
        form.do_pgsane.data = str(False)
        form.nus.data = str(False)
    else: 
        form.nus.data = str(True)
        form.do_pgsane.data = str(True)
    form.save_file.data = str(config_filename.split(".")[0])
        
    if form.validate_on_submit():
        
        # get form data
        data = request.form.to_dict()
        
        for key, val in data.items():
            if val=="True": val=True
            if val=="False": val=False
            setattr(proc_params, key, val)

        setattr(proc_params, 'format', data["format"].capitalize())

        # defind output file
        save_file_name = data['save_file'].split('.')[0] + ".mscf"

        setattr(proc_params, 'outfile', "{config_filename}_mr.msh5".format(
            project_name = project_name,
            config_filename = save_file_name.split(".")[0])
        )

        #NUS - Non Uniform Sampled
        if data["nus"] == 'True':
            setattr(proc_params, 'do_pgsane', True)
            setattr(proc_params, 'samplingfile', data["samplingfile"])

        else:
            setattr(proc_params, 'do_pgsane', False)
            setattr(proc_params, 'samplingfile', None)
            
        try:
            proc_params.verify()
            # clear flash message
            session.pop('_flashes', None)
        except Exception as e:
            flash(repr(e))
            return redirect(request.referrer)
        # create a new config file
        save_file_path = os.path.join(local_project_path, save_file_name)

        # in case file name is changed during the modification
        file_full_path = os.path.join(parent_dir, save_file_name)

        # return proc_params.__dict__

        with open(save_file_path, "w") as save:
            # write header of config file
            save.write(
                "#Project folder: {} \n".format(project_dict['name']) +
                # "#Date of acquisition: {} \n".format(project_dict['ser_date_aquisition']) +
                "#Estimate Bo from internal calibration: {}T \n".format(project_dict['Bo']) +
                "#Experiment size (F1 x F2): {}k x {}k \n".format(project_dict['sizeF1'], project_dict['sizeF2']) +
                "#Data size: {}MB \n".format(project_dict['data_size']) +
                "#Excitation pulses from {}Hz (m/z={}) to {}Hz (m/z={}) \n".format(project_dict['mzh'], project_dict['freqh'], project_dict['mzl'], project_dict['freql']) +
                "#Acquisition spectral width: {}Hz (low mass: {}) \n".format(project_dict['f2_specwidth'], project_dict['lowmass']) 
            )
            for sect in default_sections:
                # config_key and its value which are got from submited form
                for opt in default_config.options(sect):
                    try: 
                        defaut_value = default_config.get(sect, opt, None)
                        # if config section match with sections in default config file, then change value in default file
                        default_config.set(section=sect, option=opt, value=str(getattr(proc_params, opt, defaut_value)))
                    except Exception as e:
                        # return repr(e)
                        pass
            # save the new config file)
            default_config.write(save)
            save.write("\n# EDITTED BY {} at {}".format(session['current_user'], datetime.now()))
        #upload file to seafile cloud
        upload_edited_file(repo_id, parent_dir, save_file_path)
        
        #remove temp file
        if Path(save_file_path).exists():
            Path(save_file_path).unlink()
        return redirect(url_for('seafile_client.dir_items'))

    return render_template(
        "seafile_client/edit_mscf.html",
        config_dict = proc_params,
        project_dict = project_dict,
        form = form, errors = form.errors,
        config_filename = config_filename,
        repo_id=repo_id,
        file_full_path = file_full_path,
        parent_dir=parent_dir,
        prev_url = session['prev_url']
    )

def get_upload_link(_repo_id, parent_dir):
    if not _repo_id:
        return "repo_id is not found"
    request_upload_link = server+"/api2/repos/{repo_id}/upload-link/?p={dir_path}".format(repo_id=_repo_id, dir_path=parent_dir)

    _headers = {
        'Authorization':'Token {}'.format(session['seafile_token'])
    }

    upload_link_response = requests.get(url=request_upload_link, headers=_headers, verify=False)
    if upload_link_response.status_code == 200:
        upload_link = json.loads(upload_link_response.text)

        # in dev: fix bug can not connect to host: 
        # urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='seafile.fticr-ms.eu', port=443)
        upload_path = urlparse(upload_link).path
        re_upload_link = server + upload_path
        return re_upload_link
    else:
        return 'Can not get upload link'


def upload_edited_file(repo_id, parent_dir, local_file_path):
    _, filename = os.path.split(local_file_path)

    # client = custom_seafileapi.connect(server, token=session['seafile_token'])
    # repo = client.repos.get_repo(repo_id)
    # current_file = repo.get_file(file_full_path, parent_dir)
    # upload_link = current_file._get_upload_link()
    upload_link = get_upload_link(repo_id, parent_dir)

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

    response = requests.post(url=upload_link, headers=_headers, data=_data, files=_files, verify=False)
    if response.status_code != 200:
        return response.text

@seafile_client.route('/handle_button', methods=['GET', 'POST','DELETE'])
def handle_button():
    if request.method == 'POST':
        return jsonify({"message":"Method must be GET or DELETE"}), 401
    repo_id = request.args.get('repo_id')
    full_path = request.args.get('full_path')

    if not repo_id:
        return "repo_id is not found"
    v = 'api2' if request.method=='GET' else 'api/v2.1'
    request_link = server+f"/{v}/repos/{repo_id}/file/?p={full_path}"

    _headers = {
        'Authorization':'Token {}'.format(session['seafile_token']),
        'Accept' : 'application/json; charset=utf-8; indent=4'
    }
    if request.method == 'DELETE':
        response = requests.delete(url=request_link, headers=_headers, verify=False)
        if response.status_code == 200:
            return jsonify({"message":"File has been removed"}), 200
        else:
            return jsonify({"message":"file has not been removed."}), 401
    else:
        response = requests.get(url=request_link, headers=_headers, verify=False)
        if response.status_code == 200:
            return jsonify({"message":"ok", "download_link":response.text.split('"')[1]})
        else:
            return jsonify({"message":"You can not download this file."}), 401
    

@seafile_client.route('/logout')
@seafile_token_require
def logout():
    """
    after user logout, their files in tmp folder will be deleted
    """
    if 'seafile_token' in session:
        # session['current_user'] = ''
        user_tmp_dir = os.path.join(seafile_client.root_path, 'static/tmp', session['current_user'])
        # return user_tmp_dir
        if os.path.isdir(user_tmp_dir):
            shutil.rmtree(user_tmp_dir)
        session.pop('seafile_token')
        session.pop('current_user')
        session.pop('username')
        return redirect(url_for('seafile_client.index'))
    else:
        return redirect(url_for('seafile_client.login'))

@seafile_client.route("/comp_sizes", methods=["GET"])
def comp_sizes():
    """
    calculate size of output file when change sizemultipliers
    """
    if request.method == 'POST':
        return make_response('method must be GET', 400)

    # post_data = request.get_json()
    sizeF1 = int(request.args.get("sizeF1"))
    sizeF2 = int(request.args.get("sizeF2"))
    m1 = float(request.args.get("m1"))
    m2 = float(request.args.get("m2"))
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

@seafile_client.route('/predict_temp', methods=['GET'])
def predict_time():
    nproc= float(request.args.get('nproc', 7))
    si1= float(request.args.get('si1', 0))
    si2= float(request.args.get('si2',0))
    zf1= float(request.args.get('zf1',0))
    zf2= float(request.args.get('zf2',0))
    spg= float(request.args.get('spg',0))
    rank= float(request.args.get('rank',0))
    iters= float(request.args.get('iters',0))
    didimp= float(request.args.get('didimp', 1))
    # predicted_time = predict(nproc=nproc, si1=si1, si2=si2, zf1=zf1, zf2=zf2, SPG=spg,rank=rank, iters=iters, didimp=didimp)
    # return str(predicted_time)
    # return jsonify({
    #         'nproc':nproc, 
    #         'si1':si1, 
    #         'si2':si2, 
    #         'zf1':zf1, 
    #         'zf2':zf2, 
    #         'SPG':spg,
    #         'rank':rank, 
    #         'iters':iters, 
    #         'didimp':didimp
    #     })
    predicted_time = predict(nproc=nproc, si1=si1, si2=si2, zf1=zf1, zf2=zf2, SPG=spg,rank=rank, iters=iters, didimp=didimp)
    
    return make_response(jsonify({
        'params':{
            'nproc':nproc, 
            'si1':si1, 
            'si2':si2, 
            'zf1':zf1, 
            'zf2':zf2, 
            'SPG':spg,
            'rank':rank, 
            'iters':iters, 
            'didimp':didimp
        },
        'predicted_time' : predicted_time
    }), 200)