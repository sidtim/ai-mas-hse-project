import requests
from bs4 import BeautifulSoup
import json
import re
import time
from tqdm import tqdm
from pathlib import Path
import random


def fetch_html(url, retries=3, timeout=10):
    """Получить HTML-содержимое по указанному URL с повторными попытками"""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            # Определяем кодировку
            encoding = response.encoding or response.apparent_encoding

            # Декодируем с правильной кодировкой
            return response.content.decode(encoding)
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                print(f"Ошибка при загрузке страницы {url}: {e}")
                return None
            time.sleep(2**attempt)  # Экспоненциальная задержка
    return None


def parse_problem(html_content, problem_id=None):
    """
    Парсинг задачи с сайта problems.ru
    """
    if not html_content:
        return None

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
        "id": problem_id,
        "topic": "unknown",
        "complexity_level": None,
        "problem": "",
        "solution": "",
        "answer": "",
        "url": f"https://problems.ru/view_problem_details_new.php?id={problem_id}"
        if problem_id
        else None,
    }

    # 1. ID задачи (если не передан)
    if not problem_id:
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
            result["topic"] = clean_text(topic_link.get_text())

    # 3. Сложность задачи
    difficulty_cell = soup.find("td", class_="problemdetailsdifficulty")
    if difficulty_cell:
        difficulty_text = difficulty_cell.get_text(strip=True)
        complexity_match = re.search(r"Сложность:\s*([\d\+\-]+)", difficulty_text)
        if complexity_match:
            result["complexity_level"] = complexity_match.group(1)

    # 4. Классы (опционально)
    if difficulty_cell:
        classes_match = re.search(r"Классы:\s*([\d,]+)", difficulty_cell.get_text(strip=True))
        if classes_match:
            result["classes"] = classes_match.group(1)

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
    for field in ["topic", "problem", "solution", "answer"]:
        result[field] = clean_text(result[field])

    # Проверяем, что задача действительно существует (есть хотя бы условие)
    if not result["problem"] and not result["id"]:
        return None

    return result


def save_problems_to_json(problems, filename="all_problems.json"):
    """Сохранить список задач в JSON файл"""
    Path(filename).write_text(
        json.dumps(problems, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Сохранено {len(problems)} задач в файл {filename}")


def load_existing_problems(filename="all_problems.json"):
    """Загрузить уже спарсенные задачи"""
    if Path(filename).exists():
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def scrape_all_problems(
    start_id=1,
    end_id=100000,
    batch_size=1000,
    output_file="all_problems.json",
    resume=True,
    delay=0.5,
):
    """
    Парсинг всех задач в указанном диапазоне ID

    Args:
        start_id (int): Начальный ID задачи
        end_id (int): Конечный ID задачи
        batch_size (int): Размер батча для сохранения
        output_file (str): Имя выходного файла
        resume (bool): Продолжить с места остановки
        delay (float): Задержка между запросами (секунды)
    """

    # Загружаем уже спарсенные задачи
    all_problems = []
    if resume and Path(output_file).exists():
        all_problems = load_existing_problems(output_file)
        parsed_ids = {p["id"] for p in all_problems if "id" in p}
        print(f"Загружено {len(all_problems)} задач из файла")
    else:
        parsed_ids = set()

    # Создаем словарь для быстрого доступа по ID
    problems_dict = {p["id"]: p for p in all_problems if "id" in p}

    # Определяем начальный ID для парсинга
    if resume and parsed_ids:
        current_start = max(parsed_ids) + 1
    else:
        current_start = start_id

    print(f"Начинаем парсинг с ID {current_start} до {end_id}")

    # Статистика
    stats = {"success": 0, "failed": 0, "skipped": 0, "total": end_id - current_start + 1}

    # Прогресс-бар
    with tqdm(total=stats["total"], desc="Парсинг задач") as pbar:
        for problem_id in range(current_start, end_id + 1):
            # Пропускаем уже спарсенные
            if problem_id in parsed_ids:
                stats["skipped"] += 1
                pbar.update(1)
                continue

            # Формируем URL
            url = f"https://problems.ru/view_problem_details_new.php?id={problem_id}"

            # Загружаем HTML
            html_content = fetch_html(url)

            # Парсим задачу
            if html_content:
                problem_data = parse_problem(html_content, problem_id)

                if problem_data:
                    problems_dict[problem_id] = problem_data
                    stats["success"] += 1

                    # Сохраняем каждые batch_size задач
                    if stats["success"] % batch_size == 0:
                        save_problems_to_json(list(problems_dict.values()), output_file)
                        print(f"Промежуточное сохранение после {stats['success']} задач")
                else:
                    stats["failed"] += 1
            else:
                stats["failed"] += 1

            # Обновляем прогресс-бар
            pbar.update(1)
            pbar.set_postfix(
                {
                    "Успешно": stats["success"],
                    "Провалено": stats["failed"],
                    "Пропущено": stats["skipped"],
                }
            )

            # Задержка для избежания блокировки
            if delay > 0:
                time.sleep(delay + random.uniform(0, 0.3))  # Случайная задержка

    # Финальное сохранение
    save_problems_to_json(list(problems_dict.values()), output_file)

    # Вывод статистики
    print("\n" + "=" * 50)
    print("СТАТИСТИКА ПАРСИНГА:")
    print(f"Всего обработано: {stats['total']}")
    print(f"Успешно спарсено: {stats['success']}")
    print(f"Провалено: {stats['failed']}")
    print(f"Пропущено (уже было): {stats['skipped']}")
    print(f"Эффективность: {(stats['success'] / stats['total']) * 100:.1f}%")
    print("=" * 50)

    return list(problems_dict.values())


def analyze_problems(filename="all_problems.json"):
    """Анализ спарсенных задач"""
    if not Path(filename).exists():
        print(f"Файл {filename} не найден")
        return

    problems = load_existing_problems(filename)

    print(f"Всего задач: {len(problems)}")

    # Статистика по сложности
    complexity_stats = {}
    for p in problems:
        comp = p.get("complexity_level", "Не указана")
        complexity_stats[comp] = complexity_stats.get(comp, 0) + 1

    print("\nСтатистика по сложности:")
    for comp, count in sorted(complexity_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {comp}: {count}")

    # Статистика по темам
    topic_stats = {}
    for p in problems:
        topic = p.get("topic", "Не указана")
        topic_stats[topic] = topic_stats.get(topic, 0) + 1

    print(f"\nВсего уникальных тем: {len(topic_stats)}")
    print("\nТоп-10 популярных тем:")
    for topic, count in sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {topic}: {count}")


def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Парсинг задач с problems.ru")
    parser.add_argument("--start", type=int, default=1, help="Начальный ID задачи")
    parser.add_argument("--end", type=int, default=100000, help="Конечный ID задачи")
    parser.add_argument("--batch", type=int, default=1000, help="Размер батча для сохранения")
    parser.add_argument("--output", type=str, default="all_problems.json", help="Выходной файл")
    parser.add_argument("--delay", type=float, default=0.5, help="Задержка между запросами")
    parser.add_argument("--no-resume", action="store_true", help="Не продолжать с места остановки")
    parser.add_argument("--analyze", action="store_true", help="Только анализ существующего файла")

    args = parser.parse_args()

    if args.analyze:
        analyze_problems(args.output)
    else:
        scrape_all_problems(
            start_id=args.start,
            end_id=args.end,
            batch_size=args.batch,
            output_file=args.output,
            resume=not args.no_resume,
            delay=args.delay,
        )


# if __name__ == "__main__":
#     main()
