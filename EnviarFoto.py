import telebot
TOKEN = "673863930:AAHnDKVX2HyWXJfAuWS3gzs2kGq_3WRNmvE"
tb = telebot.TeleBot(TOKEN)
DestinatarioTelegram = -356316070

nombreArchivo = "Reporte.jpg"
photo = open(nombreArchivo, 'rb')
tb.send_photo(DestinatarioTelegram, photo)

#https://geekytheory.com/telegram-programando-un-bot-en-python
