import random
from typing import Union
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from entities.apriltag import AprilTag

class Crack(object):
    def __init__(self, id: int, apriltag: AprilTag):
        self.id:int  = id
        self.apriltag = apriltag
        self.init_damage = 5
        self.damage_remaining = self.init_damage

    def reset(self):
        self.damage_remaining = self.init_damage

    def repair_damage(self):
        if self.damage_remaining > 0:
            self.damage_remaining -= 1


class Bridge(object):
    def __init__(self):

        self.enabled = False
        # 1-6
        self.cracks = []

        self.cracks.append(Crack(1, AprilTag(3)))
        self.cracks.append(Crack(2, AprilTag(1)))
        self.cracks.append(Crack(3, AprilTag(5)))
        self.cracks.append(Crack(4, AprilTag(4)))
        self.cracks.append(Crack(5, AprilTag(2)))
        self.cracks.append(Crack(6, AprilTag(6)))

        self.crack_A: Union[Crack, None] = None
        self.crack_B: Union[Crack, None] = None

        self.max_damaged_spots = 6

    def generate_random_id(self):
        return random.randint(0, self.max_damaged_spots-1)

    def reset(self):
        self.enabled = False
        self.crack_A = None
        self.crack_B = None
        for crack in self.cracks:
            crack.reset()

    def randomize_damaged_spots(self):
        '''
        assign two random spots to be damaged and make sure they arent the same
        '''
        self.crack_A = self.cracks[self.generate_random_id()]

        b = self.cracks[self.generate_random_id()]

        while b.id == self.crack_A.id: #type: ignore
            b = self.cracks[self.generate_random_id()]

        self.crack_B = b

        if self.crack_B.id < self.crack_A.id:
            temp = self.crack_A
            self.crack_A = self.crack_B
            self.crack_B = temp


    def get_crack_ID(self, which_spot):
        '''
        put in either 'A'or 'B' to get the spot which is damaged
        '''
        if which_spot == "A":
            return self.crack_A.id if self.crack_A is not None else 0
        else:
            return self.crack_B.id if self.crack_B is not None else 0

    def get_damage_remaining(self, which_spot):
        '''
        put in either 'A'or 'B' to get the remaining damage for that spot
        '''
        if which_spot == "A":
            return self.crack_A.damage_remaining if self.crack_A is not None else 0
        else:
            return self.crack_B.damage_remaining if self.crack_B is not None else 0

    def get_color(self, which_spot):
        '''
        put in either 'A'or 'B' to get the remaining damage for that spot
        '''
        if which_spot == "A":
            return self.crack_A.apriltag.color if self.crack_A is not None else "None"
        else:
            return self.crack_B.apriltag.color if self.crack_B is not None else "None"

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def repair_damage(self, ID):
        if self.enabled and all([self.crack_A is not None, self.crack_B is not None]):
            if ID == self.crack_A.id: #type: ignore
                self.crack_A.repair_damage()  #type: ignore
            elif ID == self.crack_B.id:  #type: ignore
                self.crack_B.repair_damage()  #type: ignore
