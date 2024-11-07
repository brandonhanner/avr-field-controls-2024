from pysm import State, StateMachine, Event
from threading import Thread, Lock
from typing import Dict, List, Union, Any
import time
import timer
from loguru import logger
import random
import json
import re
import copy
from entities import power_lines
from entities import bridge
from entities import railroad
from entities import randomizer


class MatchModel(object):
    def __init__(self):

        self.score = 0

        with open('/configs/config.json', 'r') as file:
            self.config = json.load(file)

        self.power_lines = power_lines.Powerlines()
        self.bridge = bridge.Bridge()
        self.railroad = railroad.Railroad()
        self.randomizer = randomizer.Randomizer()

        self.phase_i_duration = self.config.get("phase_1_duration", 60)
        self.phase_ii_duration = self.config.get("phase_2_duration", 120)
        self.phase_iii_duration = self.config.get("phase_3_duration", 60)
        self.phase_iv_duration = self.config.get("phase_4_duration", 60)

        self.phase_timer = timer.Timer()
        self.match_timer = timer.Timer()

        self.ui_toggles_default = {
            "match_id": "",
            "m1_dexi_IR_beams_located": 0, # max 2?
            "m1_dexi_AT_recognized": 0,   # max 2?
            "m1_spheros_arrived_at_container_yard": 0, # max 3
            "m1_rvr_arrived_at_container_yard": False,
            "m1_rvr_autonomous_turns": 0, # max 3
            "m1_sphero_conex_boarding": 0, # max 3
            "m1_rvr_conex_delivery": 0, # max 2
            "m1_avr_conex_delivery": 0, # max 2
            "m1_avr_conex_delivery_precise": 0, # max 2
            "m1_sphero_repair_start_switches": 0, # max 2
            "m2_dexi_IR_beams_located": 0, # max 2
            "m2_dexi_AT_recognized": 0, # max 2
            "m2_sphero_conex_boarding": 0, # max 3
            "m2_rvr_conex_delivery": 0, # max 2
            "m2_avr_conex_delivery": 0, # max 2
            "m2_avr_conex_delivery_precise": 0, # max 2
            "m2_sphero_travel_to_work": 0, # max 3
            "m2_dexi_weld_repairs": 0, # max 2
            "m2_sphero_travel_to_container_yard": 0, # max 3
            "m2_sphero_travel_to_container_yard_via_avr": 0, # max 3
            "m3_avr_hotspots_located":0, # max 2
            "m3_dexi_AT_recognized":0, # max 2
            "m3_sphero_conex_boarding":0, # max 3
            "m3_rvr_conex_delivery":0, # max 2
            "m3_rvr_conex_delivery_precise":0, # max 2
            "m3_sphero_switch_reset":0, # max 2
            "m4_rvr_parked": False,
            "m4_sphero_parked": 0, # max 3
            "m4_dexi_parked": False,
            "m4_avr_parked": False,
            "m4_conex_returned_to_yard": 0, # max 3
            "m4_conex_2_stacks": 0,
            "m4_conex_3_stacks": 0,
            "m4_conex_4_stacks": 0,
            "m4_conex_5_stacks": 0,
            "m4_conex_6_stacks": 0,
        }
        self.ui_toggles = dict(self.ui_toggles_default)

        ###############################################################################

        ################### S T A T E  -  M A C H I N E   S T U F F ###################
        self.sm_lock = Lock()
        self.sm: StateMachine = StateMachine('match')

        self.idle_state = State('idle_state')
        self.idle_state.handlers = {
            "enter":self.idle_enter,
            "reset_match_event":self.idle_enter
        }
        self.staging_state = State('staging_state')
        self.staging_state.handlers = {
            "randomize_everything_event": self.sm_randomize_everything,
            "start_preheat_event": self.start_preheat,
        }
        self.phase_1_state = State('phase_1_state')
        self.phase_1_state.handlers = {
            "enter":self.phase_one_enter
        }
        self.phase_2_state = State('phase_2_state')
        self.phase_2_state.handlers = {
            "enter":self.phase_two_enter
        }
        self.phase_3_state = State('phase_3_state')
        self.phase_3_state.handlers = {
            "enter":self.phase_three_enter,
            # "exit":self.phase_three_exit,
        }
        self.phase_4_state = State('phase_4_state')
        self.phase_4_state.handlers = {
            "enter":self.phase_four_enter,
            # "exit":self.phase_four_exit,
        }
        self.post_match_state = State('post_match_state')
        self.post_match_state.handlers = {
            "enter": self.post_match_enter,
            "exit": self.post_match_exit
        }

        self.sm.add_state(self.idle_state, initial=True)
        self.sm.add_state(self.staging_state)
        self.sm.add_state(self.phase_1_state)
        self.sm.add_state(self.phase_2_state)
        self.sm.add_state(self.phase_3_state)
        self.sm.add_state(self.phase_4_state)
        self.sm.add_state(self.post_match_state)

        self.sm.add_transition(self.idle_state, self.staging_state, events=['new_match_event'])
        self.sm.add_transition(self.staging_state, self.phase_1_state, events=['match_start_event'])
        self.sm.add_transition(self.phase_1_state, self.phase_2_state, events=['phase_i_timeout_event'])
        self.sm.add_transition(self.phase_2_state, self.phase_3_state, events=['phase_ii_timeout_event'])
        self.sm.add_transition(self.phase_3_state, self.phase_4_state, events=['phase_iii_timeout_event'])
        self.sm.add_transition(self.phase_4_state, self.post_match_state, events=['phase_iv_timeout_event'])

        self.sm.add_transition(self.phase_1_state, self.post_match_state, events=['match_end_event'])
        self.sm.add_transition(self.phase_2_state, self.post_match_state, events=['match_end_event'])
        self.sm.add_transition(self.phase_3_state, self.post_match_state, events=['match_end_event'])
        self.sm.add_transition(self.phase_4_state, self.post_match_state, events=['match_end_event'])


        self.sm.add_transition(self.staging_state, self.idle_state, events=['reset_match_event'])
        self.sm.add_transition(self.post_match_state, self.idle_state, events=['reset_match_event'])

        self.sm.initialize()

    def dispatch(self, event):
        self.sm_lock.acquire()

        prev_state = self.sm.state.name #type: ignore
        if isinstance(event, str):
            event = Event(event)
        self.sm.dispatch(event)
        new_state = self.sm.state.name #type: ignore

        if new_state != prev_state:
            logger.debug(f"MATCH: State changed to {new_state}")

        self.sm_lock.release()

    def idle_enter(self, state, enter):
        self.reset_ui_toggles()
        self.match_timer.reset()
        self.phase_timer.reset()
        self.power_lines.reset()
        self.bridge.reset()
        self.railroad.reset()

    def phase_one_enter(self, state, event):
        logger.debug("starting phase 1 timer thread!")

        self.phase_timer.function = self.phase_i_timeout
        self.phase_timer.set_timeout(self.phase_i_duration)
        self.phase_timer.start()

        self.match_timer.function = None
        self.match_timer.set_timeout(self.phase_i_duration + self.phase_ii_duration + self.phase_iii_duration + self.phase_iv_duration)
        self.match_timer.start()
        self.railroad.enable()

    def phase_two_enter(self, state, event):
        logger.debug("starting phase 2 timer!")
        self.phase_timer.function = self.phase_ii_timeout
        self.phase_timer.set_timeout(self.phase_ii_duration)
        self.phase_timer.start()
        self.bridge.enable()
        self.start_preheat(None, None)

    def phase_three_enter(self, state, event):
        logger.debug("starting phase 3 timer!")
        self.phase_timer.function = self.phase_iii_timeout
        self.phase_timer.set_timeout(self.phase_iii_duration)
        self.phase_timer.start()
        self.power_lines.enable()

    def phase_four_enter(self, state, event):
        logger.debug("starting phase 4 timer!")
        self.phase_timer.function = self.phase_iv_timeout
        self.phase_timer.set_timeout(self.phase_iv_duration)
        self.phase_timer.start()

    def post_match_enter(self, state, event):
        self.match_timer.reset()
        self.phase_timer.reset()

    def post_match_exit(self, state, event):
        match_id = self.ui_toggles["match_id"]
        if match_id != "" and self.calculate_score() > 0:
                try:
                    score_json = copy.deepcopy(self.ui_toggles)
                    score_json["bridge"] = self.generate_bridge_data()
                    score_json["railroad"] = self.generate_railroad_data()
                    score_json["poles"] = self.generate_powerline_data()

                    score_json["phase_i_score"] = self.calculate_phase_i()
                    score_json["phase_ii_score"] = self.calculate_phase_ii()
                    score_json["phase_iii_score"] = self.calculate_phase_iii()
                    score_json["phase_iv_score"] = self.calculate_phase_iv()
                    score_json["total_score"] = self.calculate_score()

                    filename = match_id
                    filename = filename.replace("-", "_")
                    filename = "".join([c for c in filename if re.match(r'\w', c)])
                    with open(f"/logs/{filename}.json","w") as file:
                        file.write(json.dumps(score_json, indent=2))
                except Exception as e:
                    logger.debug("Score save failed")


    def sm_randomize_everything(self, state, event):
        logger.debug(f"Randomizing Everything")
        self.randomizer.randomize()
        self.bridge.crack_A = self.bridge.cracks[self.randomizer.bridge_A["id"]-1] # type: ignore
        self.bridge.crack_B = self.bridge.cracks[self.randomizer.bridge_B["id"]-1] # type: ignore

        self.railroad.damaged_spot_A = self.railroad.damaged_spots[self.randomizer.railroad_A["id"]-1] #type: ignore
        self.railroad.damaged_spot_B = self.railroad.damaged_spots[self.randomizer.railroad_B["id"]-1] #type: ignore

        self.power_lines.damaged_spot_A = self.power_lines.lines[self.randomizer.pole_A["id"]-1] #type: ignore
        self.power_lines.damaged_spot_B = self.power_lines.lines[self.randomizer.pole_B["id"]-1] #type: ignore

    def phase_i_timeout(self):
         self.dispatch(Event("phase_i_timeout_event"))

    def phase_ii_timeout(self):
         self.dispatch(Event("phase_ii_timeout_event"))

    def  phase_iii_timeout(self):
         self.dispatch(Event("phase_iii_timeout_event"))

    def  phase_iv_timeout(self):
         self.dispatch(Event("phase_iv_timeout_event"))

    def start_preheat(self, state, event):
        if self.power_lines.damaged_spot_A is not None and self.power_lines.damaged_spot_B is not None:
            if self.power_lines.damaged_spot_A.id != 0 and self.power_lines.damaged_spot_B.id != 0:
                self.power_lines.damaged_spot_A.ignite()
                self.power_lines.damaged_spot_B.ignite()

    ########################################################
    def calculate_phase_i(self):
        score = 0

        score = score + (self.ui_toggles["m1_dexi_IR_beams_located"] * 3)
        score = score + (self.ui_toggles["m1_dexi_AT_recognized"] * 3)
        score = score + (self.ui_toggles["m1_spheros_arrived_at_container_yard"])
        score = score + (1 if self.ui_toggles["m1_rvr_arrived_at_container_yard"] == True else 0)
        score = score + (self.ui_toggles["m1_rvr_autonomous_turns"] * 2)
        score = score + (self.ui_toggles["m1_sphero_conex_boarding"])
        score = score + (self.ui_toggles["m1_rvr_conex_delivery"])
        score = score + (self.ui_toggles["m1_avr_conex_delivery"] * 3)
        score = score + (self.ui_toggles["m1_avr_conex_delivery_precise"] * 2)
        score = score + (self.ui_toggles["m1_sphero_repair_start_switches"])

        return score

    def calculate_phase_ii(self):
        score = 0

        # only run this calc during phase 2
        if self.sm.state.name == "phase_2_state":
            repaired = 0
            if self.bridge.crack_A.damage_remaining == 0:
                repaired += 1
            if self.bridge.crack_B.damage_remaining == 0:
                repaired +=1
            self.ui_toggles["m2_dexi_weld_repairs"] = repaired

        score = score + (self.ui_toggles["m2_dexi_IR_beams_located"] * 3)
        score = score + (self.ui_toggles["m2_dexi_AT_recognized"] * 3)
        score = score + (self.ui_toggles["m2_sphero_conex_boarding"])
        score = score + (self.ui_toggles["m2_rvr_conex_delivery"])
        score = score + (self.ui_toggles["m2_avr_conex_delivery"]* 3)
        score = score + (self.ui_toggles["m2_avr_conex_delivery_precise"] * 2)
        score = score + (self.ui_toggles["m2_sphero_travel_to_work"])
        score = score + (self.ui_toggles["m2_dexi_weld_repairs"] * 10)
        score = score + (self.ui_toggles["m2_sphero_travel_to_container_yard"])
        score = score + (self.ui_toggles["m2_sphero_travel_to_container_yard_via_avr"] * 2)

        return score

    def calculate_phase_iii(self):
        score = 0
        score = score + (self.ui_toggles["m3_avr_hotspots_located"] * 10)
        score = score + (self.ui_toggles["m3_dexi_AT_recognized"] * 3)
        score = score + (self.ui_toggles["m3_sphero_conex_boarding"])
        score = score + (self.ui_toggles["m3_rvr_conex_delivery"]* 3)
        score = score + (self.ui_toggles["m3_rvr_conex_delivery_precise"] * 2)
        score = score + (self.ui_toggles["m3_sphero_switch_reset"] * 2)
        return score

    def calculate_phase_iv(self):
        score = 0
        score = score + (3 if self.ui_toggles["m4_rvr_parked"] == True else 0)
        score = score + (self.ui_toggles["m4_sphero_parked"])
        score = score + (3 if self.ui_toggles["m4_dexi_parked"] == True else 0)
        score = score + (3 if self.ui_toggles["m4_avr_parked"] == True else 0)

        # the complicated one....
        score = score + (self.ui_toggles["m4_conex_returned_to_yard"] * 2)

        score = score + (self.ui_toggles["m4_conex_2_stacks"])
        score = score + (self.ui_toggles["m4_conex_3_stacks"] * 3)
        score = score + (self.ui_toggles["m4_conex_4_stacks"] * 5)
        score = score + (self.ui_toggles["m4_conex_5_stacks"] * 7)
        score = score + (self.ui_toggles["m4_conex_6_stacks"] * 20)
        return score

    def calculate_score(self):
        #phase I
        phase_i = self.calculate_phase_i()

        #phase 2 vars
        phase_ii = self.calculate_phase_ii()

        #phase 3 vars
        phase_iii = self.calculate_phase_iii()

        #phase 4 vars
        phase_iv = self.calculate_phase_iv()

        cumulative = phase_i + phase_ii + phase_iii + phase_iv

        return cumulative

    def reset_ui_toggles(self):
        self.ui_toggles = dict(self.ui_toggles_default)

    def handle_ui_toggles(self, data):
        toggle = data.get("toggle", None)
        payload = data.get("payload", None)
        if toggle in self.ui_toggles.keys():
            self.ui_toggles[toggle] = payload
        else:
            logger.debug(f"{toggle} not in toggles dict")

    def generate_powerline_data(self):
        data = {
                    "A":
                    {
                        "id": self.power_lines.get_line_ID("A"),
                        "damaged": self.power_lines.get_damage("A"),
                        "color": self.power_lines.get_color("A")
                    },
                    "B":
                    {
                        "id": self.power_lines.get_line_ID("B"),
                        "damaged": self.power_lines.get_damage("B"),
                        "color": self.power_lines.get_color("B")
                    }
                }
        return data
    def generate_bridge_data(self):
        data = {
                    "A":
                    {
                        "id": self.bridge.get_crack_ID("A"),
                        "damage_remaining": self.bridge.get_damage_remaining("A"),
                        "color": self.bridge.get_color("A")
                    },
                    "B":
                    {
                        "id":  self.bridge.get_crack_ID("B"),
                        "damage_remaining": self.bridge.get_damage_remaining("B"),
                        "color": self.bridge.get_color("B")
                    }
               }
        return data
    def generate_railroad_data(self):
        data = {
                    "A":
                    {
                        "id": self.railroad.get_damaged_spot_ID("A"),
                        "damaged": self.railroad.get_damage("A"),
                        "color": self.railroad.get_color("A")
                    },
                    "B":
                    {
                        "id": self.railroad.get_damaged_spot_ID("B"),
                        "damaged": self.railroad.get_damage("B"),
                        "color": self.railroad.get_color("B")
                    }
               }
        return data
