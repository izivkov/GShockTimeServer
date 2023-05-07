class KeyedResult:
    def __init__(self, key, result):
        self.key = key
        self.result = result

    def __str__(self):
        return "KeyedResult(key='{}', result={})".format(self.key, self.result)


class ResultQueue:
    def __init__(self):
        self.keyedResultMap = {}

    def enqueue(self, element):
        self.keyedResultMap[element.key.upper()] = element.result

    def dequeue(self, _key):
        if not self.keyedResultMap:
            return None
        else:
            key = _key.upper()
            value = self.keyedResultMap[key]
            del self.keyedResultMap[key]
            return value

    def isEmpty(self):
        return not bool(self.keyedResultMap)

    def size(self):
        return len(self.keyedResultMap)

    def clear(self):
        self.keyedResultMap.clear()


result_queue = ResultQueue()
