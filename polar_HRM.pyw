import asyncio
import threading
import tkinter as tk
from tkinter import ttk
from bleak import BleakClient, BleakScanner


# UUID для службы и характеристики измерения пульса
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Глобальные переменные
heart_rate = 0
lower_limit = 90
upper_limit = 160

# Обработчик уведомлений о пульсе
def heart_rate_notification_handler(sender, data):
    global heart_rate
    byte0 = data[0]
    flags = byte0 & 0x01  # Проверка, является ли пульс 8-битным или 16-битным
    heart_rate = data[1] if flags == 0 else int.from_bytes(data[1:3], byteorder="little")

# Функция для обновления интерфейса
def update_gui():
    update_color_based_on_heart_rate()
    heart_rate_label.config(text=f"{heart_rate}")
    root.after(100, update_gui)  # Обновление интерфейса каждые 100 мс

# Функция для обновления цвета в зависимости от пульса
def update_color_based_on_heart_rate():
    lower_limit = int(lower_limit_var.get())
    upper_limit = int(upper_limit_var.get())
    if heart_rate < lower_limit:
        heart_rate_label.config(fg="blue", bg="lightblue")
    elif heart_rate > upper_limit:
        heart_rate_label.config(fg="red", bg="lightcoral")
    else:
        heart_rate_label.config(fg="black", bg="white")

# Функция для подключения к Polar
async def connect_to_polar(device):
    root.title(f"Подключение к {device.name} ({device.address})...")
    async with BleakClient(device) as client:
        root.title("Подключено!")

        # Включение уведомлений для данных о пульсе
        await client.start_notify(HEART_RATE_MEASUREMENT_CHAR_UUID, heart_rate_notification_handler)
        root.title("Ожидание данных о пульсе...")

        # Поддержание подключения
        while True:
            await asyncio.sleep(1)

# Функция для сканирования устройств
async def scan_devices():
    root.title("Сканирование Bluetooth-устройств...")
    devices = await BleakScanner.discover()
    return devices

# Функция для обновления списка устройств в Combobox
async def update_device_list():
    devices = await scan_devices()
    device_combobox['values'] = [f"{device.name} ({device.address})" for device in devices]

# Функция для подключения к выбранному устройству
def connect_to_selected_device():
    selected_device = device_combobox.get()
    if selected_device:
        address = selected_device.split("(")[-1].rstrip(")")
        asyncio.run_coroutine_threadsafe(connect_to_polar_by_address(address), loop)

# Функция для подключения к устройству по адресу
async def connect_to_polar_by_address(address):
    device = await BleakScanner.find_device_by_address(address)
    if device:
        await connect_to_polar(device)

# Создание основного окна Tkinter
root = tk.Tk()
root.title("Polar HRM")

# Создание метки для отображения пульса
heart_rate_label = tk.Label(root, text="0", font=("Arial", 400), fg="black", bg="white")
heart_rate_label.pack(expand=True, fill="both")

# Создание Combobox для выбора устройства
device_combobox = ttk.Combobox(root, state="readonly", width=40)
device_combobox.pack()

button_frame = tk.Frame(root)
button_frame.pack()

# Кнопка для обновления списка устройств
update_button = tk.Button(button_frame, text="Обновить список устройств", command=lambda: asyncio.run_coroutine_threadsafe(update_device_list(), loop))
update_button.pack(side=tk.constants.LEFT)

# Кнопка для подключения к выбранному устройству
connect_button = tk.Button(button_frame, text="Подключиться", command=connect_to_selected_device)
connect_button.pack(side=tk.constants.RIGHT)

entry_frame = tk.Frame(root)
entry_frame.pack()

# Поля ввода для границ пульса
lower_limit_var = tk.IntVar(root, lower_limit)
upper_limit_var = tk.IntVar(root, upper_limit)

lower_limit_spinbox = ttk.Spinbox(entry_frame, from_=40, to=160, width=10, textvariable=lower_limit_var)
lower_limit_spinbox.pack(side=tk.constants.LEFT)

upper_limit_spinbox = tk.Spinbox(entry_frame, from_=60, to=220, width=10, textvariable=upper_limit_var)
upper_limit_spinbox.pack(side=tk.constants.LEFT)

# Запуск обновления интерфейса
update_gui()

# Запуск asyncio и Tkinter в отдельных потоках
loop = asyncio.get_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()
root.mainloop()
