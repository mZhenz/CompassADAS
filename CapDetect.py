import cv2
import numpy as np
from threading import Thread
from YoloV3.yolo_detect import init_yolo_model, detect_yolo_model, draw_box, yolo_alert
from LaneDetect.SCNN_detect import scnn_main, initial_lanenet, draw_lane
from utils.AudioPlay import *
# import winsound
# global yolo_flag, scnn_flag, yolo_output_flag, scnn_output_flag, yolo_detected, lanes
# global shifting_rate, lane_alert, car_alert, person_alert, light_alert, soundFlag
# global exist, prob_w

yolo_flag, scnn_flag = 1, 1
yolo_output_flag, scnn_output_flag = 0, 0
yolo_detected, lanes = None, None
shifting_rate = 0
lane_alert, car_alert, person_alert, light_alert = 0, 0, 0, 0
soundFlag = 1

color_space = [(127,179,220), (53,250,206), (180,240,223), (108,209,232),
               (180, 240, 223), (180,240,223), (39,177,186),
               (160,76,172), (15,73,78)]

model, cuda = init_yolo_model()
sess, input_tensor, binary_seg_ret, instance_seg_ret = initial_lanenet(1)


def yolo_thread(model, img, cuda):
    global yolo_flag, yolo_output_flag, yolo_detected, person_alert, car_alert, light_alert
    yolo_flag = 0
    yolo_detected = detect_yolo_model(model, img, cuda) # 检测部分
    car_alert, light_alert, person_alert = yolo_alert(img, yolo_detected)
    yolo_output_flag = 1
    yolo_flag = 1
    #  print("yolo finish in %s s" % (time.time() - t))
    return


def scnn_thread(img, sess, input_tensor, binary_seg_ret, instance_seg_ret):
    global scnn_flag, scnn_output_flag, lanes, exist, prob_w, lane_alert, shifting_rate
    scnn_flag = 0
    lanes, exist, prob_w, lane_alert, shifting_rate = scnn_main(img, sess, input_tensor, binary_seg_ret, instance_seg_ret)
    scnn_output_flag = 1
    scnn_flag = 1
    # print("scnn finish in %s s" % (time.time() - t))
    return


class yoloThread(Thread):
    def __init__(self, model, img, cuda):
        Thread.__init__(self)
        self.model = model
        self.cuda = cuda
        self.img = img

    def run(self):
        # print("+++++++线程开始：" + self.name)
        yolo_thread(self.model, self.img, self.cuda)
        # print("-------线程退出：" + self.name)


class scnnThread(Thread):
    def __init__(self, img, sess, input_tensor, binary_seg_ret, instance_seg_ret):
        Thread.__init__(self)
        self.img = img
        self.sess = sess
        self.input_tensor = input_tensor
        self.binary_seg_ret = binary_seg_ret
        self.instance_seg_ret = instance_seg_ret

    def run(self):
        # print("+++++++线程开始：" + self.name)
        scnn_thread(self.img, self.sess, self.input_tensor, self.binary_seg_ret, self.instance_seg_ret)
        # print("-------线程退出：" + self.name)


class LaneAlertThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global soundFlag
        # winsound.Beep(399, 100)
        if lane_alert == 1:
            AudioPlay('materials/music/lane.wav')
        elif car_alert == 1:
            AudioPlay('materials/music/car.wav')
        elif light_alert == 1:
            AudioPlay('materials/music/light.wav')
        elif person_alert == 1:
            AudioPlay('materials/music/person.wav')

        soundFlag = 1


def video_detect(frame):
    global yolo_flag, scnn_flag,yolo_detected, lane_alert, car_alert, person_alert, light_alert, soundFlag
    if yolo_flag == 1:
        yolo_flag = 0
        yolo = yoloThread(model, frame, cuda)
        yolo.setDaemon(True)
        yolo.start()

    if scnn_flag == 1:
        scnn_flag = 0
        scnn = scnnThread(frame, sess, input_tensor, binary_seg_ret, instance_seg_ret)
        scnn.setDaemon(True)
        scnn.start()

    if yolo_detected is not None:
        # frame = draw_cross(frame, yolo_detected, color_space)
        frame = draw_box(frame, yolo_detected, color_space)

    if lanes is not None:
        # print(shifting_rate)
        frame = draw_lane(frame, lanes, exist, prob_w, shifting_rate)

    if (lane_alert == 1 or car_alert == 1 or person_alert == 1 or light_alert == 1) and soundFlag == 1:
        soundFlag = 0
        LaneAlert = LaneAlertThread()
        # LaneAlert.setDaemon(True)
        LaneAlert.start()
        lane_alert = 0
        car_alert = 0
        person_alert = 0
        light_alert = 0
        # cv2.waitKey(40)

    return frame, lane_alert, car_alert, person_alert, light_alert


if __name__ == '__main__':
    path = "materials/videos/biandao.mp4"
    outputFile = "materials/videos/biandao_output.mp4"
    cap = cv2.VideoCapture(path)
    vid_writer = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc(*'MP4V'), 25.0,
                                 (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    parallel = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if yolo_flag == 1:
                yolo_flag = 0
                yolo = yoloThread(model, frame, cuda)
                yolo.setDaemon(True)
                yolo.start()
                # AudioPlay('materials/music/4950.wav')

            if scnn_flag == 1:
                scnn_flag = 0
                scnn = scnnThread(frame, sess, input_tensor, binary_seg_ret, instance_seg_ret)
                scnn.setDaemon(True)
                scnn.start()

            if yolo_detected is not None:
                frame = draw_box(frame, yolo_detected, color_space)

            if lanes is not None:
                # print(shifting_rate)
                frame = draw_lane(frame, lanes, exist, prob_w, shifting_rate)

            if (lane_alert == 1 or car_alert == 1 or person_alert == 1 or light_alert == 1) and soundFlag == 1:
                soundFlag = 0
                LaneAlert = LaneAlertThread()
                # LaneAlert.setDaemon(True)
                LaneAlert.start()
                lane_alert = 0
                car_alert = 0
                person_alert = 0
                light_alert = 0
            cv2.imshow("VideoStream", frame)
            vid_writer.write(frame.astype(np.uint8))
            cv2.waitKey(40)

        else:
            break

    # sess.close()
    vid_writer.release()
    cv2.destroyAllWindows()
        # print("\tkeep going...")
