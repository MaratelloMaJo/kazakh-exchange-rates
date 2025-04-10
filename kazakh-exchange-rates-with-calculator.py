import requests
from bs4 import BeautifulSoup


def fetch_exchange_rates():
    print("Прямо сейчас здесь появится валюта (вытаскиваем из mig.kz:)\nProduced by Marat Zholynbek")
    url = 'https://mig.kz/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    currency_names = soup.find_all("td", class_="currency")
    currency_buy = soup.find_all("td", class_="buy delta-neutral")
    currency_sell = soup.find_all("td", class_="sell delta-neutral")

    rates = {}

    if len(currency_names) == len(currency_buy) == len(currency_sell):
        print("Курсы валют:")
        for i in range(len(currency_names)):
            name = currency_names[i].get_text(strip=True)
            buy = currency_buy[i].get_text(strip=True).replace(',', '.')
            sell = currency_sell[i].get_text(strip=True).replace(',', '.')

            if name in ["USD", "EUR", "RUB"]:
                print(f"{name}:")
                print(f"Покупка: {buy} ₸")
                print(f"Продажа: {sell} ₸")
                rates[name] = {
                    'buy': float(buy),
                    'sell': float(sell)
                }
    else:
        print("Ошибка: длины списков валют не совпадают. Структура сайта могла измениться.")

    return rates


def currency_calculator(rates):
    while True:
        print("\n----- Калькулятор валют -----")
        print("Доступные валюты:")
        print("1. USD (Доллар США)")
        print("2. EUR (Евро)")
        print("3. RUB (Российский рубль)")

        # Выбор валюты
        currency_choice = input("Выберите валюту (1-3): ")
        if currency_choice == '1':
            currency = 'USD'
        elif currency_choice == '2':
            currency = 'EUR'
        elif currency_choice == '3':
            currency = 'RUB'
        else:
            print("Неверный выбор валюты. Пожалуйста, выберите 1, 2 или 3.")
            continue

        # Выбор направления
        print("\nВыберите направление обмена:")
        print(f"1. Конвертировать из KZT в {currency} (по курсу покупки и продажи)")
        print(f"2. Конвертировать из {currency} в KZT (по курсу покупки и продажи)")

        direction_choice = input("Введите 1 или 2: ")

        if direction_choice == '1':
            direction = 'из KZT в валюту'
        elif direction_choice == '2':
            direction = 'из валюты в KZT'
        else:
            print("Неверный выбор направления. Пожалуйста, выберите 1 или 2.")
            continue

        # Ввод суммы
        amount = input(f"Введите сумму для конвертации (в KZT или {currency}): ")

        try:
            amount = float(amount)
        except ValueError:
            print("Неверная сумма. Попробуйте снова.")
            continue

        # Обработка конвертации в зависимости от направления
        if direction == 'из KZT в валюту':
            result_buy = amount / rates[currency]['buy']
            result_sell = amount / rates[currency]['sell']
            print(f"\n{amount} ₸ можно купить {result_buy:.2f} {currency} (по курсу покупки)")
            print(f"{amount} ₸ можно купить {result_sell:.2f} {currency} (по курсу продажи)")

        elif direction == 'из валюты в KZT':
            result_buy = amount * rates[currency]['sell']
            result_sell = amount * rates[currency]['buy']
            print(f"\n{amount} {currency} можно обменять на {result_sell:.2f} ₸ (по курсу продажи)")
            print(f"{amount} {currency} можно обменять на {result_buy:.2f} ₸ (по курсу покупки)")

        # Спрашиваем, хочет ли пользователь продолжить
        again = input("\nХотите выполнить ещё одну операцию? (да/нет): ").strip().lower()
        if again != 'да':
            print("Спасибо за использование курса валют. Выход из калькулятора...")
            break


# Основная программа
rates = fetch_exchange_rates()

while True:
    decision = input("\nХотите использовать калькулятор валют? (да/нет): ").strip().lower()

    if decision == "да":
        currency_calculator(rates)
        break
    elif decision == "нет":
        print("Спасибо за использование курса валют!")
        break
    else:
        print("Неверный ввод. Пожалуйста, ответьте 'да' или 'нет'.")
input("Нажмите Enter для выхода.")