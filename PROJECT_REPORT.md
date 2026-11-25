# PROJECT REPORT
## FocusGuard AI: Real-Time Focus & Posture Guardian

### 1. Abstract
FocusGuard AI is an intelligent desktop companion designed to encourage healthier study and coding habits. It uses a computer webcam with computer-vision techniques to estimate shoulder/head alignment and eye openness. When an indicator suggests that the user may need to adjust posture or take a short break, the application displays a reminder. It also records study-session duration and an approximate focus score in a local SQLite database and presents session trends through a graphical dashboard.

### 2. Problem Statement
Students and computer users often spend long periods in front of screens. They may overlook poor sitting posture and fail to take regular visual breaks. A lightweight desktop tool can provide timely reminders and help users review their study-session habits.

### 3. Objectives
- Access a webcam and process frames in real time.
- Estimate basic posture alignment using body landmarks.
- Estimate eye openness using facial landmarks.
- Display reminders for potentially poor posture or prolonged eye closure.
- Record session duration and summary metrics locally.
- Visualize focus-score history.

### 4. Proposed System
The webcam supplies frames to OpenCV. MediaPipe extracts pose and face landmarks. A rule-based monitoring module evaluates shoulder alignment and approximate eye aspect ratio. The graphical interface displays the live camera feed and current status. When a session ends, summary values are stored in SQLite. Matplotlib reads session history and plots focus-score trends.

### 5. Technologies Used
- Python: application logic.
- OpenCV: webcam capture and image processing.
- MediaPipe: face and pose landmark detection.
- CustomTkinter: desktop graphical interface.
- SQLite: local session storage.
- Matplotlib: analytics visualization.
- Plyer: optional desktop notifications.
- Git and GitHub: version control and source-code hosting.

### 6. System Modules
1. Webcam module – captures live frames.
2. Posture module – checks shoulder alignment and head position heuristics.
3. Eye monitoring module – estimates eye openness from facial landmarks.
4. Alert module – provides reminders with a cooldown.
5. Dashboard module – displays video, status, timer and score.
6. Database module – stores session summaries.
7. Analytics module – plots historical focus scores.

### 7. Workflow
User starts the application → grants camera access → webcam frames are captured → landmarks are detected → posture and eye indicators are calculated → dashboard is updated → reminders are displayed when required → user stops the session → session summary is saved → analytics chart displays previous sessions.

### 8. Expected Outcome
The application provides a working educational prototype for webcam-based posture and eye-state reminders, session tracking, and simple productivity analytics.

### 9. Limitations
Detection quality depends on lighting, camera placement, visibility, and device performance. The current prototype uses simple heuristics and does not diagnose eye strain, fatigue, or musculoskeletal conditions. Focus score is an approximate software indicator, not a validated measure of concentration.

### 10. Future Enhancements
- Calibrate posture thresholds for each user.
- Add a configurable 20-20-20 break reminder.
- Improve fatigue estimation using blink frequency over time.
- Add weekly reports and CSV export.
- Add an option to run minimized to the system tray.
- Add accessibility and multilingual settings.

### 11. Conclusion
FocusGuard AI demonstrates how computer vision and desktop application development can be combined to encourage better study habits. It integrates real-time landmark detection, a graphical interface, notifications, local data storage, and visual analytics in one application.
