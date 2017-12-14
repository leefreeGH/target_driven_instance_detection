import os
import torch
import torchvision.models as models
import cv2
import cPickle
import numpy as np
import importlib

from instance_detection.model_defs import network
from instance_detection.model_defs.TDID import TDID
from instance_detection.model_defs.fast_rcnn.nms_wrapper import nms

from instance_detection.utils.timer import Timer
from instance_detection.utils.utils import * 


from instance_detection.model_defs.fast_rcnn.bbox_transform import bbox_transform_inv, clip_boxes
from instance_detection.model_defs.fast_rcnn.config import cfg, cfg_from_file, get_output_dir

import active_vision_dataset_processing.data_loading.active_vision_dataset_pytorch as AVD  

#import matplotlib.pyplot as plt
import json




def im_detect(net, target_data,im_data, im_info, features_given=True):
    """Detect object classes in an image given object proposals.
    Returns:
        scores (ndarray): R x K array of object class scores (K includes
            background as object category 0)
        boxes (ndarray): R x (4*K) array of predicted bounding boxes
    """


    cls_prob, bbox_pred, rois = net(target_data, im_data, 
                                    features_given=features_given, im_info=im_info)
    scores = cls_prob.data.cpu().numpy()[0,:,:]
    zs = np.zeros((scores.size, 1))
    scores = np.concatenate((zs,scores),1)
    #boxes = rois.data.cpu().numpy()[:, 1:5] / im_info[0][2]
    boxes = rois.data.cpu().numpy()[0,:, :] #/ im_info[0][2]

    if False:
        # Apply bounding-box regression deltas
        box_deltas = bbox_pred[0].data.cpu().numpy()
        pred_boxes = bbox_transform_inv(boxes, box_deltas)
        #pred_boxes = clip_boxes(pred_boxes, im_data.shape[1:])
        pred_boxes = clip_boxes(pred_boxes, im_info)
    else:
        # Simply repeat the boxes, once for each class
        pred_boxes = np.tile(boxes, (1, scores.shape[1]))

    return scores, pred_boxes


def test_net(model_name, net, dataloader, id_to_name, target_images, chosen_ids, cfg,
             max_dets_per_target=5, score_thresh=0.1,
             output_dir=None,):
    """Test a TDID network on an image dataset."""
    #list to output for coco evaluation
    results = []
 
    #num images in test set
    num_images = len(dataloader)
   
    # timers
    _t = {'im_detect': Timer(), 'misc': Timer()}
    
    if output_dir is not None:
        det_file = os.path.join(output_dir, model_name+'.json')
        print det_file


    #pre compute features for all targets
    target_features_dict = {}
    for id_ind,t_id in enumerate(chosen_ids):
        target_name = id_to_name[t_id]
        if target_name == 'background':
            continue
        target_data = []
        for t_type,_ in enumerate(target_images[target_name]):
            img_ind = np.random.choice(np.arange(
                                  len(target_images[target_name][t_type])))
            target_img = cv2.imread(target_images[target_name][t_type][img_ind])
            target_img = normalize_image(target_img,cfg)
            target_data.append(target_img)

        target_data = match_and_concat_images_list(target_data)
        target_data = network.np_to_variable(target_data, is_cuda=True)
        target_data = target_data.permute(0, 3, 1, 2)
        target_features_dict[target_name] = net.features(target_data)




    #for i in range(num_images):
    for i,batch in enumerate(dataloader):
        im_data= batch[0]
        im_info = im_data.shape[:]
        im_data=normalize_image(im_data,cfg)
        im_data = network.np_to_variable(im_data, is_cuda=True)
        im_data = im_data.unsqueeze(0)
        im_data = im_data.permute(0, 3, 1, 2)

        #get image name and index
        img_name = batch[1][1]
        img_ind = int(img_name[:-4])

        #get image features
        img_features = net.features(im_data)

        for id_ind,t_id in enumerate(chosen_ids):
            target_name = id_to_name[t_id]
            if target_name == 'background':
                continue

            target_features = target_features_dict[target_name]

            if (target_data is None) or len(target_data) < 1:
                print 'Empty target data: {}'.format(target_name)
                continue

            _t['im_detect'].tic()
            scores, boxes = im_detect(net, target_features, img_features, im_info)
            detect_time = _t['im_detect'].toc(average=False)

            _t['misc'].tic()

            #get scores for foreground, non maximum supression
            inds = np.where(scores[:, 1] > score_thresh)[0]
            fg_scores = scores[inds, 1]
            fg_boxes = boxes[inds, 1 * 4:(1 + 1) * 4]
            fg_dets = np.hstack((fg_boxes, fg_scores[:, np.newaxis])) \
                .astype(np.float32, copy=False)
            keep = nms(fg_dets, cfg.TEST_NMS_OVERLAP_THRESH)
            fg_dets = fg_dets[keep, :]

            # Limit to max_per_target detections *over all classes*
            if max_dets_per_target > 0:
                image_scores = np.hstack([fg_dets[:, -1]])
                if len(image_scores) > max_dets_per_target:
                    image_thresh = np.sort(image_scores)[-max_dets_per_target]
                    keep = np.where(fg_dets[:, -1] >= image_thresh)[0]
                    fg_dets = fg_dets[keep, :]
            nms_time = _t['misc'].toc(average=False)

            print 'im_detect: {:d}/{:d} {:.3f}s {:.3f}s' \
                .format(i + 1, num_images, detect_time, nms_time)

            #put class id in the box
            fg_dets = np.insert(fg_dets,4,t_id,axis=1)
            #all_image_dets = np.vstack((all_image_dets,fg_dets))

            for box in fg_dets:
                cid = int(box[4])
                xmin = int(box[0])
                ymin = int(box[1])
                width = int(box[2]-box[0] + 1)
                height = int(box[3]-box[1] + 1)
                score = float(box[5])
                results.append({'image_id':img_ind, 'category_id':cid, 'bbox':[xmin,ymin,width,height    ], 'score':score})



        #record results by image name
        #all_results[batch[1][1]] = all_image_dets.tolist()
    if output_dir is not None:
        with open(det_file, 'w') as f:
            json.dump(results,f)
    return results






if __name__ == '__main__':

    trained_model_path = ('/net/bvisionserver3/playpen/ammirato/Data/Detections/' + 
                         'saved_models/')
    trained_model_names=[
                     'TDID_final_GMU2AVD_coco_0_3_3000_1063.94031_0.64303_-1.00000',
                        ]
    #load config file
    cfg_file = 'configAVD2' #NO EXTENSTION!
    cfg = importlib.import_module('instance_detection.utils.configs.'+cfg_file)
    cfg = cfg.get_config()

    ##prepare target images (gather paths to the images)
    target_images ={}
    if cfg.PYTORCH_FEATURE_NET:
        target_images = get_target_images(cfg.TARGET_IMAGE_DIR,cfg.NAME_TO_ID.keys())
    else:
        print 'Must use pytorch pretrained model, others not supported'
        #would need to add new normaliztion to get_target_images, and elsewhere

    #make sure only targets that have ids, and have target images are chosen
    test_ids = check_object_ids(cfg.TEST_OBJ_IDS, cfg.ID_TO_NAME,target_images)
    if test_ids==-1:
        print 'Invalid IDS!'
        sys.exit()

    testset = get_AVD_dataset(cfg.DATA_BASE_DIR,
                              cfg.TEST_LIST,
                              test_ids,
                              max_difficulty=cfg.MAX_OBJ_DIFFICULTY,
                              fraction_of_no_box=cfg.TEST_FRACTION_OF_NO_BOX_IMAGES)

    #create train/test loaders, with CUSTOM COLLATE function
    testloader = torch.utils.data.DataLoader(testset,
                                              batch_size=1,
                                              shuffle=True,
                                              num_workers=cfg.NUM_WORKERS,
                                              collate_fn=AVD.collate)

    #test multiple trained nets
    for model_name in trained_model_names:
        print model_name
        # load net
        net = TDID(cfg)

        vgg16_bn = models.vgg16_bn(pretrained=False)
        net.features = torch.nn.Sequential(*list(vgg16_bn.features.children())[:-1])
        net.features.eval()#freeze batchnorms layers?
        network.load_net(trained_model_path + model_name+'.h5', net)
        print('load model successfully!')

        net.cuda()
        net.eval()

        # evaluation
        test_net(model_name, net, testloader, cfg.ID_TO_NAME, 
                 target_images,test_ids, 
                 max_dets_per_target=cfg.MAX_DETS_PER_TARGET,
                 score_thresh=cfg.SCORE_THRESH, 
                 output_dir=cfg.TEST_OUTPUT_DIR)



