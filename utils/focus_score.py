def calculate_focus_score(good_frames, total_frames, posture_events, eye_alerts):
    if total_frames <= 0:
        return 0
    posture_ratio = good_frames / total_frames
    penalty = min(0.25, (posture_events + eye_alerts) / max(1, total_frames) * 2)
    return max(0, min(100, round(posture_ratio * 100 - penalty * 100)))
