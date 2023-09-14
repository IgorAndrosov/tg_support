import os

def extract_questions_answers(root_folder):
    database = {}  # База данных будет представлена словарем

    for root, dirs, files in os.walk(root_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                question = file_name  # Используем имя файла как вопрос
                answer = file.read().strip()  # Читаем содержимое файла как ответ

                # Извлечение информации о разделе и подразделе из пути
                relative_path = os.path.relpath(file_path, root_folder)
                parts = relative_path.split(os.path.sep)
                section = parts[0] if parts else "Unknown"
                subsection = parts[1] if len(parts) > 1 else "Unknown"

                # Создаем структуру данных и добавляем ее в базу данных
                entry = {"question": question, "answer": answer}
                if section not in database:
                    database[section] = {}
                if subsection not in database[section]:
                    database[section][subsection] = []
                database[section][subsection].append(entry)

    return database

faq_folder = "faq"
faq_database = extract_questions_answers(faq_folder)