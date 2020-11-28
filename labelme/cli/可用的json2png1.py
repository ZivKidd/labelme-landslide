
import json
import os
import os.path as osp
import glob
import numpy as np
import PIL.Image
import PIL.ImageDraw
import math
import base64

def shape_to_mask(
    img_shape, points, shape_type=None, line_width=10, point_size=5
):
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    mask = PIL.Image.fromarray(mask)
    draw = PIL.ImageDraw.Draw(mask)
    xy = [tuple(point) for point in points]
    if shape_type == "circle":
        assert len(xy) == 2, "Shape of shape_type=circle must have 2 points"
        (cx, cy), (px, py) = xy
        d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
        draw.ellipse([cx - d, cy - d, cx + d, cy + d], outline=1, fill=1)
    elif shape_type == "rectangle":
        assert len(xy) == 2, "Shape of shape_type=rectangle must have 2 points"
        draw.rectangle(xy, outline=1, fill=1)
    elif shape_type == "line":
        assert len(xy) == 2, "Shape of shape_type=line must have 2 points"
        draw.line(xy=xy, fill=1, width=line_width)
    elif shape_type == "linestrip":
        draw.line(xy=xy, fill=1, width=line_width)
    elif shape_type == "point":
        assert len(xy) == 1, "Shape of shape_type=point must have 1 points"
        cx, cy = xy[0]
        r = point_size
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=1, fill=1)
    else:
        assert len(xy) > 2, "Polygon must have points more than 2"
        draw.polygon(xy=xy, outline=1, fill=1)
    mask = np.array(mask, dtype=bool)
    return mask

def shapes_to_label(img_shape, shapes, label_name_to_value):
    cls = np.zeros(img_shape[:2], dtype=np.int32)
    ins = np.zeros_like(cls)
    instances = []
    for shape in shapes:
        points = shape["points"]
        label = shape["label"]
        group_id = shape.get("group_id")
        # if group_id is None:
        #     group_id = uuid.uuid1()
        shape_type = shape.get("shape_type", None)

        cls_name = label
        instance = (cls_name, group_id)

        if instance not in instances:
            instances.append(instance)
        ins_id = instances.index(instance) + 1
        cls_id = label_name_to_value[cls_name]

        mask = shape_to_mask(img_shape[:2], points, shape_type)
        cls[mask] = cls_id
        ins[mask] = ins_id

    return cls, ins


def labelme_shapes_to_label(img_shape, shapes):
    # logger.warn(
    #     "labelme_shapes_to_label is deprecated, so please use "
    #     "shapes_to_label."
    # )

    label_name_to_value = {"_background_": 0}
    for shape in shapes:
        label_name = shape["label"]
        # if label_name in label_name_to_value:
        #     label_value = label_name_to_value[label_name]
        # else:
        #     label_value = len(label_name_to_value)
        label_name_to_value[label_name] = 255

    lbl, _ = shapes_to_label(img_shape, shapes, label_name_to_value)
    return lbl, label_name_to_value

def img_data_to_pil(img_data):
    import io
    f = io.BytesIO()
    f.write(img_data)
    img_pil = PIL.Image.open(f)
    return img_pil

def img_data_to_arr(img_data):
    img_pil = img_data_to_pil(img_data)
    img_arr = np.array(img_pil)
    return img_arr

def img_b64_to_arr(img_b64):
    img_data = base64.b64decode(img_b64)
    img_arr = img_data_to_arr(img_data)
    return img_arr

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('json_file')   # 标注文件json所在的文件夹
    # parser.add_argument('-o', '--out', default=None)
    # args = parser.parse_args()

    # json_file = args.json_file
    json_file=r"D:\desktop\大岗山第二次飞行数据json(1)\大岗山第二次飞行数据json"
    image_folder=json_file+'\image'
    mask_folder=json_file+'\mask'

    if not os.path.exists(image_folder):
        os.mkdir(image_folder)
    if not os.path.exists(mask_folder):
        os.mkdir(mask_folder)

    list = os.listdir(json_file)   # 获取json文件列表
    # list=glob.glob(json_file+r'\\*.json')
    for i in range(0, len(list)):
        path = os.path.join(json_file, list[i])  # 获取每个json文件的绝对路径

        print(i,len(list),path)

        filename = list[i][:-5]       # 提取出.json前的字符作为文件名，以便后续保存Label图片的时候使用
        extension = list[i][-4:]
        if extension == 'json':
            if os.path.isfile(path):

                # data = json.load(open(path))
                f = open(path, encoding='utf-8')
                text = f.read()
                data = json.loads(text)

                # if data['imageData']:
                #     imageData = data['imageData']
                # else:
                #     imagePath = os.path.join(os.path.dirname(json_file), data['imagePath'])
                #     with open(imagePath, 'rb') as f:
                #         imageData = f.read()
                #         imageData = base64.b64encode(imageData).decode('utf-8')
                # img = img_b64_to_arr(imageData)

                img = img_b64_to_arr(data['imageData'])  # 根据'imageData'字段的字符可以得到原图像
                # lbl为label图片（标注的地方用类别名对应的数字来标，其他为0）lbl_names为label名和数字的对应关系字典
                lbl, lbl_names = labelme_shapes_to_label(img.shape, data['shapes'])   # data['shapes']是json文件中记录着标注的位置及label等信息的字段
                lbl=lbl.astype(np.uint8)
                #captions = ['%d: %s' % (l, name) for l, name in enumerate(lbl_names)]
                #lbl_viz = utils.draw.draw_label(lbl, img, captions)
                # out_dir = osp.basename(list[i])[:-5]+'_json'
                # out_dir = osp.join(osp.dirname(list[i]), out_dir)
                # if not osp.exists(out_dir):
                #     os.mkdir(out_dir)

                # ori_img=PIL.Image.fromarray(img)
                # ori_img.save('1.png')
                PIL.Image.fromarray(img).save(osp.join(image_folder, '{}.png'.format(filename)))
                PIL.Image.fromarray(lbl).save(osp.join(mask_folder, '{}.png'.format(filename)))
                #PIL.Image.fromarray(lbl_viz).save(osp.join(out_dir, '{}_viz.jpg'.format(filename)))

                # with open(osp.join(out_dir, 'label_names.txt'), 'w') as f:
                #     for lbl_name in lbl_names:
                #         f.write(lbl_name + '\n')
                #
                # warnings.warn('info.yaml is being replaced by label_names.txt')
                # info = dict(label_names=lbl_names)
                # with open(osp.join(out_dir, 'info.yaml'), 'w') as f:
                #     yaml.safe_dump(info, f, default_flow_style=False)

                # print('Saved to: %s' % out_dir)


if __name__ == '__main__':
    main()

