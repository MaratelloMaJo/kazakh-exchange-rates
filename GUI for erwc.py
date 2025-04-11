import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import threading
import time
import os
import json

# --- Получение курсов валют ---
def fetch_exchange_rates():
    url = 'https://mig.kz/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    currency_names = soup.find_all("td", class_="currency")
    currency_buy = soup.find_all("td", class_="buy delta-neutral")
    currency_sell = soup.find_all("td", class_="sell delta-neutral")

    rates = {}
    for i in range(min(len(currency_names), len(currency_buy), len(currency_sell))):
        name = currency_names[i].get_text(strip=True)
        buy = currency_buy[i].get_text(strip=True).replace(',', '.')
        sell = currency_sell[i].get_text(strip=True).replace(',', '.')
        if name in ["USD", "EUR", "RUB"]:
            rates[name] = {
                'buy': float(buy),
                'sell': float(sell)
            }
    return rates

# --- Основной класс GUI ---
class CurrencyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("₸ Калькулятор валют | MIG.kz | Produced by Marat Zholynbek")
        self.geometry("600x600")

        self.icon_path = "icon.ico"
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)

        self.logo_path = "logo.png"
        self.logo_image = None
        self.sun_icon_path = "sun.png"
        self.moon_icon_path = "moon.png"

        self.settings_file = "settings.json"
        self.rates = fetch_exchange_rates()
        self.history = []
        self.theme = "System"
        self.selected_palette = "Синий"
        self.settings_win = None

        self.load_settings()
        self.create_widgets()
        self.auto_update_rates()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theme = data.get("theme", "System")
                    self.selected_palette = data.get("palette", "Синий")
                    ctk.set_appearance_mode(self.theme)
            except:
                pass

    def save_settings(self):
        settings = {
            "theme": self.theme,
            "palette": self.selected_palette
        }
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def apply_color_palette(self):
        palettes = {
            "Синий": ("#F0F4FD", "#1E1E2F"),
            "Фиолетовый": ("#EEE0FF", "#2A1A3F"),
            "Мятный": ("#E0FFF3", "#1F3F33"),
            "Розовый": ("#FFE0F0", "#3F1A2A"),
            "Нейтральный": ("#F5F5F5", "#2E2E2E")
        }
        self.configure(fg_color=palettes.get(self.selected_palette, ("#F0F4FD", "#1E1E2F")))

    def create_widgets(self):
        self.apply_color_palette()

        if os.path.exists(self.logo_path):
            image = Image.open(self.logo_path).resize((100, 100))
            self.logo_image = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
            self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
            self.logo_label.pack(pady=5)

        if os.path.exists(self.sun_icon_path) and os.path.exists(self.moon_icon_path):
            sun = Image.open(self.sun_icon_path).resize((30, 30))
            moon = Image.open(self.moon_icon_path).resize((30, 30))
            self.sun_icon = ctk.CTkImage(light_image=sun, dark_image=sun)
            self.moon_icon = ctk.CTkImage(light_image=moon, dark_image=moon)
            self.theme_button = ctk.CTkButton(self, text="", image=self.sun_icon, width=40, command=self.toggle_theme)
            self.theme_button.pack(pady=5, anchor="ne", padx=10)

        self.label_title = ctk.CTkLabel(self, text="Калькулятор валют", font=("Arial", 26, "bold"))
        self.label_title.pack(pady=10)

        self.currency_var = ctk.StringVar(value="USD")
        self.currency_menu = ctk.CTkOptionMenu(self, values=["USD", "EUR", "RUB"], variable=self.currency_var)
        self.currency_menu.pack(pady=10)

        self.direction_var = ctk.StringVar(value="KZT -> Валюта")
        self.direction_menu = ctk.CTkOptionMenu(
            self, values=["KZT -> Валюта", "Валюта -> KZT"], variable=self.direction_var)
        self.direction_menu.pack(pady=10)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Введите сумму")
        self.amount_entry.pack(pady=10)

        self.calc_button = ctk.CTkButton(
            self, text="Рассчитать", command=self.calculate,
            fg_color=("#6A5ACD", "#4B0082"), hover_color=("#836FFF", "#6A5ACD"),
            font=("Arial", 16, "bold"), corner_radius=16)
        self.calc_button.pack(pady=10)

        self.result_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self.result_label.pack(pady=10)

        self.history_box = ctk.CTkTextbox(self, width=550, height=150)
        self.history_box.pack(pady=10)
        self.history_box.insert("end", "История операций:\n")
        self.history_box.configure(state="disabled")

        self.update_time_label = ctk.CTkLabel(self, text="")
        self.update_time_label.pack(pady=5)

        self.settings_button = ctk.CTkButton(
            self, text="Настройки", command=self.open_settings,
            fg_color=("#20B2AA", "#008B8B"), hover_color=("#40E0D0", "#20B2AA"),
            font=("Arial", 14), corner_radius=10)
        self.settings_button.pack(pady=10)

    def toggle_theme(self):
        if self.theme == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme = "Light"
            self.theme_button.configure(image=self.sun_icon)
        else:
            ctk.set_appearance_mode("Dark")
            self.theme = "Dark"
            self.theme_button.configure(image=self.moon_icon)
        self.save_settings()

    def change_palette(self, palette_name):
        self.selected_palette = palette_name
        self.apply_color_palette()
        self.save_settings()

    def calculate(self):
        currency = self.currency_var.get()
        direction = self.direction_var.get()

        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            self.result_label.configure(text="Введите корректную сумму!")
            return

        if currency not in self.rates:
            self.result_label.configure(text="Нет данных по выбранной валюте.")
            return

        rate_buy = self.rates[currency]['buy']
        rate_sell = self.rates[currency]['sell']

        if direction == "KZT -> Валюта":
            result_buy = amount / rate_buy
            result_sell = amount / rate_sell
            text = (f"{amount} ₸ ≈ {result_buy:.2f} {currency} (по покупке)\n"
                    f"{amount} ₸ ≈ {result_sell:.2f} {currency} (по продаже)")
        else:
            result_buy = amount * rate_sell
            result_sell = amount * rate_buy
            text = (f"{amount} {currency} ≈ {result_sell:.2f} ₸ (по продаже)\n"
                    f"{amount} {currency} ≈ {result_buy:.2f} ₸ (по покупке)")

        self.result_label.configure(text=text)
        self.add_to_history(text)

    def add_to_history(self, entry):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_entry = f"[{timestamp}] {entry}\n"
        self.history_box.configure(state="normal")
        self.history_box.insert("end", full_entry)
        self.history_box.configure(state="disabled")

    def auto_update_rates(self):
        def update_loop():
            while True:
                try:
                    self.rates = fetch_exchange_rates()
                    now = datetime.now().strftime("%H:%M:%S")
                    self.update_time_label.configure(text=f"Курсы обновлены: {now}")
                except:
                    self.update_time_label.configure(text="Ошибка обновления курсов")
                time.sleep(60)

        threading.Thread(target=update_loop, daemon=True).start()

    def open_settings(self):
        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.focus()
            return

        self.settings_win = ctk.CTkToplevel(self)
        self.settings_win.title("Настройки")
        self.settings_win.geometry("400x400")

        ctk.CTkLabel(self.settings_win, text="Настройки интерфейса", font=("Arial", 18, "bold")).pack(pady=15)

        theme_label = ctk.CTkLabel(self.settings_win, text="Выберите тему")
        theme_label.pack(pady=5)
        theme_select = ctk.CTkOptionMenu(self.settings_win, values=["System", "Light", "Dark"],
                                         command=lambda value: [setattr(self, "theme", value), ctk.set_appearance_mode(value), self.save_settings()])
        theme_select.set(self.theme)
        theme_select.pack(pady=5)

        ctk.CTkLabel(self.settings_win, text="Цветовая палитра фона").pack(pady=10)
        palette_selector = ctk.CTkOptionMenu(
            self.settings_win,
            values=["Синий", "Фиолетовый", "Мятный", "Розовый", "Нейтральный"],
            command=self.change_palette
        )
        palette_selector.set(self.selected_palette)
        palette_selector.pack(pady=5)


if __name__ == "__main__":
    app = CurrencyApp()
    app.mainloop()