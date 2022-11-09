import time

tasks = {}


def add_task(name, delay_ms, callback):
    global tasks
    tasks[name] = {
        'time': time.ticks_add(time.ticks_ms(), delay_ms),
        'callback': callback
    }


def exec_tasks(*args):
    global tasks

    now_ms = time.ticks_ms()
    ready = dict((k, v) for k, v in tasks.items()
                 if time.ticks_diff(v['time'], now_ms) < 0)

    for key, task in ready.items():
        del tasks[key]
        task['callback'](*args)

    return len(ready) > 0
