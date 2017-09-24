import heapq

class PriorityQueue:
    def __init__(self):
        self.count = 0
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def poll(self):
        return heapq.heappop(self.items)[2]

    def add(self, item, priority):
        heapq.heappush(self.items, (priority, self.count, item))
        self.count += 1

class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def poll(self):
        return self.items.pop(0)

    def add(self, item):
        self.items.append(item)

def recursively_flatten_list(L, flattened = []):
    if not isinstance(L, list):
        flattened.append(L)
    else:
        for item in L:
            recursively_flatten_list(item, flattened)
        return flattened
