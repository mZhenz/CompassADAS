from YoloV3.models import *
from YoloV3.utils.utils import *
import torch
from torch.autograd import Variable
import cv2
import time

LENGTH_THRESHOLD = 0.3       # 宽度占比高于这个数就会报警
HEIGHT_THRESHOLD = 0.3       # 高度占比高于这个数就会报警
ROI_THRESHOLD_L = 0.25
ROI_THRESHOLD_R = 0.75       # ROI的范围
color_space = [(5, 16, 103), (53, 250, 206), (124, 7, 202), (108, 209, 232),
               (61, 123, 154), (180, 240, 223), (39, 177, 186),
               (160, 76, 172), (15, 73, 78)]


def init_yolo_model():
    config_path = "YoloV3/config/yolov3.cfg"
    # config_path = "config/yolov3.cfg"
    weights_path = "YoloV3/weights/yolov3.weights"
    # weights_path = "weights/yolov3.weights"
    cuda = torch.cuda.is_available()
    # Set up model
    model = Darknet(config_path, img_size=416)
    model.load_darknet_weights(weights_path)

    if cuda:
        model.cuda()

    model.eval()

    return  model, cuda


def detect_yolo_model(model, img, cuda):
    conf_thres = 0.8
    nms_thres = 0.4
    Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor
    img, _ = pad_to_square(img, 128)
    img = np.transpose(cv2.resize(img, (416, 416), interpolation=cv2.INTER_NEAREST), (2, 0, 1))
    # As pytorch tensor
    img = torch.from_numpy(img).float() / 255.0
    img = img[np.newaxis, :]
    img = Variable(img.type(Tensor))
    with torch.no_grad():
        img_detected = model(img)
        img_detected = non_max_suppression(img_detected, conf_thres, nms_thres)

    return img_detected


def yolo_alert(img, detections):
    name_list = [0, 1, 2, 3, 5, 7, 9, 11, 12]
    detections = detections[0]
    car_alert = 0
    light_alert = 0
    person_alert = 0
    if detections is not None:
        # print(detections)
        for detection in detections:
            x1, y1, x2, y2, conf, cls_conf, cls_pred = detection
            if cls_pred in name_list:
                pad_x = max(img.shape[0] - img.shape[1], 0) * (416 / max(img.shape))
                pad_y = max(img.shape[1] - img.shape[0], 0) * (416 / max(img.shape))
                # Image height and width after padding is removed
                unpad_h = 416 - pad_y
                unpad_w = 416 - pad_x
                box_h = ((y2 - y1) / unpad_h) * img.shape[0]
                box_w = ((x2 - x1) / unpad_w) * img.shape[1]
                # y1 = ((y1 - pad_y // 2) / unpad_h) * img.shape[0]
                x1 = ((x1 - pad_x // 2) / unpad_w) * img.shape[1]
                hei_rate = box_h / img.shape[0]
                len_rate = box_w / img.shape[1]
                # =================ROI=====================
                middle = x1 + box_w / 2
                mid_rate = middle / img.shape[1]
                # =========================================
                if cls_pred == 0:
                    if mid_rate > 0.3 and mid_rate < 0.7:
                        person_alert = 1
                    else:
                        person_alert = 0
                elif cls_pred == 9:
                    light_alert = 1
                elif hei_rate > HEIGHT_THRESHOLD or len_rate > LENGTH_THRESHOLD:
                    if mid_rate > ROI_THRESHOLD_L and mid_rate < ROI_THRESHOLD_R:
                        car_alert = 1
                    else:
                        car_alert = 0
            else:
                continue
    else:
        pass
    return car_alert, light_alert, person_alert


def draw_box(img, detections, colors):
    # 需要画框的种类
    name_list = [0, 1, 2, 3, 5, 7, 9, 11, 12]
    detections = detections[0]
    car_alert = 0
    if detections is not None:
        # print(detections)
        for detection in detections:
            x1, y1, x2, y2, conf, cls_conf, cls_pred = detection
            if cls_pred in name_list:
                pad_x = max(img.shape[0] - img.shape[1], 0) * (416 / max(img.shape))
                pad_y = max(img.shape[1] - img.shape[0], 0) * (416 / max(img.shape))
                # Image height and width after padding is removed
                unpad_h = 416 - pad_y
                unpad_w = 416 - pad_x
                box_h = ((y2 - y1) / unpad_h) * img.shape[0]
                box_w = ((x2 - x1) / unpad_w) * img.shape[1]
                y1 = ((y1 - pad_y // 2) / unpad_h) * img.shape[0]
                x1 = ((x1 - pad_x // 2) / unpad_w) * img.shape[1]
                hei_rate = box_h / img.shape[0]
                len_rate = box_w / img.shape[1]
                # =================ROI=====================
                middle = x1 + box_w / 2
                mid_rate = middle / img.shape[1]
                # =========================================
                if cls_pred == 0: #0->person
                    if mid_rate > 0.3 and mid_rate < 0.7:
                        color = (0, 0, 255)
                    else:
                        color = colors[name_list.index(cls_pred)]
                elif cls_pred == 9: #9->traffic light
                    color = (0, 0, 255)
                elif hei_rate > HEIGHT_THRESHOLD or len_rate > LENGTH_THRESHOLD:
                    if mid_rate > ROI_THRESHOLD_L and mid_rate < ROI_THRESHOLD_R:
                        color = (0, 0, 255)
                    else:
                        color = colors[name_list.index(cls_pred)]
                else:
                    color = colors[name_list.index(cls_pred)]
                # print(color[0],color[1],color[2])
                cv2.rectangle(img, (x1, y1), (x1+box_w, y1+box_h),
                              color, thickness=3)
            else:
                continue
    else:
        pass
    return img


def yolo_main(img):
    model, cuda = init_yolo_model()
    img_detected = detect_yolo_model(model, img, cuda)

    return img_detected


if __name__ == "__main__":
    video_path = "data/samples/zhuangche.mp4"
    cap = cv2.VideoCapture(video_path)
    model, cuda = init_yolo_model()
    ii = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            t1 = time.time()
            img_detected = detect_yolo_model(model, frame, cuda)
            t2 = time.time()
            img_detected = draw_box(frame, img_detected, color_space)
            print("main time consuming: %.3f s" % (t2 - t1))
            # cv2.imshow("fig", img_detected)
            filename = "data/test/zhuangche/zhuang_" + str(ii) + ".jpg"
            cv2.imwrite(filename, img_detected)
            print("第" + str(ii) + "帧已保存")
            ii = ii + 1
        else:
            print("视频已测试完成")
            break
