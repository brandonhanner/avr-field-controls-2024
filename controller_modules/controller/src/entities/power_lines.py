import random
import sys
sys.path.append("..") # Adds higher directory to python modules path.
import timer
from pysm import State, StateMachine, Event
from loguru import logger
from threading import Lock, Thread
import time
from entities.apriltag import AprilTag
from typing import List

class PowerLine(object):
    def __init__(self, id: int, apriltag: AprilTag):
        self.id:int  = id
        self.apriltag: AprilTag = apriltag
        self.heater_timer = timer.Timer()
        self.heater_duration = 180
        self.damaged = False

        #################### S T A T E  M A C H I N E   S T U F F ####################
        self.sm_lock = Lock()

        self.sm = StateMachine("power_line")

        self.idle_state = State("idle_state")
        self.idle_state.handlers = {
            "enter":self.idle_enter
        }
        self.heating_state = State("heating_state")
        self.heating_state.handlers = {
            "enter":self.heating_enter
        }

        self.sm.add_state(self.idle_state, initial=True)
        self.sm.add_state(self.heating_state)

        self.sm.add_transition(
            self.idle_state, self.heating_state, events=["ignition_event"]
        )
        self.sm.add_transition(
            self.heating_state, self.idle_state, events=["reset_event"]
        )

        self.sm.initialize()

    def dispatch(self, event):
        self.sm_lock.acquire()
        prev_state = self.sm.state.name  # type: ignore
        if isinstance(event, str):
            event = Event(event)
        self.sm.dispatch(event)
        new_state = self.sm.state.name  # type: ignore

        if new_state != prev_state:
            logger.debug(
                f"POLE {self.id}: State changed to {new_state} from {prev_state} on {event.name}"
            )
        self.sm_lock.release()

    def heating_enter(self, state, event):
        logger.debug("starting heater timer thread!")

        self.heater_timer.function = self.heating_timeout
        self.heater_timer.set_timeout(self.heater_duration)
        self.heater_timer.start()

    def idle_enter(self, state, event):
        self.heater_timer.reset()

    def heating_timeout(self):
        self.reset()

    def reset(self):
        self.dispatch(Event("reset_event"))
        self.damaged = False

    def ignite(self):
        self.dispatch(Event("ignition_event"))
        self.damaged = True

    def repair_damage(self):
        self.damage = False

class Powerlines(object):
    def __init__(self):

        self.enabled = False

        self.lines: List[PowerLine] = []
        self.lines.append(PowerLine(1, AprilTag(1)))
        self.lines.append(PowerLine(2, AprilTag(2)))
        self.lines.append(PowerLine(3, AprilTag(3)))
        self.lines.append(PowerLine(4, AprilTag(4)))
        self.lines.append(PowerLine(5, AprilTag(5)))

        self.max_power_poles = 5

        self.damaged_spot_A: PowerLine = None #type: ignore
        self.damaged_spot_B: PowerLine = None #type: ignore

    def generate_random_id(self):
        return random.randint(0,self.max_power_poles-1)

    def randomize_damaged_spots(self):
        self.damaged_spot_A = self.lines[self.generate_random_id()]

        b = self.lines[self.generate_random_id()]
        while b.id == self.damaged_spot_A.id:
            b = self.lines[self.generate_random_id()]
        self.damaged_spot_B = b

    def get_line_ID(self, which_spot):
        '''
        put in either 'A'or 'B' to get the spot which is damaged
        '''
        if which_spot == "A":
            return self.damaged_spot_A.id if self.damaged_spot_A is not None else 0
        else:
            return self.damaged_spot_B.id if self.damaged_spot_B is not None else 0

    def reset(self):
        self.enabled = False
        for line in self.lines:
            line.reset()
        self.damaged_spot_A = None #type: ignore
        self.damaged_spot_B = None #type: ignore

    def ignite_poles(self):
        if self.damaged_spot_A is not None and self.damaged_spot_B is not None:
            self.damaged_spot_A.ignite()
            self.damaged_spot_B.ignite()

    def set_damage(self, slot, damage: bool):
        if self.enabled:
            if slot == "A" and self.damaged_spot_A is not None:
                self.damaged_spot_A.damaged = damage
            if slot == "B" and self.damaged_spot_B is not None:
                self.damaged_spot_B.damaged = damage
            else:
                raise ValueError("Gotta be A or B pal")

    def get_damage(self, slot):

        if slot == "A" :
            return self.damaged_spot_A.damaged if self.damaged_spot_A is not None else False
        if slot == "B" :
            return self.damaged_spot_B.damaged if self.damaged_spot_B is not None else False
        else:
            raise ValueError("Gotta be A or B pal")

    def get_color(self, slot):

        if slot == "A" :
            return self.damaged_spot_A.apriltag.color if self.damaged_spot_A is not None else "None"
        if slot == "B" :
            return self.damaged_spot_B.apriltag.color if self.damaged_spot_B is not None else "None"
        else:
            raise ValueError("Gotta be A or B pal")

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False