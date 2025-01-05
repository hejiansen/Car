import cv2
import pytesseract
import numpy as np
import re
import os

# 配置 tesseract 路径 (如果你是在 Windows 上使用，需要指定 tesseract.exe 的路径)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 车牌识别函数
def recognize_license_plate(image_path, preprocessed_path='preprocessed_image.jpg'):
    try:
        # 检查文件是否存在
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"错误: 图像文件 {image_path} 不存在")

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
        thresh = cv2.adaptiveThreshold(contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # 形态学操作：膨胀和腐蚀
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 边缘检测：Canny算法
        edges = cv2.Canny(morph, 100, 200)

        # 寻找图像中的轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 筛选出车牌区域（假设车牌为矩形且符合宽高比）
        license_plate_contour = None
        for contour in contours:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) == 4:  # 车牌为矩形，选择四个点的轮廓
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / h
                if 2 < aspect_ratio < 6:  # 宽高比在合理范围内（一般车牌长宽比在 2 到 6 之间）
                    license_plate_contour = approx
                    break

        # 保存预处理后的图像
        cv2.imwrite(preprocessed_path, thresh)

        if license_plate_contour is not None:
            # 提取车牌区域
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [license_plate_contour], -1, 255, thickness=cv2.FILLED)
            masked_image = cv2.bitwise_and(img, img, mask=mask)

            # 裁剪车牌区域
            x, y, w, h = cv2.boundingRect(license_plate_contour)
            license_plate_image = masked_image[y:y+h, x:x+w]

            # 保存裁剪出的车牌区域（用于调试）
            cropped_plate_path = 'cropped_license_plate.jpg'
            cv2.imwrite(cropped_plate_path, license_plate_image)

            # 使用Tesseract识别车牌号
            text = pytesseract.image_to_string(license_plate_image, config='--psm 8')

            # 使用正则表达式清理和提取车牌号
            license_plate_number = re.sub(r'[\u4e00-\u9fa5][A-Z].?[A-Z0-9]{4,6}[\u4e00-\u9fa5]?', '', text).strip()

            return license_plate_number

        return "未检测到车牌"

    except Exception as e:
        print(f"发生错误: {e}")
        return None

# 测试
image_path = r'C:\Users\86189\PycharmProjects\car\image\1.jpg'  # 替换为实际的图片路径
preprocessed_path = r'C:\Users\86189\PycharmProjects\car\image\new.jpg'  # 保存预处理图像的路径
license_plate = recognize_license_plate(image_path, preprocessed_path)

# 输出识别结果
if license_plate:
    print("识别的车牌号:", license_plate)
else:
    print("车牌识别失败")
