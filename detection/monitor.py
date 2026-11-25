import cv2
import math

class Monitor:
    """
    Uses MediaPipe Pose and Face Mesh landmarks.
    If MediaPipe is unavailable, the app still opens and reports that detection is unavailable.
    """
    def __init__(self):
        self.pose = None
        self.face = None
        self.available = False
        self.init_error = None
        try:
            import mediapipe as mp
            self.mp = mp
            self.pose = mp.solutions.pose.Pose(
                static_image_mode=False, model_complexity=0,
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            self.face = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=True,
                min_detection_confidence=0.5, min_tracking_confidence=0.5
            )
            self.available = True
        except Exception as exc:
            self.available = False
            self.init_error = f"{type(exc).__name__}: {exc}"

    def analyze(self, frame):
        if not self.available:
            return {"posture": "Unavailable", "eyes": "Unavailable",
                    "message": f"MediaPipe detection unavailable ({self.init_error})."}
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_result = self.pose.process(rgb)
        face_result = self.face.process(rgb)
        posture = "Not detected"
        eyes = "Not detected"
        messages = []

        if pose_result.pose_landmarks:
            lm = pose_result.pose_landmarks.landmark
            mp_pose = self.mp.solutions.pose.PoseLandmark
            ls, rs = lm[mp_pose.LEFT_SHOULDER.value], lm[mp_pose.RIGHT_SHOULDER.value]
            nose = lm[mp_pose.NOSE.value]
            # Shoulder level difference normalized to frame width.
            shoulder_diff = abs(ls.y - rs.y)
            shoulder_mid_x = (ls.x + rs.x) / 2
            # A simple frontal-view heuristic, not a medical posture assessment.
            if ls.visibility > 0.5 and rs.visibility > 0.5:
                if shoulder_diff > 0.075 or abs(nose.x - shoulder_mid_x) > 0.22:
                    posture = "Adjust posture"
                    messages.append("Your shoulders or head appear misaligned. Sit upright.")
                else:
                    posture = "Good"
            else:
                posture = "Move into camera view"
                messages.append("Move back or adjust lighting so your face and shoulders are visible.")
        else:
            posture = "Move into camera view"
            messages.append("Move back or adjust lighting so your face and shoulders are visible.")

        if face_result.multi_face_landmarks:
            face_lm = face_result.multi_face_landmarks[0].landmark
            # Approximate EAR using standard Face Mesh eye corner and lid landmarks.
            left = self._ear(face_lm, [33, 160, 158, 133, 153, 144])
            right = self._ear(face_lm, [362, 385, 387, 263, 373, 380])
            ear = (left + right) / 2
            eyes = "Take a break" if ear < 0.16 else "Normal"
            if eyes == "Take a break":
                messages.append("Your eyes look closed. Take a short screen break.")
        else:
            eyes = "Face not detected"
            messages.append("Keep your face centered and well lit within the camera frame.")

        return {"posture": posture, "eyes": eyes,
                "message": " ".join(messages) if messages else "Good. Keep a comfortable posture and take regular breaks."}

    @staticmethod
    def _ear(points, idx):
        p = [points[i] for i in idx]
        def dist(a, b):
            return math.hypot(a.x - b.x, a.y - b.y)
        horizontal = dist(p[0], p[3])
        if horizontal == 0:
            return 0
        return (dist(p[1], p[5]) + dist(p[2], p[4])) / (2 * horizontal)
