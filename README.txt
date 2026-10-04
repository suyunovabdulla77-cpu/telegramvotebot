# Telegram ovoz berish bot

## Kerakli sozlamalar

BotFather orqali bot yarating va token oling.

Botni ovoz berish kanaliga administrator qilib qo'ying.

Muhit o'zgaruvchilari:
- BOT_TOKEN = BotFather tokeni
- CHANNEL_USERNAME = kanal username'i, masalan @UrgutAcademy

## Ishga tushirish

pip install -r requirements.txt
export BOT_TOKEN="TOKEN"
export CHANNEL_USERNAME="@KANAL_USERNAME"
python bot.py

Windows PowerShell:
$env:BOT_TOKEN="TOKEN"
$env:CHANNEL_USERNAME="@KANAL_USERNAME"
python bot.py
