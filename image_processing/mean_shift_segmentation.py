import argparse
import pymeanshift as pms
import cv2
import os
from PIL import Image

arg_path = ''

def get_args():
    global arg_path

    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help='Directory containing images to be processed or a path to an image to be processed', type=str)
    args = parser.parse_args()

    arg_path = args.image_path

def mss_and_save(image_path, save_folder=''):
    original_image = Image.open(image_path)

    # Set MSS values
    spatial_radius = 6
    range_radius = 4.5
    min_density = 5

    pms_segmenter = pms.Segmenter()
    pms_segmenter.spatial_radius = spatial_radius
    pms_segmenter.range_radius = range_radius
    pms_segmenter.min_density = min_density

    (segmented_image, labels_image, number_regions) = pms_segmenter(original_image)

    # Save segmented image to file
    output_filename = f"{os.path.basename(os.path.splitext(image_path)[0])}_mss_d{min_density}.png"
    status = cv2.imwrite(os.path.join(save_folder, output_filename), segmented_image)

if __name__ == '__main__':
    get_args()

    if os.path.isfile(arg_path):
        mss_and_save(arg_path)
    else:
        output_folder = f"{os.path.basename(os.path.normpath(arg_path))}_mss"

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        else:
            quit(f"Error: output directory {output_folder} already exists")

        for this_file in os.listdir(arg_path):
            if this_file.endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(arg_path, this_file)
                mss_and_save(full_path, output_folder)
