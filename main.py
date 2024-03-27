import csv
import datetime
from ossapi import Ossapi
from ossapi.models import MatchResponse

def get_links_with_word(start_num, end_num, target_word):
    links_with_word = []
    for num in range(start_num, end_num + 1):
        try:
            match_id = str(num)
            match_response = api.match(match_id)
            if match_response.match:
                match_url = f"https://osu.ppy.sh/community/matches/{match_id}"
                print(f"Проверяем ссылку: {match_url}")
                if target_word.lower() in match_response.match.name.lower():
                    print(f"Слово '{target_word}' найдено на странице: {match_url}")
                    links_with_word.append(match_url)
            else:
                print(f"Матч {match_id} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при обработке матча с ID {match_id}: {e}")
    return links_with_word

def get_match_time(match_id: str):
    try:
        match_response: MatchResponse = api.match(match_id)
        if match_response.match:
            start_time: datetime.datetime = match_response.match.start_time
            return start_time
        else:
            print(f"Матч {match_id} не найден.")
            return None
    except Exception as e:
        print(f"Произошла ошибка при получении информации о матче с ID {match_id}: {e}")
        return None

def find_nearest_match(start_id, end_id, target_datetime):
    while start_id <= end_id:
        try:
            mid = (start_id + end_id) // 2
            match_datetime = get_match_time(str(mid))
            if match_datetime is not None:
                if match_datetime.date() < target_datetime.date():
                    start_id = mid + 1
                elif match_datetime.date() > target_datetime.date():
                    end_id = mid - 1
                else:
                    match_time = match_datetime.time()
                    time_difference = (datetime.datetime.combine(match_datetime.date(), match_time) - target_datetime).total_seconds() / 60
                    if abs(time_difference) <= 15:
                        return mid
                    elif time_difference < -15:
                        start_id = mid + 1
                    else:
                        end_id = mid - 1
            else:
                start_id = mid + 1
        except Exception as e:
            print(f"Произошла ошибка при поиске ближайшего матча: {e}")
            return None

if __name__ == "__main__":
    # Чтение из CSV файла
    with open('data.csv', 'r', newline='') as file:
        reader = csv.reader(file)
        target_word = next(reader)[0].rstrip(';')  # Получаем искомое слово из первой строки и удаляем ";" в конце
        matches = [(row[0].split(';')[0], row[0].split(';')[1]) for row in reader if len(row) >= 1]  # Считываем дату и время для каждого матча, если есть обе ячейки
    # Создание объекта Ossapi с указанием клиентских данных
    client_id = ""
    client_secret = ""
    api = Ossapi(client_id, client_secret)

    # Обработка каждого матча
    for target_date, target_time in matches:
        target_datetime = datetime.datetime.strptime(f"{target_date} {target_time}", "%Y-%m-%d %H:%M:%S")

        # Поиск ближайшего матча
        start_id = 0
        end_id = 113236987
        nearest_match_id = find_nearest_match(start_id, end_id, target_datetime)

        if nearest_match_id is not None:
            print(f"Самый близкий матч к указанному времени найден. ID матча: {nearest_match_id}")
            start_search_id = max(0, nearest_match_id - 300)
            end_search_id = nearest_match_id + 300
            found_links = get_links_with_word(start_search_id, end_search_id, target_word)

            # Запись результатов в CSV файл
            with open('output.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([[link] for link in found_links])
        else:
            print("Ни один матч не удовлетворяет условиям.")
