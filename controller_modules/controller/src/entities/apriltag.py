class AprilTag(object):
    def __init__(self, id):
        self.id: int = id
        color_map = {
            1: "red",
            2: "blue",
            3: "yellow",
            4: "red",
            5: "blue",
            6: "yellow"
        }
        self.color: str = color_map[self.id]