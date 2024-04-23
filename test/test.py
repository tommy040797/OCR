import cv2
import numpy as np
from PIL import Image

img = cv2.imread("C:/Code/OCR/test/test123.jpg")
img = cv2.imread("C:/Code/OCR/test/test48.jpg")

cv2.imshow("test", img)
cv2.waitKey(0)

SegmentMask = (
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
)

NumSegments = 8
TestWindowSize: int = 2
ThresholdPct = 0.4


def preProcessing(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return img


def cut(img):
    img = crop(img)

    h, w = img.shape
    marge = 0
    menge = 0
    for i in range(w):
        if img[:, i].all() == True:
            marge += i
            menge += 1
    try:
        middle = round(marge / menge)
    except:
        middle = round(w / 2)
    # cv2.line(img, (middle, 0), (middle, h), color=(0, 0, 0), thickness=2)
    cv2.imshow("", img)
    cv2.waitKey(0)

    # middle = round(w / 2)
    print(img[:, middle].all())
    # img = cv2.line(img, (middle, 0), (middle, h), color=(0, 0, 0), thickness=2)
    if img[:, middle].all() == True:
        print("Test")
        img1 = img[0:h, 0:middle]
        img2 = img[0:h, middle:w]
        img1 = crop(img1)
        img2 = crop(img2)
        return img1, img2
    else:
        return img, None


def crop(img):
    array = np.array(img)

    blacky, blackx = np.where(array == 0)

    top, bottom = blacky[0], blacky[-1]
    # Find first and last column containing yellow pixels

    left, right = min(blackx), max(blackx)

    img = array[top + 2 : bottom - 2, left + 2 : right - 2]

    return img


def deskew(img):
    rows, cols = img.shape

    blacky, blackx = np.where(img == 0)

    topleft = [blackx[0], blacky[0]]
    topright = [max(blackx), blacky[0]]
    bottomleft = [min(blackx), blacky[-15]]

    img = cv2.circle(img, bottomleft, 2, 0, 2)

    cv2.imshow("test", img)
    cv2.waitKey(0)
    pts1 = np.float32([topleft, topright, bottomleft])
    pts2 = np.float32([topleft, topright, [blackx[0], max(blacky)]])

    M = cv2.getAffineTransform(pts1, pts2)
    dst = cv2.warpAffine(img, M, (cols, rows), borderValue=(255, 255, 255))

    return dst


def read(img):
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

    half_window = int(TestWindowSize / 2)
    max_val = np.iinfo(img.dtype).max
    is_seg_active = list()

    for seg in range(NumSegments):
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
        if pct <= ThresholdPct:
            active = 1

        is_seg_active.append(active)

    print(is_seg_active)

    for seg_num, mask in enumerate(SegmentMask):
        if len(is_seg_active) != len(mask):
            raise ValueError("seg_active size != mask size")

        matched = True

        for x, seg_val in enumerate(mask):
            if seg_val != is_seg_active[x]:
                matched = False
                break

        if matched:
            return seg_num


img = preProcessing(img)


# img = deskew(img)
if img.all() == True:
    print("0 , eig done")

img = crop(img)
img1, img2 = cut(img)

# img2 = deskew(img2)
xd2 = None
cv2.imshow("", img1)

cv2.waitKey(0)
try:
    xd2 = read(img2)
    cv2.imshow("", img2)
    cv2.waitKey(0)
    h1, w1 = img1.shape
    h2, w2 = img2.shape
    if w1 > w2 * 2:
        xd2 = 1
except:
    pass
xd1 = read(img1)

if xd2 != None:
    erg = str(xd1) + str(xd2)
else:
    erg = str(xd1)

print(erg, "test")

cv2.imshow("", img1)
cv2.waitKey(0)
