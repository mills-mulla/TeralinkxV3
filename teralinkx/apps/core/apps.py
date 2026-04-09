# core/apps.py

from django.apps import AppConfig
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
# import random
# import json

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    # def ready(self):
    #     from django_celery_beat.models import PeriodicTask, IntervalSchedule

    #     # Prevent duplicate tasks
    #     task_map = {
    #         'task_query_unprocessed_checkoutrqs': random.randint(30, 40),
    #         'task_check_voucher_expiry': random.randint(60, 180),
    #         'task_check_session_expiry': random.randint(36000, 43200),
    #         'task_update_dhcp_model': random.randint(300, 1800),
    #         'task_update_active_users': random.randint(60, 300),
    #         'task_delete_pending': random.randint(300, 600),
    #     }

    #     for task_name, interval_seconds in task_map.items():
    #         schedule, _ = IntervalSchedule.objects.get_or_create(
    #             every=interval_seconds,
    #             period=IntervalSchedule.SECONDS
    #         )
    #         PeriodicTask.objects.update_or_create(
    #             name=task_name,
    #             defaults={
    #                 'interval': schedule,
    #                 'task': f'core.tasks.{task_name}',
    #                 'enabled': True,
    #                 'kwargs': json.dumps({})
    #             }
    #         )
