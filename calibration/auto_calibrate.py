from PIL import Image
import numpy as np
import cv2

'''
Given an image, returns an (x,y,w,h) rectangle or None with
the closest match.
'''
def auto_calibrate(img):
    if isinstance(img, Image.Image):
        img = np.array(img.convert('RGB'))

    query_image = cv2.imread('assets/sprite_templates/sample-gamescreen.png', 0)

    # Initiate ORB detector
    orb = cv2.ORB_create()

    # find the keypoints and descriptors with ORB
    kp1, des1 = orb.detectAndCompute(query_image, None)
    kp2, des2 = orb.detectAndCompute(img, None)

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1, des2)

    # Sort them in the order of their distance.
    good_matches = sorted(matches, key=lambda x: x.distance)

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    transform, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    h, w = query_image.shape[:2]
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, transform)
    x, y, w, h = pts_to_params(dst)
    if h < 50 or w < 50 or not is_rect(dst):
        print ("unable to find tetris board")
        return None
    return x, y, w, h


def pts_to_params(pts):
    left, top, bottom, right = pts_to_rect(pts)
    return int(left), int(top), int(right - left), int(bottom - top)


def pts_to_rect(pts):
    top = pts[0][0][1]
    left = pts[0][0][0]
    bottom = pts[2][0][1]
    right = pts[2][0][0]
    return left, top, bottom, right


def is_rect(pts):
    x_coords = sorted([pts[x][0][0] for x in [0,1,2,3]])
    y_coords = sorted([pts[x][0][1] for x in [0,1,2,3]])
    return not (
        x_coords[1] - x_coords[0] > 5 or
        x_coords[3] - x_coords[2] > 5 or
        y_coords[1] - y_coords[0] > 5 or
        y_coords[3] - y_coords[2] > 5
    )