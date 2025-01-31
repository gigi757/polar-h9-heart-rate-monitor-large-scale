import asyncio
import tkinter as tk
import logging
import threading
from bleak import BleakClient, BleakScanner

# Настройка логирования
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

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
    logging.info(f"Подключение к {device.name} ({device.address})...")
    async with BleakClient(device) as client:
        logging.info("Подключено!")

        # Включение уведомлений для данных о пульсе
        await client.start_notify(HEART_RATE_MEASUREMENT_CHAR_UUID, heart_rate_notification_handler)
        logging.info("Ожидание данных о пульсе...")

        # Поддержание подключения
        while True:
            await asyncio.sleep(1)

# Функция для сканирования устройств
async def scan_devices():
    logging.info("Начало сканирования Bluetooth-устройств...")
    try:
        # Тайм-аут сканирования (10 секунд)
        devices = await BleakScanner.discover(timeout=10)
        logging.info(f"Найдено устройств: {len(devices)}")
        for device in devices:
            logging.info(f"Устройство: {device.name} ({device.address})")
        return devices
    except Exception as e:
        logging.error(f"Ошибка при сканировании: {e}")
        return []

# Функция для создания кнопок устройств
def create_device_buttons(devices):
    for device in devices:
        # Создание кнопки для каждого устройства
        button = tk.Button(
            device_frame,
            text=f"{device.name} ({device.address})",
            command=lambda d=device: connect_to_device(d),
            font=("Arial", 14),
            bg="lightblue",
            fg="black"
        )
        button.pack(fill=tk.X, pady=5)

# Функция для подключения к выбранному устройству
def connect_to_device(device):
    # Запуск асинхронного кода в отдельном потоке
    threading.Thread(
        target=asyncio.run,
        args=(connect_to_polar_h9(device),),
        daemon=True
    ).start()

# Асинхронная функция для сканирования и отображения устройств
async def scan_and_show_devices():
    devices = await scan_devices()
    if devices:
        create_device_buttons(devices)
    else:
        no_devices_label.config(text="Устройства не найдены. Убедитесь, что Bluetooth включен.")

# Функция для запуска асинхронного сканирования
def start_scan():
    # Очистка предыдущих кнопок
    for widget in device_frame.winfo_children():
        widget.destroy()
    no_devices_label.config(text="Сканирование...")
    threading.Thread(
        target=asyncio.run,
        args=(scan_and_show_devices(),),
        daemon=True
    ).start()

# Создание основного окна Tkinter
root = tk.Tk()
root.title("Polar H9 Heart Rate Monitor")
root.attributes("-fullscreen", True)  # Полноэкранный режим

# Создание метки для отображения пульса
heart_rate_label = tk.Label(root, text="0", font=("Arial", 400), fg="red")
heart_rate_label.pack(expand=True)

# Фрейм для кнопок устройств
device_frame = tk.Frame(root)
device_frame.pack(fill=tk.BOTH, expand=True)

# Метка для сообщений (например, "Устройства не найдены")
no_devices_label = tk.Label(root, text="", font=("Arial", 14), fg="black")
no_devices_label.pack()

# Кнопка для запуска сканирования
scan_button = tk.Button(
    root,
    text="Сканировать устройства",
    command=start_scan,
    font=("Arial", 14),
    bg="green",
    fg="white"
)
scan_button.pack(fill=tk.X, pady=10)

# Запуск обновления интерфейса
update_gui()

# Запуск основного цикла Tkinter
root.mainloop()
