
import random

class DamagedSpot(object):
    def __init__(self, id: int, color: str):
        self.id:int  = id
        self.color: str = color
        self.damaged = True

    def reset(self):
        self.damaged = True

class Railroad(object):
    def __init__(self):

        self.enabled = False
        # 1-6

        self.damaged_spots = []
        self.damaged_spots.append(DamagedSpot(1, "red"))
        self.damaged_spots.append(DamagedSpot(2, "blue"))
        self.damaged_spots.append(DamagedSpot(3, "yellow"))
        self.damaged_spots.append(DamagedSpot(4, "red"))
        self.damaged_spots.append(DamagedSpot(5, "blue"))
        self.damaged_spots.append(DamagedSpot(6, "yellow"))

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

    def set_damage(self, slot, damage: bool):
            if self.enabled:
                if slot == "A" and self.damaged_spot_A is not None:
                    self.damaged_spot_A.damaged = damage
                if slot == "B" and self.damaged_spot_B is not None:
                    self.damaged_spot_B.damaged = damage

    def reset(self):
        self.enabled = False
        for spot in self.damaged_spots:
            spot.reset()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False