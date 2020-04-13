from __future__ import division, print_function

import os
import random
from warnings import filterwarnings

import fasttext
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError
from torch.backends import cudnn
import torchvision.transforms.functional as tf

filterwarnings("ignore")
cudnn.deterministic = True
cudnn.benchmark = False

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)


def load_txt_samples(txt_data_dir):
    nlp = fasttext.load_model('/home/stefanopio.zingaro/Developer/multimodal-side-tuning/data/cc.en.300.bin')
    orig_dir = f'/data01/stefanopio.zingaro/datasets/{txt_data_dir}'
    save_dir = f'/home/stefanopio.zingaro/Developer/multimodal-side-tuning/data/{txt_data_dir}'
    for i, class_path in enumerate(os.scandir(orig_dir)):
        for j, path in enumerate(os.scandir(class_path)):
            with open(path, 'rb') as f:
                txt = f.read()
            doc = [''.join([i for i in token.decode('UTF-8') if i.isalnum()]) for token in txt.split()]
            word2vec = [nlp[i] for i in doc]
            padding = 500 - len(word2vec)
            if padding > 0:
                if padding == 500:
                    x = torch.zeros((500, 300))
                else:
                    x = F.pad(torch.tensor(word2vec), [0, 0, 0, padding])
            else:
                x = torch.tensor(word2vec[:500])

            if not os.path.exists(f'{save_dir}/{i}'):
                os.mkdir(f'{save_dir}/{i}')
            torch.save(x.half(), f'{save_dir}/{i}/{j}.ptr')


def load_img_samples(img_data_dir):
    orig_dir = f'/data01/stefanopio.zingaro/datasets/{img_data_dir}'
    save_dir = f'/home/stefanopio.zingaro/Developer/multimodal-side-tuning/data/{img_data_dir}'
    for i, class_path in enumerate(os.scandir(orig_dir)):
        for j, path in enumerate(os.scandir(class_path)):
            with open(path, 'rb') as f:
                try:
                    pic = Image.open(f).convert('RGB')
                    pic = pic.resize((224, 224), Image.BILINEAR)
                    t_img = tf.to_tensor(pic)
                    t_img = tf.normalize(t_img, [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                    pic = tf.to_pil_image(t_img)
                    if not os.path.exists(f'{save_dir}/{i}'):
                        os.mkdir(f'{save_dir}/{i}')
                    pic.save(f'{save_dir}/{i}/{j}.jpg', "JPEG", optimize=True, quality=75)
                except UnidentifiedImageError:
                    pass


if __name__ == '__main__':
    load_img_samples('Tobacco3482-jpg')
    # load_txt_samples('QS-OCR-small')
    for s in ['val', 'test', 'train']:
        load_img_samples(f'RVL-CDIP/{s}')
        # load_txt_samples(f'QS-OCR-Large/{s}')
