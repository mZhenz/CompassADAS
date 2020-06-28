import numpy as np
import cv2
SHIFT_THRESHOLD = 0.08


def photo_padding(img):
    pad_value = 128
    # 1640 : 590
    h, w, _ = img.shape
    # print('w = ', w)
    # print('h = ', h)
    if w / h < 2.78:
        # pad w
        new_w = h * 2.78
        dim_diff = new_w - w
    else:
        # pad h
        new_h = w / 2.78
        dim_diff = new_h - h

    dim_diff = np.int(dim_diff)
    # print('dim_diff = ', dim_diff)
    # dim_diff = np.abs(h - w)
    #
    # # (upper / left) padding and (lower / right) padding
    pad1 = dim_diff // 2
    pad2 = dim_diff - pad1
    # # Determine padding
    pad = ((pad1, pad2), (0, 0), (0, 0)) if w/h > 2.78 else ((0, 0), (pad1, pad2), (0, 0))
    # Add padding
    img = np.pad(img, pad, "constant", constant_values=pad_value)
    # print(pad)
    # print(img.shape)
    pad_h = img.shape[0]
    pad_w = img.shape[1]
    return img, pad, pad_h, pad_w


def unpad(img, pad):
    if np.any(pad[0]):
        # padded h
        img = img[pad[0][0]:-pad[0][1], :, :]
    else:
        # padded w
        img = img[:, pad[1][0]:-pad[1][1], :]
    return img


def getLane(prob, h):
    thres = 0.45
    coordinate = np.zeros([1, 25])
    prob_h = prob.shape[0]
    for i in range(25):
        lineId = np.uint16(prob_h - i * 10 / h * prob_h)
        line = prob[lineId - 1, :]

        ids = np.argwhere(line > thres * 255)
        id = np.average(ids) if ids.size != 0 else 0
        coordinate[0, i] = id
        # id = np.argmax(line)
        # if line[id] / 255 > thres:
        #     coordinate[0, i] = id

    if np.sum(coordinate > 0) < 5:
        coordinate = np.zeros([1, 25])

    return coordinate


def prob_resize(prob, pad, pad_h, pad_w):
    if np.any(pad[0]):
        h_pad1_r = np.uint16(288 / pad_h * pad[0][0])
        h_pad2_r = np.uint16(288 / pad_h * pad[0][1])
        prob = prob[h_pad1_r: 0-h_pad2_r, :]
    else:
        w_pad1_r = np.uint16(800 / pad_w * pad[1][0])
        w_pad2_r = np.uint16(800 / pad_w * pad[1][1])
        prob = prob[:, w_pad1_r: 0-w_pad2_r]
    return prob


def prob2lane(img, prob, existence, pad, pad_h, pad_w):
    img_h = img.shape[0]
    img_w = img.shape[1]
    lanes = np.zeros([4, 25])
    # print(img_h)
    # print(img_w)
    prob_w = 800
    for i, est in enumerate(existence):
        if est:
            prob_r = prob_resize(prob[:, :, i], pad, pad_h, pad_w)
            lane = getLane(prob_r, img_h)
            lanes[i, :] = lane
            prob_w = prob_r.shape[1]
    # probMaps = np.uint8(np.zeros([288, 800, 3]))

    # =============================================================================================
    # 定义一个保存车道点的二维列表
    points = []
    for j in range(4):
        if existence[j]:
            points.append([])
            for m in range(25):
                if lanes[j, m] > 0:
                    points[j].append((np.uint16(lanes[j, m] / prob_w * img_w), img_h - 10 * m))

    left = []
    right = []
    # print(points[1])
    # print(points[2])
    for j in range(len(points[1])):
        for m in range(len(points[2])):
            if points[1][j][1] == points[2][m][1]:
                left.append(points[1][j][0])
                right.append(points[2][m][0])

    # print(left)
    # print(right)
    if len(left) == 0 or len(right) == 0:
        shifting_rate = 0
    else:
        le = np.mean(left)
        rig = np.mean(right)
        shifting = (le + rig) / 2 - img.shape[1] / 2
        shifting_rate = shifting / img.shape[1]
        # print((le+rig)/2, img.shape[1]/2, shifting, shifting_rate)

    # [left_left, left, right, right_right]
    # BGR
    if shifting_rate > SHIFT_THRESHOLD:
        lane_alert = 1
    elif shifting_rate < -SHIFT_THRESHOLD:
        lane_alert = 1
    else:
        lane_alert = 0
    # ============================================================================================
    return lanes, prob_w, lane_alert, shifting_rate


def draw_lane(img, lanes, existence, prob_w, shifting_rate):
    img_h = img.shape[0]
    img_w = img.shape[1]
    # [left_left, left, right, right_right]
    # BGR
    if shifting_rate > SHIFT_THRESHOLD:
        lane_color = ([67, 216, 95], [0, 0, 255], [67, 216, 95], [67, 216, 95])
    elif shifting_rate < -SHIFT_THRESHOLD:
        lane_color = ([67, 216, 95], [67, 216, 95], [0, 0, 255], [67, 216, 95])
    else:
        lane_color = ([67, 216, 95], [67, 216, 95], [67, 216, 95], [67, 216, 95])

    for j in range(4):
        if existence[j]:
            points = []
            for m in range(25):
                if lanes[j, m] > 0:
                    points.append((np.uint16(lanes[j, m] / prob_w * img_w), img_h - 10 * m))
                    img = cv2.circle(img, (np.uint16(lanes[j, m] / prob_w * img_w), img_h - 10 * m),
                                     3, lane_color[j], thickness=-1)
            for k in range(len(points) - 1):
                if points[k][0] != points[k+1][0]:
                    if abs((np.int(points[k][1]) - np.int(points[k+1][1])) / (np.int(points[k][0]) - np.int(points[k+1][0]))) < 0.15:
                        continue
                img = cv2.line(img, points[k], points[k+1],
                               color=lane_color[j], thickness=3)
    return img