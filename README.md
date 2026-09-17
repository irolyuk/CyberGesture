<div align="center">

# CYBERCAM

### Webcam Gesture Control for Windows

Control media, keyboard shortcuts, programs, files and folders using  
**hand gestures and facial expressions detected through your webcam.**

<br>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?logo=qt&logoColor=white)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/Tracking-MediaPipe-00A67E)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)
![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)

<br>

**[English](#english) · [Українська](#українська)**

</div>

---

# English

## About CyberCam

**CyberCam** is a Windows desktop application that turns webcam-detected hand gestures and facial expressions into system actions.

It uses **OpenCV** and **MediaPipe** for real-time computer vision and **PySide6** for the desktop interface.

CyberCam runs locally on the computer and provides configurable gesture detection, activation zones, action bindings and camera controls.

## Features

### Hand Gestures

Currently supported:

| Gesture | Support |
|---|:---:|
| Open Palm | ✅ |
| Fist | ✅ |
| Victory | ✅ |
| Point | ✅ |
| Heart | ✅ |

Each gesture can be assigned to an available action.

### Face Gestures

Currently supported:

| Expression | Support |
|---|:---:|
| Smile | ✅ |
| Mouth Open | ✅ |
| Eyebrows Up | ✅ |

Face actions are triggered only when the detected face is inside the configured activation zone.

### Actions

CyberCam can trigger:

- ▶️ Play / Pause
- ⏭️ Next Track
- ⏮️ Previous Track
- 🔊 Volume Up
- 🔉 Volume Down
- 🔇 Mute
- ⌨️ Custom keyboard shortcuts
- 🚀 Launch programs
- 📄 Open files
- 📁 Open folders

Custom actions can be created and assigned directly inside the application.

## Gesture Configuration

CyberCam provides configurable controls for:

- Activation zone position
- Activation zone width and height
- Normal hand activation size
- Fist activation size
- Gesture stability
- Gesture cooldown
- Smile sensitivity
- Mouth Open sensitivity
- Eyebrows Up sensitivity
- Face gesture stability
- Face gesture cooldown

Changes can be tested during the current session and saved when needed.

## Camera & Tracking

CyberCam includes:

- Real-time webcam preview
- Multiple camera support
- Camera device selection
- Hand landmark visualization
- Face landmark visualization
- Gesture status HUD
- Face tracking status
- Configurable activation zone

## System Tray

CyberCam can continue running after the main window is closed.

When **Minimize to Tray** is enabled:

- Closing the window hides CyberCam to the system tray
- Double-clicking the tray icon restores the application
- **Open CyberCam** restores the window
- **Exit** completely stops CyberCam and releases the webcam

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application |
| PySide6 | Desktop UI |
| OpenCV | Camera and image processing |
| MediaPipe | Hand and face tracking |
| PyInstaller | Windows application build |
| Inno Setup | Windows installer |

## Requirements

For the packaged release:

- Windows 10 / 11
- Webcam

**Python is not required for users running the packaged application.**

## Development

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install runtime dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run CyberCam:

```powershell
python main.py
```

### Development Dependencies

To install dependencies required for building CyberCam:

```powershell
python -m pip install -r requirements-dev.txt
```

## Building CyberCam

Build the Windows application with PyInstaller:

```powershell
python -m PyInstaller --clean --noconfirm CyberCam.spec
```

The generated application will be available in:

```text
dist/CyberCam/
```

The Windows installer is configured through:

```text
CyberCam_Setup.iss
```

and built using **Inno Setup**.

## User Settings

User-specific settings are stored in:

```text
%LOCALAPPDATA%\CyberCam\settings.json
```

Default application settings are bundled separately with CyberCam.

---

# Українська

## Про CyberCam

**CyberCam** — це десктопна програма для Windows, яка перетворює жести рук та міміку обличчя, розпізнані через вебкамеру, на системні дії.

Для комп'ютерного зору в реальному часі використовуються **OpenCV** та **MediaPipe**, а інтерфейс програми створений за допомогою **PySide6**.

CyberCam працює локально на комп'ютері та дозволяє налаштовувати розпізнавання жестів, зону активації, прив'язку дій і камеру.

## Можливості

### Жести рук

Наразі підтримуються:

| Жест | Підтримка |
|---|:---:|
| Відкрита долоня | ✅ |
| Кулак | ✅ |
| Victory | ✅ |
| Вказування | ✅ |
| Серце | ✅ |

Кожному жесту можна призначити доступну дію.

### Міміка обличчя

Наразі підтримуються:

| Вираз | Підтримка |
|---|:---:|
| Посмішка | ✅ |
| Відкритий рот | ✅ |
| Підняті брови | ✅ |

Дія спрацьовує лише тоді, коли розпізнане обличчя знаходиться всередині налаштованої зони активації.

### Дії

CyberCam може виконувати:

- ▶️ Play / Pause
- ⏭️ Наступний трек
- ⏮️ Попередній трек
- 🔊 Збільшення гучності
- 🔉 Зменшення гучності
- 🔇 Вимкнення звуку
- ⌨️ Власні комбінації клавіш
- 🚀 Запуск програм
- 📄 Відкриття файлів
- 📁 Відкриття папок

Власні дії можна створювати та призначати безпосередньо у CyberCam.

## Налаштування жестів

У CyberCam можна налаштувати:

- Положення зони активації
- Ширину та висоту зони
- Розмір активації руки
- Окремий розмір активації кулака
- Стабільність жесту
- Cooldown жесту
- Чутливість посмішки
- Чутливість відкритого рота
- Чутливість піднятих брів
- Стабільність міміки
- Cooldown міміки

Зміни можна тестувати під час поточної сесії та зберігати за потреби.

## Камера та відстеження

CyberCam підтримує:

- Перегляд вебкамери в реальному часі
- Декілька камер
- Вибір пристрою камери
- Візуалізацію точок рук
- Візуалізацію точок обличчя
- HUD зі статусом жестів
- Статус відстеження обличчя
- Налаштовувану зону активації

## Системний трей

CyberCam може продовжувати працювати після закриття головного вікна.

Якщо увімкнено **Minimize to Tray**:

- Закриття вікна ховає CyberCam у системний трей
- Подвійний клік по іконці повертає вікно
- **Open CyberCam** відкриває програму
- **Exit** повністю завершує CyberCam та звільняє вебкамеру

## Технології

| Технологія | Використання |
|---|---|
| Python 3.12 | Основна програма |
| PySide6 | Десктопний інтерфейс |
| OpenCV | Камера та обробка зображення |
| MediaPipe | Відстеження рук та обличчя |
| PyInstaller | Збірка Windows-програми |
| Inno Setup | Створення інсталятора |

## Вимоги

Для готової версії:

- Windows 10 / 11
- Вебкамера

**Для запуску готової збірки користувачу не потрібно встановлювати Python.**

## Розробка

Створення віртуального середовища:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Встановлення основних залежностей:

```powershell
python -m pip install -r requirements.txt
```

Запуск CyberCam:

```powershell
python main.py
```

### Залежності для розробки

Для встановлення інструментів, необхідних для збірки:

```powershell
python -m pip install -r requirements-dev.txt
```

## Збірка CyberCam

Збірка Windows-програми через PyInstaller:

```powershell
python -m PyInstaller --clean --noconfirm CyberCam.spec
```

Готова збірка з'явиться у:

```text
dist/CyberCam/
```

Конфігурація Windows-інсталятора знаходиться у:

```text
CyberCam_Setup.iss
```

Інсталятор збирається за допомогою **Inno Setup**.

## Налаштування користувача

Персональні налаштування зберігаються у:

```text
%LOCALAPPDATA%\CyberCam\settings.json
```

Стандартні налаштування постачаються окремо разом із CyberCam.

---

<div align="center">

## CyberCam v1.0.0

**Created by Ivan Roliuk**

Hand & Face Gesture Control for Windows

</div>