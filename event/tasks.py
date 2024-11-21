from datetime import datetime
import pytz
from celery import shared_task
from .models import TenderDate
import logging
@shared_task
def check_event_dates():
    logging.info("Executing Task")
    # Get the current time in Asia/Bishkek timezone
    tz = pytz.timezone('Asia/Bishkek')
    now = datetime.now(tz)

    # Find all EventDate objects where date_time is in the past and status is False
    expired_dates = TenderDate.objects.filter(date_time__lt=now, status=False)

    # Update the status of all expired dates to True
    expired_dates.update(status=False)

    # Log a message to confirm that the task has run
    print(f"Checked {expired_dates.count()} expired event dates.")
