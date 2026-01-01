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
        if response.encoding:
            encoding = response.encoding
        else:
            encoding = response.apparent_encoding

        # Декодируем с правильной кодировкой
        return response.content.decode(encoding)
    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")
        return None


def parse_problem(html_content):
    """
    An important point! html code on the website problems.ru it has koi8-r encoding.
    This encoding is parsed according to completely different rules than typical utf-8.
    That's why I parsed it incorrectly. Then I completely rewrote the code.
    """
    # Убираем from_encoding, так как html_content уже декодирован
    soup = BeautifulSoup(html_content, "html.parser")

    # Вспомогательная функция для очистки текста
    def clean_text(text):
        if not text:
            return ""
        # Заменяем все неразрывные пробелы и управляющие символы
        text = re.sub(r"[\xa0\u00A0]", " ", text)  # \xa0 и его Unicode эквивалент
        text = re.sub(r"\s+", " ", text)  # Множественные пробелы в один
        return text.strip(";&nbsp;. \n\t\r")

    # Извлечение ID задачи - правильный путь
    header_div = soup.find("div", class_="componentboxheader")
    problem_id = None
    if header_div:
        # Ищем текст с номером задачи
        text = header_div.get_text(strip=True)
        match = re.search(r"Задача\s*(\d+)", text)
        if match:
            problem_id = int(match.group(1))

    # Извлечение темы - правильный путь
    topic = "unknown"
    # Ищем таблицу с темой
    subject_table = soup.find("table", class_="problemdetailssubjecttable")
    if subject_table:
        topic_link = subject_table.find(
            "a", href=re.compile(r"/view_by_subject_new\.php\?parent=\d+")
        )
        if topic_link:
            topic = clean_text(topic_link.get_text())

    # Извлечение условия
    problem_text = ""
    # Ищем заголовок "Условие" (регистр важен)
    for h3 in soup.find_all("h3"):
        if h3.get_text(strip=True) == "Условие":
            # Собираем весь текст до следующего h3
            next_element = h3.next_sibling
            while next_element and (not hasattr(next_element, "name") or next_element.name != "h3"):
                if hasattr(next_element, "get_text"):
                    problem_text += next_element.get_text() + " "
                next_element = next_element.next_sibling
            break

    # Извлечение решения
    solution_text = ""
    for h3 in soup.find_all("h3"):
        if "решение" in h3.get_text(strip=True).lower():
            next_element = h3.next_sibling
            while next_element and (not hasattr(next_element, "name") or next_element.name != "h3"):
                if hasattr(next_element, "get_text"):
                    solution_text += next_element.get_text() + " "
                next_element = next_element.next_sibling
            break

    # Извлечение ответа
    answer_text = ""
    for h3 in soup.find_all("h3"):
        if "ответ" in h3.get_text(strip=True).lower():
            next_element = h3.next_sibling
            while next_element and (not hasattr(next_element, "name") or next_element.name != "h3"):
                if hasattr(next_element, "get_text"):
                    answer_text += next_element.get_text() + " "
                next_element = next_element.next_sibling
            break

    # Альтернативный более простой подход для ответа
    if not answer_text:
        # Ищем параграф после заголовка "Ответ"
        answer_heading = soup.find("h3", string=lambda text: text and "ответ" in text.lower())
        if answer_heading:
            answer_paragraph = answer_heading.find_next("p")
            if answer_paragraph:
                answer_text = answer_paragraph.get_text()

    return {
        "id": problem_id,
        "topic": clean_text(topic),
        "problem": clean_text(problem_text),
        "solution": clean_text(solution_text),
        "answer": clean_text(answer_text),
    }


def save_to_json(data, filename="output.json"):
    """Сохранить данные в JSON-файл"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def parse_problem_from_url(url):
    """Полный процесс: загрузка, парсинг, сохранение"""
    html_content = fetch_html(url)
    if html_content:
        parsed_data = parse_problem(html_content)
        save_to_json(parsed_data)
        return parsed_data
    else:
        return None


# if __name__ == "__main__":
#     # Пример URL (замените на реальный)
#     problem_url = "https://problems.ru/view_problem_details_new.php?id=87981"

#     result = parse_problem_from_url(problem_url)

#     if result:
#         print("Успешно спарсены данные:")
#         print(json.dumps(result, ensure_ascii=False, indent=2))
#     else:
#         print("Не удалось спарсить данные.")
