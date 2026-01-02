import re
import json
from bs4 import BeautifulSoup


def parse_problems(file_path):
    with open(file_path, "r", encoding="koi8-r") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Находим все задачи по якорям
    problem_anchors = soup.find_all("a", {"name": lambda x: x and x.startswith("problem_")})

    parsed_problems = []

    for anchor in problem_anchors:
        problem_id = anchor["name"].replace("problem_", "")
        print(f"\nОбрабатываем задачу {problem_id}...")

        # Находим родительский контейнер задачи (от текущего anchor до следующего hr)
        problem_section = []
        current = anchor

        while current and current.name != "hr":
            problem_section.append(str(current))
            current = current.find_next()
            if current and current.name == "a" and current.get("name", "").startswith("problem_"):
                break

        section_html = "".join(problem_section)
        section_soup = BeautifulSoup(section_html, "html.parser")

        # Проверяем изображения
        all_images = section_soup.find_all("img")
        has_forbidden_images = False

        for img in all_images:
            src = img.get("src", "")
            if src != "images/into_basket.gif":
                has_forbidden_images = True
                print(f"  Найдено запрещенное изображение: {src}")
                break

        if has_forbidden_images:
            print(f"  Пропускаем задачу {problem_id}: содержит запрещенные изображения")
            continue

        # Ищем условие задачи
        problem_text = ""
        # Берем первый непустой параграф после таблицы с заголовком
        problem_table = section_soup.find("table", class_="problemsmallcaptiontable")

        if problem_table:
            # Ищем все параграфы после таблицы
            current = problem_table.find_next("p")
            while current and current.name == "p":
                text_content = current.get_text(strip=True)
                if text_content and "Автор:" not in text_content:
                    problem_text += str(current)
                current = current.find_next("p")

        if not problem_text.strip():
            print(f"  Пропускаем задачу {problem_id}: нет условия задачи")
            continue

        # Ищем решение
        solution_text = ""
        # Ищем h3 с текстом "Решение"
        for h3 in section_soup.find_all("h3"):
            if h3.get_text(strip=True) == "Решение":
                # Берем следующий параграф
                next_p = h3.find_next("p")
                while next_p and next_p.name == "p":
                    solution_text += str(next_p)
                    next_p = next_p.find_next("p")
                break

        # ИЩЕМ ОТВЕТ - ГЛАВНАЯ ЗАДАЧА
        answer_text = ""
        # Ищем h3 с текстом "Ответ"
        for h3 in section_soup.find_all("h3"):
            if h3.get_text(strip=True) == "Ответ":
                # Берем следующий непустой параграф после h3
                next_elem = h3.find_next()
                while next_elem:
                    if next_elem.name == "p":
                        p_text = next_elem.get_text(strip=True)
                        if p_text:  # Берем только непустые параграфы
                            answer_text = str(next_elem)
                            break
                    next_elem = next_elem.find_next()
                break

        # Если не нашли через BeautifulSoup, пробуем регулярные выражения
        if not answer_text.strip():
            # Ищем <h3>Ответ</h3> и следующий за ним непустой <p>
            answer_pattern = r"<h3>\s*Ответ\s*</h3>(?:<p>\s*</p>)?\s*<p>(.*?)</p>"
            answer_match = re.search(answer_pattern, section_html, re.DOTALL | re.IGNORECASE)

            if answer_match:
                answer_content = answer_match.group(1)
                answer_text = f"<p>{answer_content}</p>"

        if not answer_text.strip():
            print(f"  Пропускаем задачу {problem_id}: нет ответа")
            # Отладочная информация
            print(f"  HTML секции (первые 500 символов): {section_html[:500]}")
            continue

        print(f"  Найден ответ: {answer_text}")

        # Очистка текста
        def clean_text(text):
            # Убираем лишние пробелы и переносы строк
            text = re.sub(r"\s+", " ", text)
            text = text.strip()
            # Убираем пустые параграфы
            text = re.sub(r"<p>\s*</p>", "", text)
            return text

        problem_text = clean_text(problem_text)
        solution_text = clean_text(solution_text)
        answer_text = clean_text(answer_text)

        # Создаем JSON структуру
        problem_data = {
            "id": problem_id,
            "problem": problem_text,
            "solution": solution_text,
            "answer": answer_text,
        }

        parsed_problems.append(problem_data)
        print(f"  Задача {problem_id} успешно обработана")

    # Сохраняем каждую задачу в отдельный JSON файл
    for problem in parsed_problems:
        filename = f"problem_{problem['id']}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(problem, f, ensure_ascii=False, indent=2)
        print(f"Сохранен файл: {filename}")

    print(f"\nВсего обработано задач: {len(parsed_problems)}")
    return parsed_problems


# Упрощенная версия, которая точно находит ответы
def parse_problems_simple(file_path):
    with open(file_path, "r", encoding="koi8-r") as file:
        html_content = file.read()

    # Простой подход: ищем все задачи по шаблону
    # Каждая задача начинается с <a name="problem_XXXXX">
    problem_pattern = (
        r'<a name="problem_(\d+)"></a>(.*?)(?=<hr>\s*<a name="problem_|</div>\s*</div>)'
    )

    problems = re.findall(problem_pattern, html_content, re.DOTALL)

    parsed_problems = []

    for problem_id, problem_html in problems:
        print(f"\nОбрабатываем задачу {problem_id}...")

        # Проверяем изображения
        img_pattern = r'<img[^>]*src="([^"]*)"[^>]*>'
        images = re.findall(img_pattern, problem_html)

        has_forbidden_images = False
        for img_src in images:
            if img_src != "images/into_basket.gif":
                has_forbidden_images = True
                break

        if has_forbidden_images:
            print(f"  Пропускаем задачу {problem_id}: содержит запрещенные изображения")
            continue

        # Ищем условие задачи - берем первый непустой <p> после начала
        problem_text = ""
        # Ищем все <p> теги и берем первый значимый
        p_tags = re.findall(r"<p>.*?</p>", problem_html, re.DOTALL)

        for p_tag in p_tags:
            # Убираем HTML теги, чтобы проверить текст
            text_only = re.sub(r"<[^>]+>", "", p_tag)
            text_only = text_only.strip()

            if text_only and len(text_only) > 10:  # Берем только значимые параграфы
                problem_text = p_tag
                break

        if not problem_text.strip():
            print(f"  Пропускаем задачу {problem_id}: нет условия задачи")
            continue

        # Ищем решение
        solution_text = ""
        solution_match = re.search(
            r"<h3>\s*Решение\s*</h3>(.*?)(?=<h3>|$)", problem_html, re.DOTALL | re.IGNORECASE
        )
        if solution_match:
            # Извлекаем все <p> теги из решения
            solution_content = solution_match.group(1)
            solution_p_tags = re.findall(r"<p>.*?</p>", solution_content, re.DOTALL)
            for p_tag in solution_p_tags:
                solution_text += p_tag + " "

        # ИЩЕМ ОТВЕТ - ПРОСТО И ТОЧНО
        answer_text = ""
        # Шаблон: <h3>Ответ</h3><p></p><p>ТЕКСТ ОТВЕТА</p>
        answer_match = re.search(
            r"<h3>\s*Ответ\s*</h3>\s*(?:<p>\s*</p>)?\s*<p>(.*?)</p>",
            problem_html,
            re.DOTALL | re.IGNORECASE,
        )

        if not answer_match:
            # Альтернативный шаблон: <h3>Ответ</h3> затем любой текст до следующего тега
            answer_match = re.search(
                r"<h3>\s*Ответ\s*</h3>(.*?)(?=<[^p]|$)", problem_html, re.DOTALL | re.IGNORECASE
            )
            if answer_match:
                # Извлекаем текст из найденного блока
                answer_content = answer_match.group(1)
                # Ищем в этом блоке тег <p> с текстом
                p_match = re.search(r"<p>(.*?)</p>", answer_content, re.DOTALL)
                if p_match:
                    answer_text = f"<p>{p_match.group(1)}</p>"

        if answer_match and not answer_text:
            # Если нашли совпадение, но не извлекли текст
            answer_content = answer_match.group(1)
            # Пробуем извлечь любой текст внутри тегов
            answer_text = re.sub(r"<[^>]+>", "", answer_content)
            answer_text = f"<p>{answer_text.strip()}</p>"

        if not answer_text.strip():
            print(f"  Пропускаем задачу {problem_id}: нет ответа")
            # Для отладки покажем фрагмент HTML где должен быть ответ
            if "Ответ</h3>" in problem_html:
                idx = problem_html.find("Ответ</h3>")
                print(f"  Фрагмент с ответом: {problem_html[idx : idx + 200]}")
            continue

        print(f"  Найден ответ: {answer_text}")

        # Очистка текста
        def clean_text(text):
            text = re.sub(r"\s+", " ", text)
            text = text.strip()
            text = re.sub(r"<p>\s*</p>", "", text)
            return text

        problem_text = clean_text(problem_text)
        solution_text = clean_text(solution_text)
        answer_text = clean_text(answer_text)

        problem_data = {
            "id": problem_id,
            "problem": problem_text,
            "solution": solution_text,
            "answer": answer_text,
        }

        parsed_problems.append(problem_data)
        print(f"  Задача {problem_id} успешно обработана")

    # Сохраняем
    for problem in parsed_problems:
        filename = f"problem_{problem['id']}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(problem, f, ensure_ascii=False, indent=2)

    print(f"\nВсего обработано задач: {len(parsed_problems)}")
    return parsed_problems


# Самый простой и надежный вариант
def parse_problems_direct(file_path):
    with open(file_path, "r", encoding="koi8-r") as file:
        content = file.read()

    # Находим все problem_id
    problem_ids = re.findall(r'<a name="problem_(\d+)"></a>', content)

    parsed_problems = []

    for problem_id in problem_ids:
        print(f"\nОбрабатываем задачу {problem_id}...")

        # Находим начало и конец задачи
        start_pattern = f'<a name="problem_{problem_id}"></a>'
        start_idx = content.find(start_pattern)

        if start_idx == -1:
            continue

        # Ищем конец задачи (начало следующей или <hr> с пагинацией)
        next_problem = f'<a name="problem_'
        next_idx = content.find(next_problem, start_idx + len(start_pattern))

        end_idx = content.find("<hr><p>Страница:", start_idx)
        if end_idx == -1 or (next_idx != -1 and next_idx < end_idx):
            end_idx = next_idx

        if end_idx == -1:
            end_idx = len(content)

        problem_html = content[start_idx:end_idx]

        # Проверяем изображения
        if (
            "images/go.gif" in problem_html
            or "images/ed.png" in problem_html
            or "images/hide.gif" in problem_html
        ):
            print(f"  Пропускаем задачу {problem_id}: содержит запрещенные изображения")
            continue

        # Ищем условие - первый значимый <p> после начала
        problem_text = ""
        p_start = problem_html.find("<p>")
        while p_start != -1:
            p_end = problem_html.find("</p>", p_start)
            if p_end == -1:
                break

            p_tag = problem_html[p_start : p_end + 4]
            # Проверяем, есть ли в теге текст
            text_only = re.sub(r"<[^>]+>", "", p_tag)
            text_only = re.sub(r"\s+", " ", text_only).strip()

            if text_only and len(text_only) > 10 and "Автор:" not in text_only:
                problem_text = p_tag
                break

            p_start = problem_html.find("<p>", p_end)

        if not problem_text:
            print(f"  Пропускаем задачу {problem_id}: нет условия")
            continue

        # Ищем решение
        solution_text = ""
        sol_idx = problem_html.find("<h3>Решение</h3>")
        if sol_idx == -1:
            sol_idx = problem_html.find("<h3>\nРешение\n</h3>")

        if sol_idx != -1:
            # Ищем конец решения
            end_sol = problem_html.find("<h3>", sol_idx + 1)
            if end_sol == -1:
                end_sol = len(problem_html)

            solution_block = problem_html[sol_idx:end_sol]
            # Извлекаем все <p> теги из блока решения
            p_tags = re.findall(r"<p>.*?</p>", solution_block, re.DOTALL)
            for p_tag in p_tags:
                solution_text += p_tag + " "

        # ИЩЕМ ОТВЕТ - ПРОСТО И ПОНЯТНО
        answer_text = ""
        # Ищем <h3>Ответ</h3>
        answer_idx = problem_html.find("<h3>Ответ</h3>")
        if answer_idx == -1:
            answer_idx = problem_html.find("<h3>\nОтвет\n</h3>")

        if answer_idx != -1:
            # Ищем следующий <p> после Ответа
            p_start = problem_html.find("<p>", answer_idx)
            while p_start != -1:
                p_end = problem_html.find("</p>", p_start)
                if p_end == -1:
                    break

                p_tag = problem_html[p_start : p_end + 4]
                # Проверяем, есть ли в теге текст
                text_only = re.sub(r"<[^>]+>", "", p_tag)
                text_only = re.sub(r"\s+", " ", text_only).strip()

                if text_only:
                    answer_text = p_tag
                    break

                p_start = problem_html.find("<p>", p_end)

        if not answer_text:
            print(f"  Пропускаем задачу {problem_id}: нет ответа")
            continue

        print(f"  Найден ответ: {answer_text}")

        # Очистка
        def clean_text(text):
            text = re.sub(r"\s+", " ", text)
            text = text.strip()
            text = re.sub(r"<p>\s*</p>", "", text)
            return text

        problem_text = clean_text(problem_text)
        solution_text = clean_text(solution_text)
        answer_text = clean_text(answer_text)

        problem_data = {
            "id": problem_id,
            "problem": problem_text,
            "solution": solution_text,
            "answer": answer_text,
        }

        parsed_problems.append(problem_data)
        print(f"  Задача {problem_id} успешно обработана")

    # Сохраняем
    for problem in parsed_problems:
        filename = f"problem_{problem['id']}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(problem, f, ensure_ascii=False, indent=2)

    print(f"\nВсего обработано задач: {len(parsed_problems)}")
    return parsed_problems
