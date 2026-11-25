def notify(title, message):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, timeout=4)
    except Exception:
        # Notifications are optional; dashboard status remains available.
        pass
