import argparse
import base64
import json
import os
import os.path as osp

import PIL.Image
import yaml

from labelme.logger import logger
from labelme import utils

import sys

import glob

def main():
    logger.warning('This script is aimed to demonstrate how to convert the'
                   'JSON file to a single image dataset, and not to handle'
                   'multiple JSON files to generate a real-use dataset.')

    # parser = argparse.ArgumentParser()
    # parser.add_argument('json_file')
    # parser.add_argument('-o', '--out', default=None)
    # args = parser.parse_args()

    json_files=glob.glob(r'C:\Users\Zeran\Desktop\loudi\*.json')
    for json_file in json_files:



        out_dir = osp.basename(json_file).replace('.', '_')
        out_dir = osp.join(osp.dirname(json_file), out_dir)

        # reload(sys)
        # sys.setdefaultencoding('utf8')
        f = open(json_file,encoding='utf-8')
        text = f.read()
        # text = text.decode("gbk").encode("utf-8")
        data = json.loads(text)

        # data = f.read().decode(encoding='gbk').encode(encoding='utf-8')

        # data = json.load(open(json_file))

        if data['imageData']:
            imageData = data['imageData']
        else:
            imagePath = os.path.join(os.path.dirname(json_file), data['imagePath'])
            with open(imagePath, 'rb') as f:
                imageData = f.read()
                imageData = base64.b64encode(imageData).decode('utf-8')
        img = utils.img_b64_to_arr(imageData)

        label_name_to_value = {'_background_': 0}
        for shape in sorted(data['shapes'], key=lambda x: x['label']):
            label_name = shape['label']
            # if label_name in label_name_to_value:
            #     label_value = label_name_to_value[label_name]
            # else:
            #     label_value = len(label_name_to_value)
            label_name_to_value[label_name] = 255
        lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)

        label_names = [None] * (max(label_name_to_value.values()) + 1)
        for name, value in label_name_to_value.items():
            label_names[value] = name
        lbl_viz = utils.draw_label(lbl, img, label_names)
        saved_name = os.path.splitext(os.path.basename(json_file))[0]+'.png'
        utils.lblsave(osp.join('D:\\coslight\\0304_beforetolabel\\label\\', saved_name), lbl)
        #saved_name 取得json文件名称，使得转换后的label图片的名称为json的名称
        #'D:\\coslight\\0304_beforetolabel\\label\\'为保存label图片的文件夹
        #将原文件此处以下部分代码删去，这样就不用生成包含标签种类名称，原始图片，转换后的图片文件夹，只需要json转换后的label图片

if __name__ == '__main__':
    main()

