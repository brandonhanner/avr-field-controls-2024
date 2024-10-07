import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import match
import mqtt_client
import time
from loguru import logger


def mapRange(value, inMin, inMax, outMin, outMax):
    return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))


class Controller(object):
    def __init__(self):


        # create an MQTT client
        self.mqtt_client = mqtt_client.MQTTClient("mqtt", 1883)
        self.mqtt_client.register_callback("+/events/#", self.handle_events)

        # create a match
        self.match = match.MatchModel()

    def handle_events(self, topic: str, msg: dict):
        parts = topic.split("/")
        source = parts[0]
        channel = parts[1]
        subsystem = parts[2]

        # see if the source is a bridge
        if source in (
            [self.match.bridge.get_crack_ID("A"),self.match.bridge.get_crack_ID("B")]
        ):
            if subsystem in ["laser_detector"]:
                event_type = msg.get("event_type", None)
                if event_type == "hit":
                    self.match.bridge.repair_damage(source)

        elif source == "ui":
            event_type = msg.get("event_type", None)
            if event_type is not None:
                if event_type == "ui_toggle":
                    # logger.debug("got a toggle event")
                    self.match.handle_ui_toggles(msg.get("data"))
                else:
                    logger.debug("Got a normal event")
                    self.match.dispatch(event_type)

    def publish_score(self):
        # publish score
        current_score = self.match.calculate_score()
        self.mqtt_client.publish("ui/state/score", {"current_score": current_score})

        phase_i = self.match.calculate_phase_i()
        self.mqtt_client.publish("ui/state/phase_i_score", {"current_score": phase_i})

        phase_ii = self.match.calculate_phase_ii()
        self.mqtt_client.publish("ui/state/phase_ii_score", {"current_score": phase_ii})

        phase_iii = self.match.calculate_phase_iii()
        self.mqtt_client.publish("ui/state/phase_iii_score", {"current_score": phase_iii})

        phase_iv = self.match.calculate_phase_iv()
        self.mqtt_client.publish("ui/state/phase_iv_score", {"current_score": phase_iv})

    def publish_bridge_table(self):
        table_data = []
        row_data = {}
        row_data["Site"] = self.match.bridge.get_crack_ID("A")
        row_data["Damage Remaining"] = self.match.bridge.get_damage_remaining("A")
        row_data["State"] = "damaged" if self.match.bridge.get_damage_remaining("A") > 0 else "repaired"
        table_data.append(row_data)
        row_data["Site"] = self.match.bridge.get_crack_ID("B")
        row_data["Damage Remaining"] = self.match.bridge.get_damage_remaining("B")
        row_data["State"] = "damaged" if self.match.bridge.get_damage_remaining("B") > 0 else "repaired"

        self.mqtt_client.publish("ui/state/bridge_table_data", table_data)

    def publish_toggles(self):
        for key, value in self.match.ui_toggles.items():
            self.mqtt_client.publish(
                f"ui/state/{key}",
                {"data": value}
            )

    def publish_game_state(self):
        # publish the states
        state = self.match.sm.state.name  # type: ignore
        if state == "phase_1_state":
            state = "Phase 1"
        elif state == "phase_2_state":
            state = "Phase 2"
        elif state == "phase_3_state":
            state = "Phase 3"
        elif state == "phase_4_state":
            state = "Phase 4"
        elif state == "idle_state":
            state = "Idle"
        elif state == "staging_state":
            state = "Staging/Preheat"
        elif state == "post_match_state":
            state = "End Game"
        self.mqtt_client.publish("ui/state/match_state", {"state": state})

    def publish_timers(self):
        # publish time remainings
        time_left = time.strftime(
            "%M:%S", time.gmtime(self.match.phase_timer.time_remaining)
        )
        self.mqtt_client.publish("ui/state/phase_remaining", {"time": time_left})

        time_left = time.strftime(
            "%M:%S", time.gmtime(self.match.match_timer.time_remaining)
        )
        self.mqtt_client.publish("ui/state/match_remaining", {"time": time_left})

        time_left = 0
        for line in self.match.power_lines.lines:
            if line.sm.state.name == "heating_state":
                time_left = line.heater_timer.time_remaining

        self.mqtt_client.publish("ui/state/heater_countdown", {"time": time_left})

    def publish_railroad_damaged_spots(self):
        # publish the hot spot building
        self.mqtt_client.publish(
            "ui/state/railroad/damaged_spots",
            {
                "A":
                {
                    "id": self.match.railroad.get_damaged_spot_ID("A"),
                    "damaged": self.match.railroad.get_damage("A")
                },
                "B":
                {
                    "id": self.match.railroad.get_damaged_spot_ID("B"),
                    "damaged": self.match.railroad.get_damage("B")
                }
            },
        )

    def publish_bridge_damaged_spots(self):
        # publish the hot spot building
        self.mqtt_client.publish(
            "ui/state/bridge/damaged_spots",
            {
                "A":
                {
                    "id": self.match.bridge.get_crack_ID("A"),
                    "damage_remaining": self.match.bridge.get_damage_remaining("A")
                },
                "B":
                {
                    "id":  self.match.bridge.get_crack_ID("B"),
                    "damage_remaining": self.match.bridge.get_damage_remaining("B")
                }
            },
        )

    def publish_powerline_damaged_spots(self):
        # publish the hot spot building
        self.mqtt_client.publish(
            "ui/state/powerlines/damaged_spots",
            {
                "A":
                {
                    "id": self.match.power_lines.get_line_ID("A"),
                    "damaged": self.match.power_lines.get_damage("A")
                },
                "B":
                {
                    "id": self.match.power_lines.get_line_ID("B"),
                    "damaged": self.match.power_lines.get_damage("B")
                }
            },
        )


    def generate_LED_dict(self, strip):
        strip_len = 30
        data = {}
        data["pixel_data"] = []
        for i in range(0, strip_len):
            data["pixel_data"].append([0, 0, 0])

        # fire_level = building.current_fire_level
        # init = building.initial_fire_level
        # pixels_per_fs = 2 if init <= 8 else 1

        # if fire_level > (init // 2):
        #     left = (init // 2) * pixels_per_fs
        #     right = (fire_level - (init // 2)) * pixels_per_fs
        # elif fire_level <= (init // 2):
        #     left = fire_level * pixels_per_fs
        #     right = 0
        # else:
        #     left = 0
        #     right = 0

        # # do the first window's portion of the led strip
        # if left > 0:
        #     for i in range(0, left):
        #         data["pixel_data"][i] = [0, 0, 255]
        # # do the second window's portion of the led strip
        # if right > 0:
        #     for i in range(strip_len - 1, strip_len - 1 - right, -1):
        #         data["pixel_data"][i] = [0, 0, 255]

        return data
    # def publish_LED_bar_commands(self):
    #     data = self.generate_LED_dict(bridge = self.match.bridge)
    #     self.mqtt_client.publish(f"{entity_id}/progress_bar/set", data)

    def publish_railroad_commands(self):

        # railroad
        id_A = self.match.railroad.get_damaged_spot_ID("A")
        id_B = self.match.railroad.get_damaged_spot_ID("B")

        for spot in self.match.railroad.damaged_spots:
            if spot.id in [id_A, id_B]:
                self.mqtt_client.publish(
                    f"railroad/relay/set", {"channel": spot.id, "state": "on"}
                )
            else:
                self.mqtt_client.publish(
                    f"railroad/relay/set", {"channel": spot.id, "state": "off"}
                )
    def publish_bridge_commands(self):
        # bridge
        id_A = self.match.bridge.get_crack_ID("A")
        id_B = self.match.bridge.get_crack_ID("B")

        for spot in self.match.bridge.cracks:
            if spot.id in [id_A, id_B]:
                self.mqtt_client.publish(
                    f"bridge/relay/set", {"channel": spot.id, "state": "on"}
                )
            else:
                self.mqtt_client.publish(
                    f"bridge/relay/set", {"channel": spot.id, "state": "off"}
                )

    def publish_power_line_commands(self):
        heater_channel = 1
        for line in self.match.power_lines.lines:
            if line.sm.state.name == "heating_state":
                self.mqtt_client.publish(
                    f"power_line/relay/set", {"channel": line.id, "state": "on"}
                )
            else:
                self.mqtt_client.publish(
                    f"power_line/relay/set", {"channel": line.id, "state": "off"}
                )

    def run(self):
        self.mqtt_client.start_threaded()
        last_update_time = time.time()
        while True:
            if time.time() - last_update_time > .5:
                # publish UI data
                self.publish_score()
                self.publish_bridge_table()
                self.publish_game_state()
                self.publish_timers()
                self.publish_railroad_damaged_spots()
                self.publish_bridge_damaged_spots()
                self.publish_powerline_damaged_spots()
                # publish building commands
                self.publish_railroad_commands()
                self.publish_power_line_commands()
                self.publish_bridge_commands()
                # self.publish_LED_bar_commands()
                last_update_time = time.time()
            self.publish_toggles()
            time.sleep(0.1)


if __name__ == "__main__":
    controller = Controller()
    controller.run()
