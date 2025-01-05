import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from paddleocr import PaddleOCR
import numpy as np
import re

ocr = PaddleOCR(use_angle_cls=True, lang='ch')

root = tk.Tk()
root.title("车牌识别")
root.geometry("1000x600")

image_path = ""

# 图像预处理函数
def preprocess_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"错误: 无法加载图像 {image_path}")

        # 转换为灰度图像
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 中值滤波去除噪声
        denoised = cv2.medianBlur(gray, 5)

        # 直方图均衡化增强对比
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(denoised)

        # 阈值化增强清晰度
        thresh = cv2.adaptiveThreshold(contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 11, 2)

        # 车牌区域检测（可选）：在识别前检测车牌区域，提高准确性
        # 可以选择性地加上车牌区域检测代码，进行ROI定位

        return thresh

    except Exception as e:
        raise RuntimeError(f"预处理失败: {e}")

# 上传图片并显示
def upload_image():
    global image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            img_tk = ImageTk.PhotoImage(img)
            image_label.config(image=img_tk)
            image_label.image = img_tk
            image_path = file_path
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")

# 显示预处理后的图像
def display_processed_image(processed_image):
    processed_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(processed_image_rgb)
    pil_image.thumbnail((400, 400))
    img_tk = ImageTk.PhotoImage(pil_image)
    processed_image_label.config(image=img_tk)
    processed_image_label.image = img_tk

# 识别车牌
def recognize_license_plate():
    if not image_path:
        messagebox.showwarning("警告", "请先上传图片")
        return

    try:
        # 图像预处理
        preprocessed_image = preprocess_image(image_path)

        # 显示预处理后的图像
        display_processed_image(preprocessed_image)

        # 使用PaddleOCR识别
        result = ocr.ocr(preprocessed_image, cls=True)

        # 处理OCR结果
        all_texts = []
        plate_numbers = []
        for line in result[0]:
            if isinstance(line[1], tuple) and isinstance(line[1][0], str):
                text = line[1][0]
                all_texts.append(text)

                # 匹配车牌号
                if re.match(r'[\u4e00-\u9fa5][A-Z].?[A-Z0-9]{4,6}[\u4e00-\u9fa5]?$', text):
                    plate_numbers.append(text)

        # 显示结果
        if plate_numbers:
            result_text = "识别的车牌号:\n" + "\n".join(plate_numbers)
        else:
            result_text = "未能识别到车牌号\n\n所有识别结果:\n" + "\n".join(all_texts)

        result_label.config(state='normal')
        result_label.delete(1.0, tk.END)
        result_label.insert(tk.END, result_text)
        result_label.config(state='disabled')

    except Exception as e:
        messagebox.showerror("错误", f"车牌识别失败: {e}")

# 创建界面
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True)

left_frame = tk.Frame(main_frame, width=500, bg="#f0f0f0")
left_frame.pack(side=tk.LEFT, padx=20, pady=20)

right_frame = tk.Frame(main_frame, width=500, bg="#f0f0f0")
right_frame.pack(side=tk.LEFT, padx=20, pady=20)

image_label = tk.Label(left_frame, bg="#f0f0f0")
image_label.pack(pady=20)

upload_button = tk.Button(right_frame, text="上传图片", command=upload_image, width=20, height=2, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief="flat", bd=0)
upload_button.pack(pady=10)

recognize_button = tk.Button(right_frame, text="识别车牌号", command=recognize_license_plate, width=20, height=2, bg="#FF5722", fg="white", font=("Arial", 12, "bold"), relief="flat", bd=0)
recognize_button.pack(pady=10)

processed_image_label = tk.Label(right_frame, bg="#f0f0f0")
processed_image_label.pack(pady=20)

result_label = tk.Text(right_frame, width=60, height=15, font=("Arial", 14), state='disabled', wrap='word', bd=2, relief="sunken", padx=10, pady=10)
result_label.pack(pady=20)

# 主循环
root.mainloop()
