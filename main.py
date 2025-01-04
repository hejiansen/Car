import cv2
import pytesseract
from PIL import Image

# 设置Tesseract的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 根据你的安装路径修改


def recognize_license_plate(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用阈值化以提高识别效果
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 使用PIL库将图像转换为PIL图像
    pil_image = Image.fromarray(thresh)

    # 使用pytesseract进行OCR识别
    text = pytesseract.image_to_string(pil_image, lang='eng')

    # 打印识别结果
    print("识别的车牌号是:", text.strip())


# 调用函数
image_path = 'path_to_your_image.jpg'  # 替换为你的图片路径
recognize_license_plate(image_path)