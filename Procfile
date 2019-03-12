web: gunicorn --chdir=/app/src website.wsgi:application --timeout 240 --graceful-timeout 230 --log-file -
# worker: python /app/src/website/celery/worker.py
# django_email_queue: python -m django_email_queue.worker
# always keep the task with the beat at max 1 process
#celery_with_beat: celery worker --workdir=/app/src --app=website.celery.app --loglevel debug --hostname worker@%%h --beat --heartbeat-interval 86400 --without-gossip --without-mingle --max-tasks-per-child=500 --without-heartbeat
# celery_with_beat: celery worker --workdir=/app/src --app=website.celery.app --loglevel debug --hostname worker@%%h --beat --heartbeat-interval 3600 --without-gossip --without-mingle --max-tasks-per-child=500
#                        worker --app=website.celery:app -l debug --autoscale=1,1
release: /app/bin/release
