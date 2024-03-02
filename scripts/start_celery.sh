#/bin/bash

celery -A src.worker.celery_app worker -l info --pool=solo -E
