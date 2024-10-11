import random
class Randomizer(object):
    def __init__(self):
        self.powerline_map = {
            1: {
                "apriltag_id": 1,
                "color": "red"
            },
            2: {
                "apriltag_id": 2,
                "color": "blue"
            },
            3: {
                "apriltag_id": 3,
                "color": "yellow"
            },
            4: {
                "apriltag_id": 4,
                "color": "red"
            },
            5: {
                "apriltag_id": 5,
                "color": "blue"
            }
        }
        self.railroad_map = {
            1: {
                "apriltag_id": 1,
                "color": "red"
            },
            2: {
                "apriltag_id": 3,
                "color": "yellow"
            },
            3: {
                "apriltag_id": 2,
                "color": "blue"
            },
            4: {
                "apriltag_id": 4,
                "color": "red"
            },
            5: {
                "apriltag_id": 6,
                "color": "yellow"
            },
            6: {
                "apriltag_id": 5,
                "color": "blue"
            }
        }
        self.bridge_map = {
            1: {
                "apriltag_id": 3,
                "color": "yellow"
            },
            2: {
                "apriltag_id": 1,
                "color": "red"
            },
            3: {
                "apriltag_id": 5,
                "color": "blue"
            },
            4: {
                "apriltag_id": 2,
                "color": "red"
            },
            5: {
                "apriltag_id": 4,
                "color": "yellow"
            },
            6: {
                "apriltag_id": 6,
                "color": "blue"
            }
        }

    def randomize(self):

        # start with power poles
        pole_A = pole_B = self.generate_random_num(5)
        while pole_B == pole_A:
            pole_B = self.generate_random_num(5)
        pole_A_at = self.powerline_map[pole_A]
        pole_B_at = self.powerline_map[pole_B]
        #then do bridge
        bridge_A = bridge_B = self.generate_random_num(6)
        # while bridge_B == bridge_A and :

        # then do railroad

    def generate_random_num(self, max):
        return random.randint(1,max)