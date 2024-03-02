#/bin/bash
celery -A src.worker.celery_app flower --port=5555
