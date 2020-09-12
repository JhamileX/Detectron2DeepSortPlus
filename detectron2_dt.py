from detectron2.utils.logger import setup_logger

setup_logger()

import numpy as np
import cv2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg


class Detectron2:

    def __init__(self, args):
        self.cfg = get_cfg()
        self.cfg.merge_from_file("/home/minhkv/tienpv_DO_NOT_REMOVE/detectron2/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        self.cfg.MODEL.WEIGHTS = "/home/minhkv/tienpv_DO_NOT_REMOVE/detectron2/projects/Thesis/output/model_final.pth"
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1 #default for hand, FIX THIS!
        #self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.95  # set threshold for this model
        self.cfg.merge_from_list(args.opts)
        self.predictor = DefaultPredictor(self.cfg)

    def bbox(self, img):
        rows = np.any(img, axis=1)
        cols = np.any(img, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        return cmin, rmin, cmax, rmax

    def detect(self, im):
        outputs = self.predictor(im)
        boxes = outputs["instances"].pred_boxes.tensor.cpu().numpy()
        classes = outputs["instances"].pred_classes.cpu().numpy()
        scores = outputs["instances"].scores.cpu().numpy()
        predict_masks = outputs["instances"].pred_masks
        masks = predict_masks.cpu().numpy()
        print('------------------------------------- DETECTRON2 detect-----------------------------------------------')
        print('len(boxes), len(classes), len(scores), len(masks)', len(boxes), len(classes), len(scores), len(masks))
        #print('boxes, classes, scores, masks', boxes, classes, scores, masks)
        bbox_xcycwh, cls_conf, cls_ids, cls_masks = [], [], [], []

        for (box, _class, score, mask) in zip(boxes, classes, scores, masks):

            if _class == 0:
                x0, y0, x1, y1 = box
                xc = (x1+x0)/2
                yc = (y1+y0)/2
                w = x1-x0
                h = y1-y0
                if (xc>1) and (yc>1) and (w>1) and (h>1):
                    bbox_xcycwh.append([xc, yc, w, h])
                    cls_conf.append(score)
                    cls_ids.append(_class)
                    cls_masks.append(mask)

        temp = np.zeros_like(im[:, :, 0])
        for i in range(len(predict_masks)):
            predict_mask_i = predict_masks[i]
            temp += np.array(predict_mask_i.to("cpu").numpy()).astype(np.uint8)
        region = im.copy()
        region[temp == 0] = 0
        region[temp!= 0] = im[temp != 0]
        return np.array(bbox_xcycwh, dtype=np.float64), np.array(cls_conf), np.array(cls_ids), np.array(cls_masks), region 