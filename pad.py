import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from paddleocr import PaddleOCR
import re  # 用于正则表达式匹配车牌号

# 初始化PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # use_angle_cls=True表示启用方向分类器，lang='ch'表示中文车牌识别

# 创建窗口
root = tk.Tk()
root.title("车牌识别")
root.geometry("1000x600")  # 调整窗口大小

# 初始化全局变量
image_path = ""

# 图像预处理函数
def preprocess_image(image_path):
    # 读取图像
    img = cv2.imread(image_path)

    # 检查图像是否加载成功
    if img is None:
        raise ValueError(f"错误: 无法加载图像 {image_path}")

    # 转换为灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 去噪：使用高斯滤波去除噪声
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)

    # 提升对比度：自适应直方图均衡化
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(denoised)

    # 自适应阈值：处理不同光照条件下的车牌
    morph = cv2.adaptiveThreshold(contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return morph

# 上传图片并显示
def upload_image():
    global image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        try:
            # 使用PIL打开图像文件
            img = Image.open(file_path)
            img.thumbnail((400, 400))  # 缩放图像，最大尺寸为400x400
            img_tk = ImageTk.PhotoImage(img)

            # 在界面中显示图片
            image_label.config(image=img_tk)
            image_label.image = img_tk  # 保持对图像的引用
            # 保存图片路径
            image_path = file_path

        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")

# 显示预处理后的图像
def display_processed_image(processed_image):
    # 将OpenCV图像（BGR格式）转换为RGB格式，以便在Tkinter中显示
    processed_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)

    # 将NumPy数组转换为PIL图像
    pil_image = Image.fromarray(processed_image_rgb)

    # 设置预处理图像的最大显示尺寸
    pil_image.thumbnail((400, 400))  # 最大尺寸为400x400

    # 将PIL图像转换为Tkinter兼容的格式
    img_tk = ImageTk.PhotoImage(pil_image)

    # 在界面中显示预处理后的图像
    processed_image_label.config(image=img_tk)
    processed_image_label.image = img_tk  # 保持对图像的引用

# 识别车牌
def recognize_license_plate():
    if not image_path:
        messagebox.showwarning("警告", "请先上传图片")
        return

    try:
        # 先进行图像预处理
        preprocessed_image = preprocess_image(image_path)

        # 显示预处理后的图像
        display_processed_image(preprocessed_image)

        # 使用PaddleOCR进行车牌识别
        result = ocr.ocr(preprocessed_image, cls=True)

        # 输出OCR识别结果
        print("完整OCR识别结果：")
        for line in result[0]:
            print(line[1])  # 打印每行识别到的文本

        # 将所有识别结果显示到界面上
        all_texts = []
        plate_numbers = []
        for line in result[0]:
            if isinstance(line[1], tuple) and isinstance(line[1][0], str):
                text = line[1][0]  # 提取文本
                all_texts.append(text)  # 收集所有识别到的文本

                # 正则表达式匹配车牌号
                # 支持普通车牌和新能源车牌号（带点）
                if re.match(r'[\u4e00-\u9fa5][A-Z].?[A-Z0-9]{4,6}[\u4e00-\u9fa5]?$', text):
                    plate_numbers.append(text)

        # 显示车牌号或者未识别到的信息
        if plate_numbers:
            result_text = "识别的车牌号:\n" + "\n".join(plate_numbers)
        else:
            result_text = "未能识别到车牌号\n\n所有识别结果:\n" + "\n".join(all_texts)

        result_label.config(state='normal')  # 允许更新文本框内容
        result_label.delete(1.0, tk.END)  # 清空文本框内容
        result_label.insert(tk.END, result_text)  # 插入识别结果
        result_label.config(state='disabled')  # 禁止编辑文本框内容

    except Exception as e:
        messagebox.showerror("错误", f"车牌识别失败: {e}")

# 创建主框架（左侧和右侧布局）
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True)

# 左侧框架：用于显示上传的图片
left_frame = tk.Frame(main_frame, width=500, bg="#f0f0f0")
left_frame.pack(side=tk.LEFT, padx=20, pady=20)

# 右侧框架：用于显示按钮、预处理图片和结果
right_frame = tk.Frame(main_frame, width=500, bg="#f0f0f0")
right_frame.pack(side=tk.LEFT, padx=20, pady=20)

# 左侧图片显示标签
image_label = tk.Label(left_frame, bg="#f0f0f0")
image_label.pack(pady=20)

# 右侧上传和识别按钮
upload_button = tk.Button(right_frame, text="上传图片", command=upload_image, width=20, height=2, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief="flat", bd=0)
upload_button.pack(pady=10)

recognize_button = tk.Button(right_frame, text="识别车牌号", command=recognize_license_plate, width=20, height=2, bg="#FF5722", fg="white", font=("Arial", 12, "bold"), relief="flat", bd=0)
recognize_button.pack(pady=10)

# 右侧显示预处理后图像的标签
processed_image_label = tk.Label(right_frame, bg="#f0f0f0")
processed_image_label.pack(pady=20)

# 使用Text组件显示多个车牌号或调试结果
result_label = tk.Text(right_frame, width=60, height=15, font=("Arial", 14), state='disabled', wrap='word', bd=2, relief="sunken", padx=10, pady=10)
result_label.pack(pady=20)

# 运行Tkinter主循环
root.mainloop()
