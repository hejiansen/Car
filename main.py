import cv2
import pytesseract
from PIL import Image
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 载入图片
image_path = r"C:\Users\86189\PycharmProjects\car\image\1.jpg"
img = cv2.imread(image_path)

# 转为灰度图
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 使用二值化提高对比度
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# 将处理后的图片转换为PIL对象
pil_img = Image.fromarray(binary)

# 使用Tesseract识别文本
text = pytesseract.image_to_string(pil_img, lang='chi_sim+eng')

print(text)
