import cv2
import pytesseract
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import re

# 配置 Tesseract 路径（根据你的安装路径进行修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\迅雷下载\tesseract-ocr-w64-setup-5.5.0.20241111.exe'

# 省份简称列表
province_codes = ["京", "沪", "津", "渝", "冀", "晋", "蒙", "辽", "吉", "黑", "苏", "浙", "皖", "闽",
                  "赣", "鲁", "豫", "鄂", "湘", "粤", "桂", "琼", "川", "贵", "云", "藏", "陕", "甘",
                  "青", "宁", "新"]


def preprocess_image(img):
    """
    图像预处理：灰度化、边缘检测
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200)
    return edges


def find_plate_contour(img):
    """
    使用轮廓检测找到车牌区域
    """
    edges = preprocess_image(img)

    # 找到轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # 获取边界框
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h

        # 车牌通常是宽而扁的矩形
        if 2 < aspect_ratio < 6 and 1000 < w * h < 30000:
            plate_img = img[y:y + h, x:x + w]
            return plate_img
    return None


def recognize_plate(img):
    """
    识别车牌号
    """
    # 车牌定位
    plate_img = find_plate_contour(img)
    if plate_img is None:
        return "未检测到车牌"

    # 进一步处理车牌区域
    gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    _, thresh_plate = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 使用 Tesseract OCR 识别
    ocr_result = pytesseract.image_to_string(thresh_plate, config='--psm 7')

    # 使用正则表达式提取车牌号
    plate_pattern = r'[京沪津渝冀晋蒙辽吉黑苏浙皖闽赣鲁豫鄂湘粤桂琼川贵云藏陕甘青宁新][A-Z][A-Z0-9]{5,7}'
    matches = re.findall(plate_pattern, ocr_result)

    if matches:
        return matches[0]
    else:
        return "未能识别到车牌号"


def open_image():
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if not file_path:
        return

    # 读取图片
    img = cv2.imread(file_path)
    if img is None:
        result_label.config(text="无法读取图片", font=("Arial", 16))
        return

    # 识别车牌
    plate_number = recognize_plate(img)
    result_label.config(text=f"车牌识别结果：{plate_number}", font=("Arial", 16))

    # 显示图片
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil = img_pil.resize((400, int(img_pil.height * 400 / img_pil.width)))
    img_tk = ImageTk.PhotoImage(img_pil)

    image_label.config(image=img_tk)
    image_label.image = img_tk


# 创建主窗口
root = tk.Tk()
root.title("车牌识别器")
root.geometry("700x700")

# 创建界面元素
image_label = tk.Label(root)
image_label.pack(pady=10)

result_label = tk.Label(root, text="车牌识别结果：", font=("Arial", 16))
result_label.pack(pady=10)

open_button = tk.Button(root, text="选择图片", command=open_image, font=("Arial", 14), width=20, height=2)
open_button.pack(pady=20)

# 启动主循环
root.mainloop()
