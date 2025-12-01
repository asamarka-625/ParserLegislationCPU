# Внешние зависимости
import pytesseract
from PIL import Image
import fitz
import io


# Извлекает текст из байт-кода PDF используя OCR
def extract_text_from_pdf_bytes(pdf_bytes):
    # Открываем PDF из байтов
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)

        # Получаем изображение страницы с высоким качеством
        mat = fitz.Matrix(300 / 72, 300 / 72)  # 300 DPI
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")

        # Конвертируем в PIL Image
        image = Image.open(io.BytesIO(img_data))

        # Применяем OCR
        text = pytesseract.image_to_string(image, lang='rus+eng')
        full_text += text + "\n\n"

    pdf_document.close()
    return full_text.strip()