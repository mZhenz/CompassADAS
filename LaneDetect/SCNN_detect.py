import cv2
import tensorflow as tf
from LaneDetect.lanenet_model import lanenet_merge_model
from LaneDetect.config import global_config
from LaneDetect.utils import *
import time

CFG = global_config.cfg
VGG_MEAN = [103.939, 123.68, 116.779]

def initial_lanenet(use_gpu):
    weights_path = "LaneDetect/weights/culane_lanenet_vgg_2018-12-01-14-38-37.ckpt-10000"
    # weights_path = "weights/culane_lanenet_vgg_2018-12-01-14-38-37.ckpt-10000"
    # img = tf.convert_to_tensor(np.zeros([1, 288, 800, 3]))
    input_tensor = tf.placeholder(dtype=tf.float32, shape=[1, 288, 800, 3], name='input_tensor')
    # img_resized = tf.image.resize_images(img, [CFG.TRAIN.IMG_HEIGHT, CFG.TRAIN.IMG_WIDTH],
    #                                      method=tf.image.ResizeMethod.BICUBIC)
    img_casted = tf.cast(input_tensor, tf.float32)
    img = tf.subtract(img_casted, VGG_MEAN)
    net = lanenet_merge_model.LaneNet()
    phase_tensor = tf.constant('test', tf.string)
    binary_seg_ret, instance_seg_ret = net.test_inference(img, phase_tensor, 'lanenet_loss')
    # print("net.test_inference time: %.3f s" % (time.time() - t))
    initial_var = tf.global_variables()
    final_var = initial_var[:-1]
    saver = tf.train.Saver(final_var)


    # ##配置
    if use_gpu:
        sess_config = tf.ConfigProto(device_count={'GPU': 1})
    else:
        sess_config = tf.ConfigProto(device_count={'GPU': 0})
    sess_config.gpu_options.per_process_gpu_memory_fraction = CFG.TEST.GPU_MEMORY_FRACTION
    sess_config.gpu_options.allow_growth = CFG.TRAIN.TF_ALLOW_GROWTH
    sess_config.gpu_options.allocator_type = 'BFC'
    sess = tf.Session(config=sess_config)

    with sess.as_default():
        # ##初始化参数
        sess.run(tf.global_variables_initializer())
        # sess.run()
        # ##读取参数
        saver.restore(sess=sess, save_path=weights_path)

    return sess, input_tensor, binary_seg_ret, instance_seg_ret


def detect_lanenet(image_np, sess, input_tensor, binary_seg_ret, instance_seg_ret):

    instance_seg_image, existence = sess.run([binary_seg_ret, instance_seg_ret], feed_dict={input_tensor: image_np})
    prob_output = (instance_seg_image[0, :, :, 1:] * 255).astype(int)
    existence_output = existence[0, :] > 0.5

    return prob_output, existence_output


def scnn_main(img, sess, input_tensor, binary_seg_ret, instance_seg_ret):
    img_src = img
    img, pad, pad_h, pad_w = photo_padding(img)
    img_np = cv2.resize(img, (800, 288), interpolation=2)
    img_np = img_np[np.newaxis, :]
    prob, exist = detect_lanenet(img_np, sess, input_tensor, binary_seg_ret, instance_seg_ret)
    lanes, prob_w, lane_alert, shifting_rate = prob2lane(img_src, prob, exist, pad, pad_h, pad_w)
    return lanes, exist, prob_w, lane_alert, shifting_rate


if __name__ == '__main__':
        sess, input_tensor, binary_seg_ret, instance_seg_ret = initial_lanenet(1)
        video_path = "./test/video/biandao.mp4"
        # ## 图片预处理部分
        cap = cv2.VideoCapture(video_path)
        # print(cap.isOpened())
        ii = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                t1 = time.time()
                img_src = frame
                frame, pad, pad_h, pad_w = photo_padding(frame)
                img_np = cv2.resize(frame, (800, 288), interpolation=2)
                img_np = img_np[np.newaxis, :]
                # 运行网络
                prob, exist = detect_lanenet(img_np, sess, input_tensor, binary_seg_ret, instance_seg_ret)
                # 画图部分
                # prob = unpad_prob()
                lanes, prob_w, lane_alert, shifting_rate = prob2lane(img_src, prob, exist, pad, pad_h, pad_w)
                frame = draw_lane(img_src, lanes, exist, prob_w, shifting_rate)
                t2 = time.time()
                print("main time consuming: %.3f s" % (t2 - t1))
                filename = "test/biandao/bian_" + str(ii) + ".jpg"
                cv2.imwrite(filename, frame)
                print("第" + str(ii) + "帧已保存")
                ii = ii + 1
            else:
                print("视频已测试完成")
                break
        # img = unpad(img, pad)
        # ## 图片显示
        # cv2.imshow("fig", img.astype(np.uint8))
        # sess.close()
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

