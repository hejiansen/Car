import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from paddleocr import PaddleOCR
import re  # 用于正则表达式匹配车牌号

# 初始化PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # use_angle_cls=True表示启用方向分类器，lang='ch'表示中文车牌识别

# 创建窗口
root = tk.Tk()
root.title("车牌识别")
root.geometry("600x700")  # 调整界面大小


# 上传图片并显示
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        try:
            # 使用PIL打开图像文件
            img = Image.open(file_path)
            img.thumbnail((400, 400))  # 缩放图像
            img_tk = ImageTk.PhotoImage(img)

            # 在界面中显示图片
            image_label.config(image=img_tk)
            image_label.image = img_tk  # 保持对图像的引用
            # 保存图片路径
            global image_path
            image_path = file_path

        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")


# 识别车牌
def recognize_license_plate():
    if not image_path:
        messagebox.showwarning("警告", "请先上传图片")
        return

    # 使用PaddleOCR进行车牌识别
    result = ocr.ocr(image_path, cls=True)

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
            if re.match(r'^[\u4e00-\u9fa5][A-Z0-9]{5,6}•?[A-Z0-9]{1}$', text):
                plate_numbers.append(text)

    # 显示车牌号或者未识别到的信息
    if plate_numbers:
        result_text = "识别的车牌号:\n" + "\n".join(plate_numbers)
    else:
        result_text = "未能识别到车牌号\n\n所有OCR识别结果:\n" + "\n".join(all_texts)

    result_label.config(state='normal')  # 允许更新文本框内容
    result_label.delete(1.0, tk.END)  # 清空文本框内容
    result_label.insert(tk.END, result_text)  # 插入识别结果
    result_label.config(state='disabled')  # 禁止编辑文本框内容


# 设置界面组件
image_label = tk.Label(root)
image_label.pack(pady=20)

upload_button = tk.Button(root, text="上传图片", command=upload_image, width=20)
upload_button.pack(pady=10)

recognize_button = tk.Button(root, text="识别车牌号", command=recognize_license_plate, width=20)
recognize_button.pack(pady=10)

# 使用Text组件显示多个车牌号或调试结果
result_label = tk.Text(root, width=60, height=15, font=("Arial", 14), state='disabled', wrap='word')
result_label.pack(pady=20)

# 初始化全局变量
image_path = ""

# 运行Tkinter主循环
root.mainloop()
