# import the necessary packages
import os
import random

import cv2 as cv
import keras.backend as K
import numpy as np

from data_generator import random_choice, safe_crop
from model import build_encoder_decoder

if __name__ == '__main__':
    img_rows, img_cols = 320, 320
    channel = 3

    model_weights_path = 'models/model.12-0.0720.hdf5'
    model = build_encoder_decoder()
    model.load_weights(model_weights_path)

    print(model.summary())

    test_images_folder = 'data/instance-level_human_parsing/Testing/Images'
    id_file = 'data/instance-level_human_parsing/Testing/test_id.txt'
    with open(id_file, 'r') as f:
        names = f.read().splitlines()

    samples = random.sample(names, 10)

    for i in range(len(samples)):
        image_name = samples[i]
        filename = os.path.join(test_images_folder, image_name + '.jpg')
        image = cv.imread(filename)
        image_size = image.shape[:2]
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        x, y = random_choice(image_size)
        image = safe_crop(image, x, y)
        gray = safe_crop(gray, x, y)
        print('Start processing image: {}'.format(filename))

        x_test = np.empty((1, img_rows, img_cols, 3), dtype=np.float32)
        x_test[0, :, :, 0] = gray / 255.

        out = model.predict(x_test)
        out = np.reshape(out, (img_rows, img_cols, 3))
        out = out * 255.
        out = out.astype(np.uint8)

        if not os.path.exists('images'):
            os.makedirs('images')

        cv.imwrite('images/{}_image.png'.format(i), gray)
        cv.imwrite('images/{}_gt.png'.format(i), image)
        cv.imwrite('images/{}_out.png'.format(i), out)

    K.clear_session()
