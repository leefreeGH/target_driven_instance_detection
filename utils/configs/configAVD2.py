from instance_detection.utils.utils import *



class Config():
    """
    Holds all config parameters for training/testing.
    """

    #Directories - MUST BE CHANGED for your environment
    BASE_DIR = '/net/bvisionserver3/playpen10/ammirato/Data/'
    DATA_BASE_DIR = '/net/bvisionserver3/playpen10/ammirato/Data/HalvedRohitData/'
    FULL_MODEL_LOAD_DIR= BASE_DIR + 'DetectionModels/'
    SNAPSHOT_SAVE_DIR= BASE_DIR + 'DetectionModels/'
    META_SAVE_DIR = BASE_DIR + 'DetectionModelsMeta/'
    TARGET_IMAGE_DIR= BASE_DIR + 'instance_detection_targets/AVD_BB_exact_few_and_other_BB_gen_and_AVD_ns_BB_80/'
    TEST_OUTPUT_DIR = BASE_DIR + 'DetectionTestOutputs/'
    GROUND_TRUTH_BOXES = BASE_DIR + 'RohitCOCOgt/avd_split2.json'
    #PRETRAINED_MODELS_DIR= BASE_DIR + ''
    #using VID dataset is not necessary, set USE_VID to false
    VID_DATA_DIR = BASE_DIR + 'ILSVRC/'


    #Model Loading and saving 
    BATCH_NORM= True
    FEATURE_NET_NAME= 'squeezenet1_1'
    PYTORCH_FEATURE_NET= True
    USE_PRETRAINED_WEIGHTS = True
    FULL_MODEL_LOAD_NAME= ''
    LOAD_FULL_MODEL= False
    MODEL_BASE_SAVE_NAME = 'TDID_AVD2_2'
    SAVE_FREQ = 1
    SAVE_BY_EPOCH = True  


    #Training 
    MAX_NUM_EPOCHS= 30
    BATCH_SIZE= 16 
    LEARNING_RATE = .001
    MOMENTUM = .9
    WEIGHT_DECAY = .0005
    DISPLAY_INTERVAL = 10
    NUM_WORKERS = 4

    #Target Images
    PRELOAD_TARGET_IMAGES= False
    AUGMENT_TARGET_IMAGES= True
    MIN_TARGET_SIZE = 32

    #Training Data
    ID_MAP_FNAME= 'all_instance_id_map.txt'
    ID_TO_NAME = {}
    NAME_TO_ID = {}
    OBJ_IDS_TO_EXCLUDE = [8,18,32,33]

    TRAIN_OBJ_IDS= [cid for cid in range(1,33) if cid not in OBJ_IDS_TO_EXCLUDE]
    FRACTION_OF_NO_BOX_IMAGES = .1 
    MAX_OBJ_DIFFICULTY= 4
    TRAIN_LIST= [
                 'Home_001_1',
                 'Home_001_2',
                 'Home_002_1',
                 'Home_004_1',
                 'Home_004_2',
                 'Home_005_1',
                 'Home_005_2',
                 'Home_006_1',
                 'Home_008_1',
                 'Home_014_1',
                 'Home_014_2',
                ]

    VAL_OBJ_IDS = TRAIN_OBJ_IDS 
    VAL_FRACTION_OF_NO_BOX_IMAGES = 1 
    VAL_LIST=   [
                 'Home_003_1',
                 'Home_003_2',
                 'Office_001_1',
                ]

    #VID dataset
    USE_VID = False
    VID_MAX_MIN_TARGET_SIZE = [200,16]
    VID_SUBSET = 'train_single' 


    ##############################################
    #Testing
    MAX_DETS_PER_TARGET = 5
    SCORE_THRESH = .01
    TEST_NMS_OVERLAP_THRESH = .7

    TEST_OBJ_IDS= [cid for cid in range(1,33) if cid not in OBJ_IDS_TO_EXCLUDE]
    TEST_FRACTION_OF_NO_BOX_IMAGES = 1
    TEST_LIST = [ 
                'Home_003_1',
                ]

    ###############################################
    #Model paramters
    PRE_NMS_TOP_N = 6000
    POST_NMS_TOP_N = 300
    NMS_THRESH = .7
    PROPOSAL_MIN_BOX_SIZE = 8 

    PROPOSAL_CLOBBER_POSITIVES = False 
    PROPOSAL_NEGATIVE_OVERLAP = .3
    PROPOSAL_POSITIVE_OVERLAP = .6
    PROPOSAL_FG_FRACTION = .5
    PROPOSAL_BATCH_SIZE = 300 
    PROPOSAL_POSITIVE_WEIGHT = -1
    PROPOSAL_BBOX_INSIDE_WEIGHTS = [1,1,1,1]

    EPS = 1e-14



def get_config():

    cfg = Config()
    cfg.ID_TO_NAME = get_class_id_to_name_dict(cfg.DATA_BASE_DIR,
                                               cfg.ID_MAP_FNAME)
    name_to_id = {}
    for cid in cfg.ID_TO_NAME.keys():
        name_to_id[cfg.ID_TO_NAME[cid]] = cid 
    cfg.NAME_TO_ID = name_to_id
    
    #ensures chosen object ids are valid(exist in the name/id map file)
    

    return cfg 
