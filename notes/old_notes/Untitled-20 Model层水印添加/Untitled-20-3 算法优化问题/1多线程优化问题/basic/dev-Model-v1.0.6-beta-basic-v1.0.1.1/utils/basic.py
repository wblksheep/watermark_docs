import io
import sys
import glob
import numpy as np
from PIL import Image
import os
import yaml
import logging
from multiprocessing import Pool, cpu_count
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    handlers=[logging.FileHandler("watermark.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
# logger = logging.getLogger(__name__)
# 读取图片文件
def load_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件 {image_path} 不存在")
    return Image.open(image_path)

# 读取npy文件
def load_npy(npy_path):
    if not os.path.exists(npy_path):
        raise FileNotFoundError(f"npy文件 {npy_path} 不存在")
    return np.load(npy_path)

def overlay_and_crop(base_image, npy_data):
    """叠加水印并裁剪"""
    # print(f"npy_data.shape = {npy_data.shape}")
    watermark_image = Image.fromarray(npy_data)
    # 获取图片和水印的尺寸
    base_width, base_height = base_image.size
    watermark_width, watermark_height = watermark_image.size

    # 裁剪水印超出图片的部分
    if watermark_width > base_width or watermark_height > base_height:
        watermark_image = watermark_image.crop((0, 0, base_width, base_height))

    # 将水印覆盖到图片的左上角
    base_image.paste(watermark_image, (0, 0), watermark_image)  # 使用alpha通道（如果存在）
    return base_image

def process_single_image(input_path, output_path, config, npy_data, quality=30):
    """处理单张图片"""
    try:
        # 加载并预处理图片
        base_image = load_image(input_path)
        # if base_image.mode != "RGBA":
        #     base_image = base_image.convert("RGBA")

        scale = config['output_height'] / base_image.height
        width = int(base_image.width * scale)
        base_image = base_image.resize((width, config['output_height']))
        if base_image.mode == "RGB":
            buffer = io.BytesIO()
            base_image.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            base_image = Image.open(buffer)
        else:
            # PNG 压缩（无损但有压缩级别）
            buffer = io.BytesIO()
            base_image.save(buffer, format="PNG", compress_level=7)  # 最高压缩级别
            buffer.seek(0)
            base_image = Image.open(buffer)
        # npy_data = npy_data.resize((config['output_height'], config['output_height']))
        np.resize(npy_data, (config['output_height'], config['output_height']))
        # 应用水印
        watermarked = overlay_and_crop(base_image, npy_data)


        if os.path.splitext(output_path)[1] in [".jpeg", ".jpg"]:
            watermarked = watermarked.convert("RGB")
        # watermarked = watermarked.convert("RGB")
        # 保存结果
        watermarked.save(output_path, quality=100)
        logger.info(f"Processed: {os.path.basename(input_path)}")
    except Exception as e:
        logger.exception(f"Error processing {input_path}: {str(e)}")
        raise



def generate_watermark(input_folder, watermark_type, opacity, quality):
    """批量生成水印"""
    # 加载配置
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)['watermark']

    # 初始化路径
    output_folder = os.path.join(input_folder, 'output')
    os.makedirs(output_folder, exist_ok=True)

    # 加载水印数据
    npy_path = f"{watermark_type}.npy"
    # npy_data = load_npy(npy_path) * (opacity/100.0)
    npy_data = load_npy(npy_path)


    # 获取图片文件列表
    supported_formats = ('*.jpg', '*.jpeg', '*.png')
    image_files = []
    for fmt in supported_formats:
        image_files.extend(glob.glob(os.path.join(input_folder, fmt), recursive=True))

    # for input_path in image_files:
    #     file_name = os.path.basename(input_path)
    #     output_path = os.path.join(output_folder, file_name)
    #     process_single_image_wrapper(input_path, output_path, config, npy_data, quality)
    # 批量处理
    with Pool(processes=cpu_count()) as pool:
        logger = logging.getLogger(__name__)
        pool.starmap(process_single_image_wrapper,
                     [(input_path, os.path.join(output_folder, os.path.basename(input_path)), config, npy_data,
                       quality)
                      for input_path in image_files])

def process_single_image_wrapper(*arg):
    return process_single_image(*arg)

if __name__ == "__main__":
    # 加载配置
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)['watermark']
    input_folder = config['input_folder']
    watermark_type = config['npy_path']
    opacity = float(config['opacity'])
    quality = int(config['quality'])

    # # 配置日志
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
    #     handlers=[logging.FileHandler("watermark.log"), logging.StreamHandler()]
    # )
    # logger = logging.getLogger(__name__)

    generate_watermark(input_folder, watermark_type, opacity, quality=quality)
