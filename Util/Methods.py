import cv2


# TODO: Überprüfen ob Rechtecke überhaupt im bild sind
def dictRectangles(rectangles, img):
    dict = {}
    for item in rectangles:
        dict[item.name] = img[
            item.y : item.y + item.height, item.x : item.x + item.width
        ]
    return dict


def preProcessing(img, blur, grayscale, thresholding, negative):
    if grayscale == "True":
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if blur == "True":
        img = cv2.medianBlur(img, 5)
    if thresholding == "True":
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    if negative == "True":
        img = 255 - img

    return img


def str2bool(v):
    return v.lower() in ("True", "true")
