import cv2


def drawRect(event, x, y, flags, param):
    global draw, coords, end

    if event == cv2.EVENT_LBUTTONDOWN:
        draw = True
        coords = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        draw = False
        coords.append((x, y))

        cv2.rectangle(img, coords[0], coords[1], (0, 255, 0), 2)
