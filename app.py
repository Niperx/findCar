from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def classify_by_dimensions(length, height):
    """Классифицирует автомобиль по габаритам согласно таблице"""
    length = int(length)
    height = int(height)

    # Малолитражка
    if length <= 3750 and height <= 1750:
        return "Малолитражка"

    # Куда (город)
    if 3751 <= length <= 4100 and height <= 1530:
        return "Городской автомобиль"

    # Кей-Кар
    if 4051 <= length <= 4550 and height <= 1550:
        return "Кей-Кар"

    # Седан
    if 4551 <= length <= 5000 and height <= 1550:
        return "Седан"

    # Длинный седан
    if 3900 <= length <= 4550 and 1551 <= height <= 1750:
        return "Длинный седан"

    # Кросс
    if 4551 <= length <= 4905 and 1551 <= height <= 1750:
        return "Кросс"

    # Длинный кросс
    if 4400 <= length <= 4750 and 1751 <= height <= 1900:
        return "Длинный кросс"

    # Джип
    if 4751 <= length <= 5050 and 1751 <= height <= 1900:
        return "Джип"

    # Длинный джип
    if 5051 <= length <= 5300 and 1700 <= height <= 1900:
        return "Длинный джип"

    # Большое авто
    if length > 5300 or height > 1900:
        return "Большое авто"

    # Если не попадает ни в одну категорию, пытаемся определить по отдельным параметрам
    if height > 1750:
        return "Внедорожник"
    elif length > 5000:
        return "Большой автомобиль"
    else:
        return "Легковой автомобиль"

def transliterate_to_url(brand, model):
    """Преобразует кириллицу в латиницу для URL"""
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    brand_lower = brand.lower().strip()
    model_lower = model.lower().strip()

    # Транслитерация
    brand_url = ''.join(translit_dict.get(c, c) for c in brand_lower)
    model_url = ''.join(translit_dict.get(c, c) for c in model_lower)

    # Замена пробелов на дефисы
    brand_url = brand_url.replace(' ', '-')
    model_url = model_url.replace(' ', '-')

    return brand_url, model_url

def scrape_drom_dimensions(brand, model):
    """Парсит габариты с сайта drom.ru"""
    try:
        # Формируем URL
        brand_url, model_url = transliterate_to_url(brand, model)
        url = f"https://www.drom.ru/catalog/{brand_url}/{model_url}/specs/dimensions/"

        # Выполняем запрос
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Парсим HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        dimensions = {}

        # Простой подход: ищем все ячейки td на странице
        all_cells = soup.find_all('td')

        for cell in all_cells:
            text = cell.get_text(strip=True)

            # Ищем габариты (формат: "XXXX x XXXX x XXXX")
            if not dimensions.get('length'):
                match = re.search(r'(\d{4})\s*[xх×]\s*(\d{4})\s*[xх×]\s*(\d{4})', text)
                if match:
                    dimensions['length'] = match.group(1)
                    dimensions['width'] = match.group(2)
                    dimensions['height'] = match.group(3)

                    # Попробуем найти массу в соседних ячейках
                    next_sibling = cell.find_next_sibling('td')
                    if next_sibling:
                        mass_text = next_sibling.get_text(strip=True)
                        mass_numbers = re.findall(r'\d+', mass_text)
                        if mass_numbers and len(mass_numbers[0]) >= 3:  # Масса обычно >= 100 кг
                            dimensions['weight'] = mass_numbers[0]

                    break

        # Классифицируем по габаритам, если они найдены
        if dimensions.get('length') and dimensions.get('height'):
            body_type = classify_by_dimensions(dimensions['length'], dimensions['height'])
            dimensions['body_type'] = body_type

        if dimensions:
            return {
                'success': True,
                'data': dimensions,
                'url': url
            }
        else:
            return {
                'success': False,
                'error': 'Не удалось найти габариты на странице. Проверьте правильность написания марки и модели (латиницей).'
            }

    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Ошибка при запросе к drom.ru. Возможно, такая модель не существует в каталоге.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка парсинга: {str(e)}'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    brand = data.get('brand', '').strip()
    model = data.get('model', '').strip()

    if not brand or not model:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать марку и модель'
        })

    result = scrape_drom_dimensions(brand, model)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
