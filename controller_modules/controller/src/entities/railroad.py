
import random
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from entities.apriltag import AprilTag

class DamagedSpot(object):
    def __init__(self, id: int, apriltag: AprilTag):
        self.id: int  = id
        self.apriltag: AprilTag = apriltag
        self.damaged = True

    def reset(self):
        self.damaged = True

class Railroad(object):
    def __init__(self):

        self.enabled = False
        # 1-6
        self.damaged_spots = []
        self.damaged_spots.append(DamagedSpot(1, AprilTag(1)))
        self.damaged_spots.append(DamagedSpot(2, AprilTag(3)))
        self.damaged_spots.append(DamagedSpot(3, AprilTag(2)))
        self.damaged_spots.append(DamagedSpot(4, AprilTag(4)))
        self.damaged_spots.append(DamagedSpot(5, AprilTag(6)))
        self.damaged_spots.append(DamagedSpot(6, AprilTag(5)))

        self.damaged_spot_A = None
        self.damaged_spot_B = None

        self.max_damaged_spots = 6

    def generate_random_id(self):
        return random.randint(0,self.max_damaged_spots-1)

    def randomize_damaged_spots(self):
        self.damaged_spot_A = self.damaged_spots[self.generate_random_id()]

        b = self.damaged_spots[self.generate_random_id()]
        while b.id == self.damaged_spot_A.id:
            b = self.damaged_spots[self.generate_random_id()]
        self.damaged_spot_B = b

    def get_damaged_spot_ID(self, which_spot):
        '''
        put in either 'A'or 'B' to get the spot which is damaged
        '''
        if which_spot == "A":
            return self.damaged_spot_A.id if self.damaged_spot_A is not None else 0
        else:
            return self.damaged_spot_B.id if self.damaged_spot_B is not None else 0

    def get_damage(self, which_spot):
        if which_spot == "A":
            return self.damaged_spot_A.damaged if self.damaged_spot_A is not None else False
        else:
            return self.damaged_spot_A.damaged if self.damaged_spot_A is not None else False

    def get_color(self, slot):

        if slot == "A" :
            return self.damaged_spot_A.apriltag.color if self.damaged_spot_A is not None else "None"
        if slot == "B" :
            return self.damaged_spot_B.apriltag.color if self.damaged_spot_B is not None else "None"
        else:
            raise ValueError("Gotta be A or B pal")

    def set_damage(self, slot, damage: bool):
            if self.enabled:
                if slot == "A" and self.damaged_spot_A is not None:
                    self.damaged_spot_A.damaged = damage
                if slot == "B" and self.damaged_spot_B is not None:
                    self.damaged_spot_B.damaged = damage

    def reset(self):
        self.enabled = False
        self.damaged_spot_A = None
        self.damaged_spot_B = None
        for spot in self.damaged_spots:
            spot.reset()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False