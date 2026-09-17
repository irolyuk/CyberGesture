<div align="center">

# CYBERGESTURE

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

## About CyberGesture

**CyberGesture** is a Windows desktop application that turns webcam-detected hand gestures and facial expressions into system actions.

It uses **OpenCV** and **MediaPipe** for real-time computer vision and **PySide6** for the desktop interface.

CyberGesture runs locally on the computer and provides configurable gesture detection, activation zones, action bindings and camera controls.

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

CyberGesture can trigger:

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

CyberGesture provides configurable controls for:

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

CyberGesture includes:

- Real-time webcam preview
- Multiple camera support
- Camera device selection
- Hand landmark visualization
- Face landmark visualization
- Gesture status HUD
- Face tracking status
- Configurable activation zone

## System Tray

CyberGesture can continue running after the main window is closed.

When **Minimize to Tray** is enabled:

- Closing the window hides CyberGesture to the system tray
- Double-clicking the tray icon restores the application
- **Open CyberGesture** restores the window
- **Exit** completely stops CyberGesture and releases the webcam

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

Run CyberGesture:

```powershell
python main.py
```

### Development Dependencies

To install dependencies required for building CyberGesture:

```powershell
python -m pip install -r requirements-dev.txt
```

## Building CyberGesture

Build the Windows application with PyInstaller:

```powershell
python -m PyInstaller --clean --noconfirm CyberGesture.spec
```

The generated application will be available in:

```text
dist/CyberGesture/
```

The Windows installer is configured through:

```text
CyberGesture_Setup.iss
```

and built using **Inno Setup**.

## User Settings

User-specific settings are stored in:

```text
%LOCALAPPDATA%\CyberGesture\settings.json
```

Default application settings are bundled separately with CyberGesture.

## Tested Configuration

CyberGesture v1.0.0 has been tested on the following system:

| Component | Tested configuration |
|---|---|
| OS | Windows 11 64-bit |
| CPU | Intel Core i5-9400 |
| RAM | 16 GB |
| GPU | NVIDIA GeForce GTX 1650 |
| Camera | Standard webcam |
| CyberGesture RAM usage | ~375 MB |
| Installed size | ~380 MB |
| Internet connection | Not required |

During testing, simultaneous hand and face tracking remained stable even when CyberGesture was restricted to a single logical CPU core.

> These are tested specifications, not minimum system requirements. CyberGesture may work on significantly lower-end hardware, but minimum requirements have not yet been established.
---

# Українська

## Про CyberGesture

**CyberGesture** — це десктопна програма для Windows, яка перетворює жести рук та міміку обличчя, розпізнані через вебкамеру, на системні дії.

Для комп'ютерного зору в реальному часі використовуються **OpenCV** та **MediaPipe**, а інтерфейс програми створений за допомогою **PySide6**.

CyberGesture працює локально на комп'ютері та дозволяє налаштовувати розпізнавання жестів, зону активації, прив'язку дій і камеру.

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

CyberGesture може виконувати:

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

Власні дії можна створювати та призначати безпосередньо у CyberGesture.

## Налаштування жестів

У CyberGesture можна налаштувати:

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

CyberGesture підтримує:

- Перегляд вебкамери в реальному часі
- Декілька камер
- Вибір пристрою камери
- Візуалізацію точок рук
- Візуалізацію точок обличчя
- HUD зі статусом жестів
- Статус відстеження обличчя
- Налаштовувану зону активації

## Системний трей

CyberGesture може продовжувати працювати після закриття головного вікна.

Якщо увімкнено **Minimize to Tray**:

- Закриття вікна ховає CyberGesture у системний трей
- Подвійний клік по іконці повертає вікно
- **Open CyberGesture** відкриває програму
- **Exit** повністю завершує CyberGesture та звільняє вебкамеру

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

Запуск CyberGesture:

```powershell
python main.py
```

### Залежності для розробки

Для встановлення інструментів, необхідних для збірки:

```powershell
python -m pip install -r requirements-dev.txt
```

## Збірка CyberGesture

Збірка Windows-програми через PyInstaller:

```powershell
python -m PyInstaller --clean --noconfirm CyberGesture.spec
```

Готова збірка з'явиться у:

```text
dist/CyberGesture/
```

Конфігурація Windows-інсталятора знаходиться у:

```text
CyberGesture_Setup.iss
```

Інсталятор збирається за допомогою **Inno Setup**.

## Налаштування користувача

Персональні налаштування зберігаються у:

```text
%LOCALAPPDATA%\CyberGesture\settings.json
```

Стандартні налаштування постачаються окремо разом із CyberGesture.

## Протестована конфігурація

CyberGesture v1.0.0 протестовано на такій системі:

| Компонент | Протестована конфігурація |
|---|---|
| ОС | Windows 11 64-bit |
| Процесор | Intel Core i5-9400 |
| Оперативна пам'ять | 16 ГБ |
| Відеокарта | NVIDIA GeForce GTX 1650 |
| Камера | Стандартна вебкамера |
| Використання RAM CyberGesture | ~375 МБ |
| Розмір після встановлення | ~380 МБ |
| Інтернет | Не потрібен |

Під час тестування одночасне відстеження рук та обличчя залишалося стабільним навіть при обмеженні CyberGesture до одного логічного ядра процесора.

> Це протестована конфігурація, а не мінімальні системні вимоги. CyberGesture може працювати на значно слабшому обладнанні, але мінімальні вимоги поки не визначені.
---

<div align="center">

## CyberGesture v1.0.0

**Created by Ivan Roliuk**

Hand & Face Gesture Control for Windows

</div>