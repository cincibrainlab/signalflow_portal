from celery import Celery
import time
# Initialize the Celery application with a name and broker URL
app = Celery('tasks', broker='pyamqp://guest@localhost//')
# Define a simple task function that takes a parameter 'n' and sleeps for n seconds before returning.
@app.task
def add(n):
    time.sleep(n)
    return n * 2