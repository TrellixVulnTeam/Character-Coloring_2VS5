# import the necessary packages
import os
import random

import cv2 as cv
import keras.backend as K
import numpy as np

from config import img_rows, img_cols
from model import build_encoder_decoder

if __name__ == '__main__':
    channel = 3

    model_weights_path = 'models/model.00-3.8439.hdf5'
    model = build_encoder_decoder()
    model.load_weights(model_weights_path)

    print(model.summary())

    test_images_folder = 'data/instance-level_human_parsing/Testing/Images'
    id_file = 'data/instance-level_human_parsing/Testing/test_id.txt'
    with open(id_file, 'r') as f:
        names = f.read().splitlines()

    samples = random.sample(names, 10)

    h, w = img_rows // 4, img_cols // 4
    q_ab = np.load("data/pts_in_hull.npy")
    nb_q = q_ab.shape[0]

    for i in range(len(samples)):
        image_name = samples[i]
        filename = os.path.join(test_images_folder, image_name + '.jpg')
        # b: 0 <=b<=255, g: 0 <=g<=255, r: 0 <=r<=255.
        bgr = cv.imread(filename)
        bgr = cv.resize(bgr, (img_rows, img_cols), cv.INTER_CUBIC)
        # L: 0 <=L<= 255, a: 42 <=a<= 226, b: 20 <=b<= 223.
        lab = cv.cvtColor(bgr, cv.COLOR_BGR2LAB)

        print('Start processing image: {}'.format(filename))

        x_test = np.empty((1, img_rows, img_cols, 1), dtype=np.float32)
        x_test[0, :, :, 0] = lab[:, :, 0] / 255.

        # L: 0 <=L<= 255, a: 42 <=a<= 226, b: 20 <=b<= 223.
        X_colorized = model.predict(x_test)
        X_colorized = X_colorized.reshape((h * w, nb_q))

        q_a = q_ab[:, 0].reshape((1, 313))
        q_b = q_ab[:, 1].reshape((1, 313))
        X_a = np.sum(X_colorized * q_a, 1).reshape((h, w)) + 128
        X_b = np.sum(X_colorized * q_b, 1).reshape((h, w)) + 128
        print('np.max(X_a): ' + str(np.max(X_a)))
        print('np.min(X_a): ' + str(np.min(X_a)))
        print('np.max(X_b): ' + str(np.max(X_b)))
        print('np.min(X_b): ' + str(np.min(X_b)))
        X_a = cv.resize(X_a, (img_rows, img_cols), cv.INTER_CUBIC)
        X_b = cv.resize(X_b, (img_rows, img_cols), cv.INTER_CUBIC)

        out = np.empty((img_rows, img_cols, 3), dtype=np.float32)
        out[:, :, 0] = lab[:, :, 0]
        out[:, :, 1] = X_a
        out[:, :, 2] = X_b
        out = out.astype(np.uint8)
        out = cv.cvtColor(out, cv.COLOR_LAB2BGR)

        if not os.path.exists('images'):
            os.makedirs('images')

        bgr = bgr.astype(np.uint8)
        gray = (lab[:, :, 0]).astype(np.uint8)
        cv.imwrite('images/{}_image.png'.format(i), gray)
        cv.imwrite('images/{}_gt.png'.format(i), bgr)
        cv.imwrite('images/{}_out.png'.format(i), out)

    K.clear_session()
