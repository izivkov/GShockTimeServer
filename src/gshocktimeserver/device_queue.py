import queue


class DeviceQueue:
    def __init__(self):
        self.q = queue.Queue()

    def get(self):
        return self.q.get(block=True, timeout=None)

    def put(self, item):
        self.q.put(item)


device_queue = DeviceQueue()
