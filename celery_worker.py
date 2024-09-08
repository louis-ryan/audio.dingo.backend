import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery import Celery

app = Celery('video_processor')

app.config_from_object('celeryconfig')

app.autodiscover_tasks(['modules'])

if __name__ == '__main__':
    app.start()