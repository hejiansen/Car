import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from paddleocr import PaddleOCR
import re

# 初始化OCR实例
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 启用角度分类器来检测倾斜

# 省份简称列表
province_codes = ["京", "沪", "津", "渝", "冀", "晋", "蒙", "辽", "吉", "黑", "苏", "浙", "皖", "闽",
                  "赣", "鲁", "豫", "鄂", "湘", "粤", "桂", "琼", "川", "贵", "云", "藏", "陕", "甘",
                  "青", "宁", "新"]


def detect_plate_area(img):
    """
    使用OCR检测车牌区域，返回车牌的矩形坐标。
    """
    result = ocr.ocr(img, cls=True)
    boxes = [elements[0] for elements in result[0]]  # 获取每个文本框的坐标
    txts = [elements[1][0] for elements in result[0]]  # 获取每个文本框的文本内容

    # 提取字符并去掉可信度分数（我们只关心字符）
    filtered_txts = []
    for txt in txts:
        # 使用正则表达式过滤掉车牌中的无关符号
        cleaned_txt = re.sub(r'[^\w\s]', '', txt)  # 只保留字母和数字
        filtered_txts.append(cleaned_txt)

    # 只保留以省份简称开头的车牌号码
    valid_plate_numbers = []
    for line in filtered_txts:
        if line[:1] in province_codes:  # 如果车牌以省份简称开头
            valid_plate_numbers.append(line)

    if valid_plate_numbers:
        # 假设车牌区域就是第一个有效车牌区域
        plate_box = boxes[0]  # 获取车牌区域的坐标点
        # 获取最小矩形框的左上角坐标和宽高
        x_min = min([point[0] for point in plate_box])
        y_min = min([point[1] for point in plate_box])
        x_max = max([point[0] for point in plate_box])
        y_max = max([point[1] for point in plate_box])

        # 返回车牌区域的矩形边界
        return int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)
    return None


def open_image():
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if not file_path:
        return

    # 读取图片
    img = cv2.imread(file_path)
    if img is None:
        # 如果无法读取图片，将错误信息显示在界面上
        result_label.config(text="无法读取图片", font=("Arial", 16))
        return

    # 使用OCR检测车牌区域
    plate_area = detect_plate_area(img)
    if plate_area is None:
        result_label.config(text="未检测到车牌", font=("Arial", 16))
        return

    # 进行文字识别
    result = ocr.ocr(img, cls=True)

    # 提取文本框坐标和文本内容
    boxes = [elements[0] for elements in result[0]]  # 获取每个文本框的坐标
    txts = [elements[1][0] for elements in result[0]]  # 获取每个文本框的文本内容

    # 提取字符并去掉可信度分数（我们只关心字符）
    filtered_txts = []
    for txt in txts:
        # 使用正则表达式过滤掉车牌中的无关符号
        cleaned_txt = re.sub(r'[^\w\s]', '', txt)  # 只保留字母和数字
        filtered_txts.append(cleaned_txt)

    # 只保留以省份简称开头的车牌号码
    valid_plate_numbers = []
    for line in filtered_txts:
        if line[:1] in province_codes:  # 如果车牌以省份简称开头
            valid_plate_numbers.append(line)

    # 更新界面显示车牌识别结果（以列表形式展示）
    if valid_plate_numbers:
        formatted_plate_number = valid_plate_numbers[0]  # 取第一个有效车牌号
        plate_list = list(formatted_plate_number)  # 将车牌号转为字符列表
        result_label.config(text="车牌识别结果：")  # 设置标题
        plate_details_label.config(text=f"{str(plate_list)}")  # 设置车牌号码显示
    else:
        result_label.config(text="车牌识别结果：")
        plate_details_label.config(text="未识别到有效车牌")

    # 将图片转换为tkinter格式并显示，统一调整尺寸
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV读取的是BGR格式，需要转为RGB格式
    img_pil = Image.fromarray(img_rgb)

    # 设置图片尺寸为适中的统一尺寸（例如，宽度为400px）
    img_pil = img_pil.resize((400, int(img_pil.height * 400 / img_pil.width)))  # 按比例调整高度

    img_tk = ImageTk.PhotoImage(img_pil)

    image_label.config(image=img_tk)
    image_label.image = img_tk  # 保持引用


# 创建主窗口
root = tk.Tk()
root.title("车牌识别器")

# 设置窗口大小为700x700
root.geometry("700x700")

# 创建主框架，确保元素居中
main_frame = tk.Frame(root)
main_frame.pack(expand=True)  # 使用pack的expand来填充整个窗口

# 使用grid布局，确保按钮和车牌识别结果居中
main_frame.grid_rowconfigure(0, weight=1)  # 使得第0行可以扩展
main_frame.grid_columnconfigure(0, weight=1)  # 使得第0列可以扩展

# 创建界面元素
image_label = tk.Label(main_frame)
image_label.grid(row=0, column=0, pady=10)  # 图片标签位于第0行第0列

# 修改按钮和结果标签的位置
result_label = tk.Label(main_frame, text="车牌识别结果：", font=("Arial", 14))
result_label.grid(row=1, column=0, pady=10)  # 结果标签位于第1行第0列

# 新增一个标签显示车牌号码
plate_details_label = tk.Label(main_frame, text="", font=("Arial", 14))
plate_details_label.grid(row=2, column=0, pady=10)

# 修改按钮位置
open_button = tk.Button(main_frame, text="选择图片", command=open_image, font=("Arial", 14), width=20, height=2)
open_button.grid(row=3, column=0, pady=20)  # 按钮位于第3行第0列，下面有间距

# 启动主循环
root.mainloop()

