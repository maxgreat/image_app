from PIL import Image
import glob
import tqdm

def correct_gif_folder(folder):
    for image_path in tqdm.tqdm(glob.glob(folder+"*.gif")):
        im = Image.open(image_path)
        im.seek(0)
        corrected = im.copy()
        corrected.putalpha(255)
        corrected = corrected.convert('RGBA')
        list_images = []
        for i in range(1, im.n_frames):
            im.seek(i)
            list_images.append(im.copy().convert('RGBA'))
        corrected.save(image_path, save_all=True, append_images=list_images, optimize=False, loop=0)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Correcting GIF files')
    parser.add_argument('paths', type=str, nargs='+',
                        help='List of directories')
    parser.add_argument('--override', action='store_true')
    args = parser.parse_args()

    for dir in args.paths:
        correct_gif_folder(dir)
