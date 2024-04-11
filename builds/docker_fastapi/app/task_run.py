from tasks import add
import time
# Call the 'add' task with a parameter of 5 seconds
result = add.delay(5)
print('Task started!')
# Wait for the result to be ready before printing it
while not result.ready():
    time.sleep(1)
print('Result:', result.get())