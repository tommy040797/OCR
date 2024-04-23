import configparser
import Util.Methods as Methods
import numpy as np
import cv2
import sys

np.set_printoptions(threshold=sys.maxsize)


class OCR:
    def __init__(self) -> None:
        # ReadConfig
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.cropdistance = int(config["sevenSegment"]["cropdistance"])

        self.SegmentMask = (
            (1, 1, 1, 1, 1, 1, 0, 0),  # 0
            (1, 1, 1, 1, 1, 1, 1, 1),  # 1
            (1, 1, 0, 1, 1, 0, 1, 0),  # 2
            (1, 1, 1, 1, 0, 0, 1, 0),  # 3
            (0, 1, 1, 0, 0, 1, 1, 0),  # 4
            (1, 0, 1, 1, 0, 1, 1, 0),  # 5
            (0, 0, 1, 1, 1, 1, 1, 0),  # 6
            (1, 1, 1, 0, 0, 0, 0, 0),  # 7
            (1, 1, 1, 1, 1, 1, 1, 0),  # 8
            (1, 1, 1, 0, 0, 1, 1, 0),  # 9
            (1, 1, 1, 1, 1, 0, 1, 1),  # 1
        )
        print("SevenSegment plugin initialized")

        self.NumSegments = 8
        self.TestWindowSize: int = 3
        self.ThresholdPct = 0.3

    def Rec(self, img):
        if img.all() == True:
            return "0", None
        img = Methods.crop(img, self.cropdistance)
        erg2 = None
        try:
            img1, img2 = Methods.cut(img, self.cropdistance)
        except:
            img1 = img
            img2 = None

        try:
            erg2 = self.read(img2)
            h1, w1 = img1.shape
            h2, w2 = img2.shape
            if w1 > w2 * 2:
                erg2 = 1
        except:
            pass
        if img1.all() == True:
            return str(0), None
        erg1 = self.read(img1)
        try:
            h1, w1 = img1.shape
            h2, w2 = img2.shape
            if w2 > w1 * 2:
                erg1 = 1
        except:
            pass
        if erg2 != None:
            erg = str(erg1) + str(erg2)
        else:
            erg = str(erg1)
        return erg, None

    def read(self, img):
        rows, cols = img.shape

        SegmentTestPoints = (
            (
                (round(cols * 0.4), round(rows * 0.05)),
                (round(cols * 0.6), round(rows * 0.05)),
            ),  # 0
            (
                (round(cols * 0.9), round(rows * 0.25)),
                (round(cols * 0.9), round(rows * 0.35)),
            ),  # 1
            (
                (round(cols * 0.9), round(rows * 0.65)),
                (round(cols * 0.9), round(rows * 0.75)),
            ),  # 2
            (
                (round(cols * 0.4), round(rows * 0.95)),
                (round(cols * 0.6), round(rows * 0.95)),
            ),  # 3
            (
                (round(cols * 0.1), round(rows * 0.65)),
                (round(cols * 0.1), round(rows * 0.75)),
            ),  # 4
            (
                (round(cols * 0.15), round(rows * 0.25)),
                (round(cols * 0.15), round(rows * 0.35)),
            ),  # 5
            (
                (round(cols * 0.4), round(rows * 0.5)),
                (round(cols * 0.6), round(rows * 0.5)),
            ),  # 6
            (
                (round(cols * 0.5), round(rows * 0.3)),
                (round(cols * 0.5), round(rows * 0.7)),
            ),  # 7 check for 1
        )

        if len(img.shape) > 2 and img.shape[2] != 1:
            raise TypeError("Input image is not grayscale.")

        half_window = int(self.TestWindowSize / 2)
        max_val = np.iinfo(img.dtype).max
        is_seg_active = list()

        for seg in range(self.NumSegments):
            test_pts = SegmentTestPoints[seg]
            num_pts = len(test_pts)
            pt_vals = list()

            for pt_idx in range(num_pts):
                num_px = 0
                px_val: int = 0
                pt = test_pts[pt_idx]
                for x in range(-half_window, half_window):
                    for y in range(-half_window, half_window):
                        px_val += int(img.item(pt[1] + y, pt[0] + x))
                        num_px += 1
                pt_vals.append(int(px_val / num_px))

            seg_mean = sum(pt_vals) / num_pts
            pct = float(seg_mean / max_val)
            active = 0
            if pct <= self.ThresholdPct:
                active = 1

            is_seg_active.append(active)

        # print(is_seg_active)

        for seg_num, mask in enumerate(self.SegmentMask):
            if len(is_seg_active) != len(mask):
                raise ValueError("seg_active size != mask size")

            matched = True

            for x, seg_val in enumerate(mask):
                if seg_val != is_seg_active[x]:
                    matched = False
                    break

            if matched:
                if seg_num == 10:
                    return 1
                return seg_num

        return 0
