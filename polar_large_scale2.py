import asyncio
import tkinter as tk
from bleak import BleakClient, BleakScanner

# UUID для службы и характеристики измерения пульса
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Глобальная переменная для хранения пульса
heart_rate = 0

# Функция для разбора данных о пульсе
def parse_heart_rate_data(data):
    byte0 = data[0]
    flags = byte0 & 0x01  # Проверка, является ли пульс 8-битным или 16-битным
    return data[1] if flags == 0 else int.from_bytes(data[1:3], byteorder="little")

# Обработчик уведомлений о пульсе
def heart_rate_notification_handler(sender, data):
    global heart_rate
    heart_rate = parse_heart_rate_data(data)

# Функция для обновления интерфейса
def update_gui():
    heart_rate_label.config(text=f"{heart_rate}")
    root.after(100, update_gui)  # Обновление интерфейса каждые 100 мс

# Функция для подключения к Polar H9
async def connect_to_polar_h9(device):
    print(f"Подключение к {device.name} ({device.address})...")
    async with BleakClient(device) as client:
        print("Подключено!")

        # Включение уведомлений для данных о пульсе
        await client.start_notify(HEART_RATE_MEASUREMENT_CHAR_UUID, heart_rate_notification_handler)
        print("Ожидание данных о пульсе...")

        # Поддержание подключения
        while True:
            await asyncio.sleep(1)

# Функция для сканирования устройств
async def scan_devices():
    print("Сканирование Bluetooth-устройств...")
    devices = await BleakScanner.discover()
    return devices

# Функция для отображения списка устройств и выбора Polar H9
async def select_device():
    devices = await scan_devices()
    if not devices:
        print("Устройства не найдены. Убедитесь, что Bluetooth включен.")
        return None

    print("Найденные устройства:")
    for i, device in enumerate(devices):
        print(f"{i + 1}. {device.name} ({device.address})")

    # Выбор устройства
    try:
        choice = int(input("Введите номер устройства, к которому хотите подключиться: ")) - 1
        if 0 <= choice < len(devices):
            return devices[choice]
        else:
            print("Неверный выбор.")
            return None
    except ValueError:
        print("Неверный ввод.")
        return None

# Создание основного окна Tkinter
root = tk.Tk()
root.title("Polar H9 Heart Rate Monitor")
root.attributes("-fullscreen", True)  # Полноэкранный режим

# Создание метки для отображения пульса
heart_rate_label = tk.Label(root, text="0", font=("Arial", 400), fg="red")
heart_rate_label.pack(expand=True)

# Запуск обновления интерфейса
update_gui()

# Основная функция
async def main():
    device = await select_device()
    if device:
        await connect_to_polar_h9(device)

# Запуск asyncio и Tkinter в отдельных потоках
import threading
threading.Thread(target=asyncio.run, args=(main(),), daemon=True).start()
root.mainloop()
