# FocusGuard AI – Real-Time Focus & Posture Guardian

A Python desktop companion that uses a webcam and computer-vision landmarks to provide basic posture and eye-state reminders during study or coding sessions.

## Features
- Live webcam preview (camera frames are processed locally and are not stored).
- MediaPipe Pose-based shoulder/head alignment heuristic.
- MediaPipe Face Mesh-based approximate eye aspect ratio.
- Basic eye-state feedback; facial expressions and emotions are not classified.
- Desktop reminders (Plyer, when supported by the operating system).
- Study session timer and SQLite session history.
- Focus-score trend chart using Matplotlib.
- Desktop interface using CustomTkinter.
- Light/dark appearance toggle; the app logo accent follows the selected theme.

## Requirements
- Windows 10/11, macOS, or Linux with Python 3.11 recommended.
- Webcam.
- Internet connection for installing Python packages.

## Setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```
If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Setup (Command Prompt)
```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## How to use
1. Run `python main.py`.
2. Allow webcam access if the operating system asks.
3. Sit far enough back for your shoulders and face to be visible.
4. Click **START MONITORING**.
5. Click **STOP** to save the session.
6. Click **Saved Sessions** to browse the saved records, or **Analytics** to view the focus-score chart.

## GitHub workflow
```bash
git init
git add .
git commit -m "Initial FocusGuard AI project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Real-Time-Focus-Posture-Guardian.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. Create the empty repository on GitHub first.

## Limitations and responsible use
This is an educational prototype, not a medical device or a scientifically validated fatigue detector. Posture estimates depend on camera angle, lighting, clothing, and whether shoulders/face are visible. Eye closure in a single frame is not proof of fatigue; blink patterns and fatigue require longer-term calibrated analysis. Facial expressions and emotions are not classified. Do not use the score for health, employment, or academic evaluation. Webcam images are not saved by this application. Stop monitoring whenever desired.

## Troubleshooting
- **Camera unavailable:** close other camera apps, check OS camera permission, and try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in `main.py`.
- **MediaPipe install issue:** use Python 3.11 (64-bit) and install dependencies in a fresh virtual environment.
- **No face/posture detected:** improve lighting and move back so your face and shoulders are visible.
- **Notifications not appearing:** some operating systems restrict desktop notifications; dashboard alerts still update.
