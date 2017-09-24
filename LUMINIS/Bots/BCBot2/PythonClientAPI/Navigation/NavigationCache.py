from zipfile import ZipFile

from PythonClientAPI.Game.Enums import Direction

class NavigationCache:
    def __init__(self):
        self.navigation_data = []
        self.loaded = False

    def deserialize_nav_data(self, array):
        d1 = array[0]
        d2 = array[1]
        d3 = array[2]
        d4 = array[3]
        d5 = array[4]

        data = [[[[[[] for i5 in range(d5)] for i4 in range(d4)] for i3 in range(d3)] for i2 in range(d2)] for i1 in range(d1)]
        for i1 in range(d1):
            for i2 in range(d2):
                for i3 in range(d3):
                    for i4 in range(d4):
                        for i5 in range(d5):
                            index = 5 + i1 * d2 * d3 * d4 * d5 + i2 * d3 * d4 * d5 + i3 * d4 * d5 + i4 * d5 + i5
                            data[i1][i2][i3][i4][i5] = [array[index]]

        return data

    def load_compiled_data(self, file):
        with ZipFile(file) as zip_file:
            info = zip_file.getinfo("data")

            expected_size = info.file_size

            data = zip_file.read('data')

            if len(data) != expected_size:
                raise EOFError("Expected " + str(expected_size) + " bytes, got " + str(len(data)))

            self.navigation_data = self.deserialize_nav_data(data)
            self.loaded = True

    def get_next_direction_in_path(self, position, target):
        return Direction.INDEX_TO_DIRECTION[self.navigation_data[position[0]][position[1]][target[0]][target[1]][0][0]]

    def get_distance(self, position, target):
        return self.navigation_data[position[0]][position[1]][target[0]][target[1]][1][0]

navigation_cache = NavigationCache()