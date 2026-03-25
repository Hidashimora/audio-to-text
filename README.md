# AudioToText

Russian section: [jump to Russian](#russian)

## Support The Author
BNB Smart Chain (BEP20): `0x78187a5efaefa1a790be883492c4f0952a167c4a`  
Tron (TRC20): `TBynQEXksZzCcx5KC52i7VyjRKvmv6DrjV`  
Ethereum (ERC20): `0x78187a5efaefa1a790be883492c4f0952a167c4a`  
Toncoin (TON): `UQDfs6VWbinw4lmLOWZfrc4rfchxEhCHmtR0KNJzUpJ3mmK5`

## 📑 Содержание проекта
1. [English](#english)
2. [Русский](#russian)

<a id="english"></a>
## English

### What this project does
AudioToText is a desktop app (CustomTkinter + AssemblyAI) that converts audio/video files into `.txt` transcripts.

Main features:
- Language auto-detection
- Multiple API key support
- Built-in settings panel (language, theme, API keys)
- One-click open for output file and output folder

### Project structure
- `main.py`: app entry point
- `transcriber/ui.py`: full UI logic and user actions
- `transcriber/api.py`: AssemblyAI API client (upload, create job, polling)
- `transcriber/config.py`: config and local settings loading/saving
- `transcriber/utils.py`: helper utilities
- `assets/icons/`: all icons and UI resources
- `rebuild_clean.bat`: clean EXE build script
- `.env.example`: env template (`ASSEMBLYAI_API_KEY`)

### API key
Get your AssemblyAI API key here:  
https://www.assemblyai.com/dashboard/login

### Free tier limits (AssemblyAI)
- Access to industry-leading Speech-to-Text and Audio Intelligence models
- Transcribe up to 185 hours of pre-recorded audio for free
- Transcribe up to 333 hours of streaming audio for free
- Up to 5 new streams per minute
- Developer docs, community support, and resources to help you build
- Or roughly around `$50` in free credits

Limits can change over time, so check the dashboard for the latest values.

But we’re sneaky about it — we just create multiple accounts and use multiple keys.

### Note for users in Russia
AssemblyAI may require VPN access from Russia.  
Useful project: https://github.com/Hidashimora/free-vpn-anti-rkn

### Build EXE
Run:
```bat
rebuild_clean.bat
```
Result:
- `AudioToText.exe` in project root

### Local run
```bat
py main.py
```

<a id="russian"></a>
## Русский

### Что делает проект
AudioToText это десктопное приложение (CustomTkinter + AssemblyAI), которое переводит аудио/видео в текстовый `.txt` файл.

Основные возможности:
- Автоопределение языка
- Поддержка нескольких API-ключей
- Встроенные настройки (язык, тема, ключи)
- Быстрое открытие готового TXT и папки с результатами

### Структура проекта
- `main.py`: точка входа
- `transcriber/ui.py`: интерфейс и действия пользователя
- `transcriber/api.py`: работа с API AssemblyAI (загрузка, создание задачи, опрос статуса)
- `transcriber/config.py`: загрузка и сохранение локальных настроек
- `transcriber/utils.py`: вспомогательные функции
- `assets/icons/`: все иконки и ресурсы интерфейса
- `rebuild_clean.bat`: чистая сборка EXE
- `.env.example`: шаблон переменных окружения (`ASSEMBLYAI_API_KEY`)

### Где взять API ключ
Ключ берется в личном кабинете AssemblyAI:  
https://www.assemblyai.com/dashboard/login

### Лимиты бесплатной версии AssemblyAI
- Доступ к продвинутым Speech-to-Text и Audio Intelligence моделям
- До 185 часов распознавания заранее записанного аудио бесплатно
- До 333 часов стримингового аудио бесплатно
- До 5 новых стримов в минуту
- Документация, комьюнити и ресурсы для разработчиков
- Либо примерно около `$50` бесплатных кредитов

Лимиты со временем могут меняться, поэтому лучше перепроверять в кабинете AssemblyAI.

Но мы-то хитрые жуки, поэтому создаём несколько аккаунтов и пользуемся несколькими ключами.

### Важно для пользователей из России
Для доступа к AssemblyAI может понадобиться VPN.  
Ссылка: https://github.com/Hidashimora/free-vpn-anti-rkn

### Как собрать EXE
Запусти:
```bat
rebuild_clean.bat
```
Результат:
- `AudioToText.exe` в корне проекта

### Как запустить из Python
```bat
py main.py
```

## Support The Author
BNB Smart Chain (BEP20): `0x78187a5efaefa1a790be883492c4f0952a167c4a`  
Tron (TRC20): `TBynQEXksZzCcx5KC52i7VyjRKvmv6DrjV`  
Ethereum (ERC20): `0x78187a5efaefa1a790be883492c4f0952a167c4a`  
Toncoin (TON): `UQDfs6VWbinw4lmLOWZfrc4rfchxEhCHmtR0KNJzUpJ3mmK5`
