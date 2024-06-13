from django.apps import AppConfig


class LeavetrackingappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'LeaveTrackingApp'

    def ready(self):
        # Import receivers to register them
        import LeaveTrackingApp.receivers
