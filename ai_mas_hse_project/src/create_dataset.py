import requests
from bs4 import BeautifulSoup
import json
import re


def fetch_html(url):
    """Получить HTML-содержимое по указанному URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Проверить, нет ли HTTP-ошибок

        # Определяем кодировку
        encoding = response.encoding or response.apparent_encoding

        # Декодируем с правильной кодировкой
        return response.content.decode(encoding)
    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")
        return None


def parse_problem(html_content, main_topic):
    """
    Парсинг задачи с сайта problems.ru
    """
    soup = BeautifulSoup(html_content, "html.parser")

    def clean_text(text):
        """Очистка текста от неразрывных пробелов и лишних пробелов"""
        if not text:
            return ""
        # Заменяем \xa0 на обычные пробелы
        text = re.sub(r"[\xa0\u00A0]", " ", text)
        # Убираем лишние пробелы
        text = " ".join(text.split())
        return text.strip(";&nbsp;. \n\t\r")

    result = {
        "id": None,
        "topic": main_topic,
        "subtopic": "unknown",
        "complexity_level": None,  # Новое поле для сложности
        "problem": "",
        "solution": "",
        "answer": "",
    }

    # 1. ID задачи
    header_div = soup.find("div", class_="componentboxheader")
    if header_div:
        text = header_div.get_text(strip=True)
        match = re.search(r"Задача\s*(\d+)", text)
        if match:
            result["id"] = int(match.group(1))

    # 2. Тема
    subject_table = soup.find("table", class_="problemdetailssubjecttable")
    if subject_table:
        topic_link = subject_table.find(
            "a", href=re.compile(r"/view_by_subject_new\.php\?parent=\d+")
        )
        if topic_link:
            result["subtopic"] = clean_text(topic_link.get_text())

    # 3. Сложность задачи (НОВОЕ ПОЛЕ)
    # Ищем блок со сложностью
    difficulty_cell = soup.find("td", class_="problemdetailsdifficulty")
    if difficulty_cell:
        # Ищем текст со сложностью
        difficulty_text = difficulty_cell.get_text(strip=True)

        # Ищем паттерн "Сложность: X" где X может быть "2-", "3+", "4" и т.д.
        complexity_match = re.search(r"Сложность:\s*([\d\+\-]+)", difficulty_text)
        if complexity_match:
            result["complexity_level"] = complexity_match.group(1)
        else:
            # Альтернативный поиск если паттерн не найден
            lines = difficulty_text.split("\n")
            for line in lines:
                if "Сложность:" in line:
                    # Извлекаем значение после "Сложность:"
                    parts = line.split("Сложность:")
                    if len(parts) > 1:
                        result["complexity_level"] = clean_text(parts[1])
                    break

    # 4. Классы (опционально, можно добавить если нужно)
    if difficulty_cell:
        # Ищем классы
        classes_match = re.search(r"Классы:\s*([\d,]+)", difficulty_cell.get_text(strip=True))
        if classes_match:
            # Можно добавить в результат если нужно
            classes_str = classes_match.group(1)
            # result["classes"] = [int(c.strip()) for c in classes_str.split(',')]
            pass

    # 5. Условие
    for h3 in soup.find_all("h3"):
        if h3.get_text(strip=True) == "Условие":
            next_element = h3.next_sibling
            while next_element and (not hasattr(next_element, "name") or next_element.name != "h3"):
                if hasattr(next_element, "get_text"):
                    result["problem"] += next_element.get_text() + " "
                next_element = next_element.next_sibling
            break

    # 6. Решение
    for h3 in soup.find_all("h3"):
        if "решение" in h3.get_text(strip=True).lower():
            next_element = h3.next_sibling
            while next_element and (not hasattr(next_element, "name") or next_element.name != "h3"):
                if hasattr(next_element, "get_text"):
                    result["solution"] += next_element.get_text() + " "
                next_element = next_element.next_sibling
            break

    # 7. Ответ
    for h3 in soup.find_all("h3"):
        if "ответ" in h3.get_text(strip=True).lower():
            next_element = h3.next_sibling
            while next_element and (not hasattr(next_element, "name") or next_element.name != "h3"):
                if hasattr(next_element, "get_text"):
                    result["answer"] += next_element.get_text() + " "
                next_element = next_element.next_sibling
            break

    # Очищаем все текстовые поля
    for field in ["subtopic", "problem", "solution", "answer"]:
        result[field] = clean_text(result[field])

    return result


def save_to_json(data, filename="output.json"):
    """Сохранить данные в JSON-файл"""
    from pathlib import Path

    Path(filename).write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")


def parse_problem_from_url(url):
    """Полный процесс: загрузка, парсинг, сохранение"""
    html_content = fetch_html(url)
    if html_content:
        parsed_data = parse_problem(html_content)
        save_to_json(parsed_data)
        return parsed_data
    return None


def parse_problem_from_file(filename="test.html", main_topic="algebra", encoding="utf-8"):
    """Парсинг задачи из локального HTML-файла"""
    try:
        with open(filename, "r", encoding=encoding) as f:
            html_content = f.read()

        parsed_data = parse_problem(html_content, main_topic=main_topic)

        # Сохраняем результат
        save_to_json(parsed_data, "output_from_file.json")

        return parsed_data
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return None
