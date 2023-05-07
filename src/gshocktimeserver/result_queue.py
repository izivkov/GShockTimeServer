class KeyedResult:
    def __init__(self, key, result):
        self.key = key
        self.result = result

    def __str__(self):
        return "KeyedResult(key='{}', result={})".format(self.key, self.result)


class ResultQueue:
    def __init__(self):
        self.keyed_result_map = {}

    def enqueue(self, element):
        self.keyed_result_map[element.key.upper()] = element.result

    def dequeue(self, _key):
        if not self.keyed_result_map:
            return None
        else:
            key = _key.upper()
            value = self.keyed_result_map[key]
            del self.keyed_result_map[key]
            return value

    def is_empty(self):
        return not bool(self.keyed_result_map)

    def size(self):
        return len(self.keyed_result_map)

    def clear(self):
        self.keyed_result_map.clear()


result_queue = ResultQueue()
