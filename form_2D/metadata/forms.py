from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp

class ConfigForm(FlaskForm):
    regexp_float = r'^[-+]?[0-9]*\.?[0-9]+$|^$|^\s$' # except float number with +/-. also except an empty string
    regexp_sizemultipliers = r'^([0-9]{0,1}.?[0-9]\s{1}[0-9]{0,1}.?[0-9])$' # except 2 float number
    # exlude_specifique_characters = r'[^\+=+]'

    save_file = StringField(
        "mscf Output File Name",
        validators=[
            DataRequired(message="File name is required")
        ]
    )

    ### [Import section] ###
    apex = StringField(
        "apex",
        validators=[
        ],
        description="The Apex directory which contains the 2D file to be read. \
                    This attribute is not used if infile (below) is available."
    )

    F1_specwidth = StringField(
        "F1_specwidth",
        validators=[
            Regexp(regex=regexp_float, message ='F1_specwidth must be a float number')
        ],
        description="F1_specwidth is the sampling frequency along F1 (vertical) axis."
    )
    highmass = StringField(
        "highmass",
        validators=[
            Regexp(regex=regexp_float, message ='highmass must be a number')
        ],
        description="High Mass is the cutoff frequency of the P1-P2 excitation pulses"

    )
    format = SelectField(
        "Format",
        coerce=str,
        validators=[
        ],
        description="Format can be either Solarix or Apex depending on the version of the spectrometer.",
        choices=[("apex","Apex"),("solarix","Solarix")]
    )

    ### [processing section] ###
    # infile = StringField(
    #     "infile",
    #     validators=[
    #     ],
    #     description="The hdf5 file which will be processed - usually coming from apex above.\
    #                 This attribute will be untouched"
    # )
    # outfile = StringField(
    #     "outfile",
    #     validators=[
    #     ],
    #     description="The file which will be created"
    # )
    compress_outfile = SelectField(
        "compress_outfile",
        coerce=str,
        validators=[
        ],
        description="Outfile file is internally compressed by removing the weakest value lost in the noise.",
        choices=[("True","True"),("False","False")]
    )
    compress_level = StringField(
        "compress_level",
        validators=[
            Regexp(regex=regexp_float, message = 'compress_level must be a float number')
        ],
        description="Compress_level is the ratio of noise level that will be discarded, up to 3.0 (3 x sigma) it should be ok. \
                    The highest compress_level, the better the compression, but expect some distortions and missing small peaks."
    )
    # tempdir = StringField(
    #     "tempdir",
    #     validators=[
    #     ],
    #     description="Directory for temporary files."
    # )
    sizemultipliers = StringField(
        "sizemultipliers",
        validators=[
            Regexp(regex=regexp_sizemultipliers, message = 'sizemultipliers has form "1 1" or "01 01"')
        ],
        description="Sizemultipliers tells the program the size of the final 2D, as multiples of the initial (acquisition) sizes"
    )
    # do_F1 = SelectField(
    #     "do_F1",
    #     coerce=str,
    #     validators=[
    #     ],
    #     description="If false, processing along F1 (vertical) is not performed",
    #     choices=[("True","True"),("False","False")]
    # )
    # do_F2 = SelectField(
    #     "do_F2",
    #     coerce=str,
    #     validators=[
    #     ],
    #     description="If false, processing along F2 (horizontal) is not performed",
    #     choices=[("True","True"),("False","False")]
    # )
    # do_f1demodu = SelectField(
    #     "do_f1demodu",
    #     coerce=str,
    #     validators=[
    #     ],
    #     description="if True, the F1 offset correction will be applied.",
    #     choices=[("True","True"),("False","False")]
    # )
    # do_modulus = SelectField(
    #     "do_modulus",
    #     coerce=str,
    #     validators=[
    #     ],
    #     description="if True, a modulus will be applied at the end of the processing.",
    #     choices=[("True","True"),("False","False")]
    # )
    # do_rem_ridge = SelectField(
    #     "do_rem_ridge",
    #     coerce=str,
    #     validators=[
    #     ],
    #     description="do_rem_ridge : if True, vertical ridges will be applied",
    #     choices=[("True","True"),("False","False")]
    # )
    urqrd_iterations = StringField(
        "urqrd_iterations",
        validators=[
            Regexp(regex=regexp_float, message = 'urqrd_iterations must be a number')
        ],
        description="Urqrd iterations"
    )
    do_sane = SelectField(
        "do_sane",
        coerce=str,
        validators=[
        ],
        description="do_sane : if True, the SANE denoising is applied in F1",
        choices=[("True","True"),("False","False")]
    )
    sane_rank = StringField(
        "sane_rank",
        validators=[
            Regexp(regex=regexp_float, message = 'sane_rank must be a number')
        ],
        description="Rank used for SANE ~ the number of lines expected in each column."
    )
    sane_iterations = StringField(
        "sane_iterations",
        validators=[
            Regexp(regex=regexp_float, message = 'sane_iterations must be a number')
        ],
        description="A few SANE iterations may improve, to the price of additional times."
    )


    nus = SelectField(
        "NUS - Non Uniform Sampled",
        coerce=str,
        validators=[
        ],
        choices=[("True","True"),("False","False")],
        description="Non Uniform Sampled (NUS)"
    )
    samplingfile = TextAreaField(
        "samplingfile",
        validators=[
        ],
        description="Samplingfile is the the list, one entry per line, of the indices of the measured experiments. \
                    Generally generated with the random_sampling.py generator."
    )
    do_pgsane = SelectField(
        "do_pgsane",
        coerce=str,
        validators=[
        ],
        description="The optimal reconstruction algorithm is currently PG_SANE, based SANE (see above, same ref). \
                    Do_pgsane should be True for NUS experiments to be processed.",
        choices=[("True","True"),("False","False")]
    )
    pgsane_rank = StringField(
        "pgsane_rank",
        validators=[
            Regexp(regex=regexp_float)
        ],
        description="PG_SANE combines 2 approaches: SANE (see above) and PG\
                    Rank used for SANE ~ the number of lines expected in each column."
    )
    pgsane_threshold = StringField(
        "pgsane_threshold",
        validators=[
            Regexp(regex=regexp_float)
        ],
        description="PG needs a threshold to reject artefacts below threshold x noise; the lower the more inclusive."
    )
    pgsane_iterations = StringField(
        "pgsane_iterations",
        validators=[
            Regexp(regex=regexp_float)
        ],
        description="PG_SANE iterations are required to obtain convergence, usually the more the better (and the slower)."
    )
    nproc = StringField(
        "nproc",
        validators=[
            Regexp(regex=regexp_float)
        ],
        description="nproc is the number of process on which the computation is done ( +1 for control). \
                    So the optimum is n+1 = nb of core on the machine."
    )

    ### [peak_picking] ###

    peakpicking = SelectField(
        "peakpicking",
        coerce=str,
        validators=[
        ],
        description="Peak-Picking is performed automatically on the spectrum.",
        choices=[("True","True"),("False","False")]
    )

    peakpicking_noise_level = StringField(
        "peakpicking_noise_level",
        validators=[
        ],
        description="Peaks are detected if larger a ratio of noise level, larger than 10  (10 x sigma) should be ok.."
    )

    centroid = SelectField(
        "centroid",
        coerce=str,
        validators=[
        ],
        description="Each peak position and width is optimized by a 2D centroid.",
        choices=[("True","True"),("False","False")]
    )

    erase = SelectField(
        "erase",
        coerce=str,
        validators=[
        ],
        description="If the output file is already present, it will be erased.",
        choices=[("True","True"),("False","False")]
    )
