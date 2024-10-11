import random
from loguru import logger

class Randomizer(object):
    def __init__(self):
        self.powerline_map = {
            1: {
                "apriltag_id": 1,
                "color": "red",
                "id": 1
            },
            2: {
                "apriltag_id": 2,
                "color": "blue",
                "id": 2
            },
            3: {
                "apriltag_id": 3,
                "color": "yellow",
                "id": 3
            },
            4: {
                "apriltag_id": 4,
                "color": "red",
                "id": 4
            },
            5: {
                "apriltag_id": 5,
                "color": "blue",
                "id": 5
            }
        }
        self.railroad_map = {
            1: {
                "apriltag_id": 1,
                "color": "red",
                "id": 1
            },
            2: {
                "apriltag_id": 3,
                "color": "yellow",
                "id": 2
            },
            3: {
                "apriltag_id": 2,
                "color": "blue",
                "id": 3
            },
            4: {
                "apriltag_id": 4,
                "color": "red",
                "id": 4
            },
            5: {
                "apriltag_id": 6,
                "color": "yellow",
                "id": 5
            },
            6: {
                "apriltag_id": 5,
                "color": "blue",
                "id": 6
            }
        }
        self.bridge_map = {
            1: {
                "apriltag_id": 3,
                "color": "yellow",
                "id": 1
            },
            2: {
                "apriltag_id": 1,
                "color": "red",
                "id": 2
            },
            3: {
                "apriltag_id": 5,
                "color": "blue",
                "id": 3
            },
            4: {
                "apriltag_id": 2,
                "color": "blue",
                "id": 4
            },
            5: {
                "apriltag_id": 4,
                "color": "red",
                "id": 5
            },
            6: {
                "apriltag_id": 6,
                "color": "yellow",
                "id": 6
            }
        }

        self.num_reds_remaining = 2
        self.num_blues_remaining = 2
        self.num_yellows_remaining = 2

        self.pole_A = None
        self.pole_B = None

        self.bridge_A = None
        self.bridge_B = None

        self.railroad_A = None
        self.railroad_B = None

    def randomize(self):
        solved = False

        while not solved:
            # print("starting while")
            self.reset()
            pole_A = None
            pole_B = None
            bridge_A = None
            bridge_B = None
            railroad_A = None
            railroad_B = None

            # start with power poles
            a = b = self.generate_random_num(5)
            pole_A = self.powerline_map[a]
            self.account_for_colors(pole_A["color"])

            #check for id collisions and color acceptance
            color_accepted = False
            i=0
            while b == a or not color_accepted:
                b = self.generate_random_num(5)
                color_accepted = self.account_for_colors(self.powerline_map[b]["color"], check=True)
                if i > 500 and not color_accepted:
                    break
                i+=1
            if color_accepted:
                pole_B = self.powerline_map[b]
            self.account_for_colors(pole_B["color"])


            # then do bridge
            color_accepted = False
            while not color_accepted:
                a = self.generate_random_num(6)
                color_accepted = self.account_for_colors(self.bridge_map[a]["color"], check=True)
                if i > 500 and not color_accepted:
                    break
                i+=1
            if color_accepted:
                bridge_A = self.bridge_map[a]
            self.account_for_colors(bridge_A["color"])

            #check for id collisions and color acceptance
            color_accepted = False
            while b == a or not color_accepted:
                b = self.generate_random_num(6)
                color_accepted = self.account_for_colors(self.bridge_map[b]["color"], check=True)
                if i > 500 and not color_accepted:
                    break
                i+=1
            if color_accepted:
                bridge_B = self.bridge_map[b]
            self.account_for_colors(bridge_B["color"])

            # then do railroad
            color_accepted = False
            while not color_accepted:
                a = self.generate_random_num(6)
                color_accepted = self.account_for_colors(self.railroad_map[a]["color"], check=True)
                if i > 500 and not color_accepted:
                    break
                i+=1
            if color_accepted:
                railroad_A = self.railroad_map[a]
            self.account_for_colors(railroad_A["color"])

            #check for id collisions and color acceptance
            color_accepted = False
            while b == a or not color_accepted:
                b = self.generate_random_num(6)
                color_accepted = self.account_for_colors(self.railroad_map[b]["color"], check=True)
                if i > 500 and not color_accepted:
                    break
                i+=1
            if color_accepted:
                railroad_B = self.railroad_map[b]
            self.account_for_colors(railroad_B["color"])

            if all([pole_A is not None,
                    pole_B is not None,
                    bridge_A is not None,
                    bridge_B is not None,
                    railroad_A is not None,
                    railroad_B is not None]):

                solved = True
                if pole_A["id"] < pole_B["id"]:
                    self.pole_A = pole_A
                    self.pole_B = pole_B
                else:
                    self.pole_B = pole_A
                    self.pole_A = pole_B

                if bridge_A["id"] < bridge_B["id"]:
                    self.bridge_A = bridge_A
                    self.bridge_B = bridge_B
                else:
                    self.bridge_B = bridge_A
                    self.bridge_A = bridge_B

                if railroad_A["id"] < railroad_B["id"]:
                    self.railroad_A = railroad_A
                    self.railroad_B = railroad_B
                else:
                    self.railroad_B = railroad_A
                    self.railroad_A = railroad_B

                pole_A_id = self.pole_A["id"] # type: ignore
                pole_A_color = self.pole_A["color"] # type: ignore
                pole_B_id = self.pole_B["id"] # type: ignore
                pole_B_color = self.pole_B["color"] # type: ignore
                bridge_A_id = self.bridge_A["id"] # type: ignore
                bridge_A_color = self.bridge_A["color"] # type: ignore
                bridge_B_id = self.bridge_B["id"] # type: ignore
                bridge_B_color = self.bridge_B["color"] # type: ignore
                railroad_A_id = self.railroad_A["id"] # type: ignore
                railroad_A_color = self.railroad_A["color"] # type: ignore
                railroad_B_id = self.railroad_B["id"] # type: ignore
                railroad_B_color = self.railroad_B["color"] # type: ignore

                # logger.debug(f"pole_A: id: {pole_A_id} color: {pole_A_color}")
                # logger.debug(f"pole_B: id: {pole_B_id} color: {pole_B_color}")
                # logger.debug(f"bridge_A: id: {bridge_A_id} color: {bridge_A_color}")
                # logger.debug(f"bridge_B: id: {bridge_B_id} color: {bridge_B_color}")
                # logger.debug(f"railroad_A: id: {railroad_A_id} color: {railroad_A_color}")
                # logger.debug(f"railroad_B: id: {railroad_B_id} color: {railroad_B_color}")


    def reset(self):
        self.num_reds_remaining = 2
        self.num_blues_remaining = 2
        self.num_yellows_remaining = 2

        self.pole_A = None
        self.pole_B = None

        self.crack_A = None
        self.crack_B = None

        self.railroad_A = None
        self.railroad_B = None

    def generate_random_num(self, max):
        return random.randint(1,max)

    def account_for_colors(self, color, check=False):
        if color == "red":
            if self.num_reds_remaining > 0:
                if check == True:
                    return True
                self.num_reds_remaining -=1
                return True
        elif color == "blue":
            if self.num_blues_remaining > 0:
                if check == True:
                    return True
                self.num_blues_remaining -=1
                return True
        elif color == "yellow":
            if self.num_yellows_remaining > 0:
                if check == True:
                    return True
                self.num_yellows_remaining -=1
                return True
        return False

if __name__ == "__main__":
    while True:
        randomizer = Randomizer()
        randomizer.randomize()
        print("done")
