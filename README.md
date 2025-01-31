 Скрипт автоматически не определяет датчик Polar h9.
 для его подсоединения необходимо добавить его адрес вместо "A0:9E:1A:E0:4C:A3"
 Чтобы найти адрес: запустите в command shell (admin) строку 
 Get-PnpDevice -Class Bluetooth | Where-Object { $_.Name -like "*Polar*" } | Select-Object Name, InstanceId
 в результате получаем что-то типа : 
 Name              InstanceId
----              ----------
Polar H9 E04CA329 BTHLE\DEV_A09E1AE04CA3\7&20E906F3&0&A09E1AE04CA3

Итак адрес вашего устройства:  "A0:9E:1A:E0:4C:A3"
