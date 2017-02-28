"""
Provides classes for the Telemetry Data output by Project CARS.
"""

from racedata.Packet import Packet


class TelemetryDataPacket(Packet):
    """Class representing Telemetry Data.

    The main type of packet output by Project CARS.

    The telemetry data packets have a length of 1367 and is packet type 0.
    """

    _packet_string = "=HB"
    _packet_string += "B"
    _packet_string += "bb"
    _packet_string += "BBbBB"
    _packet_string += "B"
    _packet_string += "21f"
    _packet_string += "H"
    _packet_string += "B"
    _packet_string += "B"
    _packet_string += "hHhHHBBBBBbffHHBBbB"
    _packet_string += "22f"
    _packet_string += "8B12f8B8f12B4h20H16f4H"
    _packet_string += "2f"
    _packet_string += "2B"
    _packet_string += "bbBbbb"

    _packet_string += "hhhHBBBBf" * 56
    
    _packet_string += "fBBB"

    def __init__(self, packet_data: bytes):
        """Initialization of TelemetryDataPacket object.
        
        Args:
            packet_data: Packed binary data captured from the Project CARS UDP
                broadcast.
        """
        super().__init__(packet_data)
        
        self._game_session_state = int(self._unpacked_data.popleft())

        self.viewed_participant_index = int(self._unpacked_data.popleft())
        self.num_participants = int(self._unpacked_data.popleft())

        self.unfiltered_throttle = int(self._unpacked_data.popleft())
        self.unfiltered_brake = int(self._unpacked_data.popleft())
        self.unfiltered_steering = int(self._unpacked_data.popleft())
        self.unfiltered_clutch = int(self._unpacked_data.popleft())
        self._race_state_flags = int(self._unpacked_data.popleft())

        self.laps_in_event = int(self._unpacked_data.popleft())

        self.best_lap_time = float(self._unpacked_data.popleft())
        self.last_lap_time = float(self._unpacked_data.popleft())
        self.current_time = float(self._unpacked_data.popleft())
        self.split_time_ahead = float(self._unpacked_data.popleft())
        self.split_time_behind = float(self._unpacked_data.popleft())
        self.split_time = float(self._unpacked_data.popleft())
        self.event_time_remaining = float(self._unpacked_data.popleft())
        self.personal_fastest_lap_time = float(
            self._unpacked_data.popleft())
        self.world_fastest_lap_time = float(self._unpacked_data.popleft())
        self.current_s1_time = float(self._unpacked_data.popleft())
        self.current_s2_time = float(self._unpacked_data.popleft())
        self.current_s3_time = float(self._unpacked_data.popleft())
        self.fastest_s1_time = float(self._unpacked_data.popleft())
        self.fastest_s2_time = float(self._unpacked_data.popleft())
        self.fastest_s3_time = float(self._unpacked_data.popleft())
        self.personal_fastest_s1_time = float(
            self._unpacked_data.popleft())
        self.personal_fastest_s2_time = float(
            self._unpacked_data.popleft())
        self.personal_fastest_s3_time = float(
            self._unpacked_data.popleft())
        self.world_fastest_s1_time = float(self._unpacked_data.popleft())
        self.world_fastest_s2_time = float(self._unpacked_data.popleft())
        self.world_fastest_s3_time = float(self._unpacked_data.popleft())

        self._joypad = int(self._unpacked_data.popleft())

        self._highest_flag = int(self._unpacked_data.popleft())

        self._pit_mode_schedule = int(self._unpacked_data.popleft())

        self.oil_temp = int(self._unpacked_data.popleft())
        self.oil_pressure = int(self._unpacked_data.popleft())
        self.water_temp = int(self._unpacked_data.popleft())
        self.water_pressure = int(self._unpacked_data.popleft())
        self.fuel_pressure = int(self._unpacked_data.popleft())
        self._car_flags = int(self._unpacked_data.popleft())
        self.fuel_capacity = int(self._unpacked_data.popleft())
        self.brake = int(self._unpacked_data.popleft())
        self.throttle = int(self._unpacked_data.popleft())
        self.clutch = int(self._unpacked_data.popleft())
        self.steering = int(self._unpacked_data.popleft())
        self.fuel_level = float(self._unpacked_data.popleft())
        self.speed = float(self._unpacked_data.popleft())
        self.rpm = int(self._unpacked_data.popleft())
        self.max_rpm = int(self._unpacked_data.popleft())
        self._gear_num_gears = int(self._unpacked_data.popleft())
        self.boost_amount = int(self._unpacked_data.popleft())
        self.enforced_pit_stop_lap = int(self._unpacked_data.popleft())
        self._crash_state = int(self._unpacked_data.popleft())

        self.odometer = float(self._unpacked_data.popleft())

        """
        VEC_X = 0
        VEC_Y = 1
        VEC_Z = 2
        """
        self.orientation = list()
        self.local_velocity = list()
        self.world_velocity = list()
        self.angular_velocity = list()
        self.local_acceleration = list()
        self.world_acceleration = list()
        self.extents_centre = list()
        for _ in range(3):
            self.orientation.append(float(
                self._unpacked_data.popleft()))
        for _ in range(3):
            self.local_velocity.append(float(
                self._unpacked_data.popleft()))
        for _ in range(3):
            self.world_velocity.append(float(
                self._unpacked_data.popleft()))
        for _ in range(3):
            self.angular_velocity.append(float(
                self._unpacked_data.popleft()))
        for _ in range(3):
            self.local_acceleration.append(float(
                self._unpacked_data.popleft()))
        for _ in range(3):
            self.world_acceleration.append(float(
                self._unpacked_data.popleft()))
        for _ in range(3):
            self.extents_centre.append(float(
                self._unpacked_data.popleft()))

        """
        TYRE_FRONT_LEFT = 0
        TYRE_FRONT_RIGHT = 1
        TYRE_REAR_LEFT = 2
        TYRE_REAR_RIGHT = 3
        """
        self._tyre_flags = list()

        """
        TERRAIN_ROAD = 0,
        TERRAIN_LOW_GRIP_ROAD = 1
        TERRAIN_BUMPY_ROAD1 = 2
        TERRAIN_BUMPY_ROAD2 = 3
        TERRAIN_BUMPY_ROAD3 = 4
        TERRAIN_MARBLES = 5
        TERRAIN_GRASSY_BERMS = 6
        TERRAIN_GRASS = 7
        TERRAIN_GRAVEL = 8
        TERRAIN_BUMPY_GRAVEL = 9
        TERRAIN_RUMBLE_STRIPS = 10
        TERRAIN_DRAINS = 11
        TERRAIN_TYREWALLS = 12
        TERRAIN_CEMENTWALLS = 13
        TERRAIN_GUARDRAILS = 14
        TERRAIN_SAND = 15
        TERRAIN_BUMPY_SAND = 16
        TERRAIN_DIRT = 17
        TERRAIN_BUMPY_DIRT = 18
        TERRAIN_DIRT_ROAD = 19
        TERRAIN_BUMPY_DIRT_ROAD = 20
        TERRAIN_PAVEMENT = 21
        TERRAIN_DIRT_BANK = 22
        TERRAIN_WOOD = 23
        TERRAIN_DRY_VERGE = 24
        TERRAIN_EXIT_RUMBLE_STRIPS = 25
        TERRAIN_GRASSCRETE = 26
        TERRAIN_LONG_GRASS = 27
        TERRAIN_SLOPE_GRASS = 28
        TERRAIN_COBBLES = 29
        TERRAIN_SAND_ROAD = 30
        TERRAIN_BAKED_CLAY = 31
        TERRAIN_ASTROTURF = 32
        TERRAIN_SNOWHALF = 33
        TERRAIN_SNOWFULL = 34
        """
        self.terrain = list()
        self.tyre_y = list()
        self.tyre_rps = list()
        self.tyre_slip_speed = list()
        self.tyre_temp = list()
        self.tyre_grip = list()
        self.tyre_height_above_ground = list()
        self.tyre_lateral_stiffness = list()
        self.tyre_wear = list()
        self.brake_damage = list()
        self.suspension_damage = list()
        self.brake_temp = list()
        self.tyre_tread_temp = list()
        self.tyre_layer_temp = list()
        self.tyre_carcass_temp = list()
        self.tyre_rim_temp = list()
        self.tyre_internal_air_temp = list()
        self.wheel_local_position_y = list()
        self.ride_height = list()
        self.suspension_travel = list()
        self.suspension_velocity = list()
        self.air_pressure = list()

        for _ in range(4):
            self._tyre_flags.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.terrain.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_y.append(float(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_rps.append(float(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_slip_speed.append(float(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_temp.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_grip.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_height_above_ground.append(
                float(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_lateral_stiffness.append(float(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_wear.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.brake_damage.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.suspension_damage.append(int(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.brake_temp.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_tread_temp.append(int(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_layer_temp.append(int(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_carcass_temp.append(int(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_rim_temp.append(int(self._unpacked_data.popleft()))
        for _ in range(4):
            self.tyre_internal_air_temp.append(int(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.wheel_local_position_y.append(float(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.ride_height.append(float(self._unpacked_data.popleft()))
        for _ in range(4):
            self.suspension_travel.append(float(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.suspension_velocity.append(float(
                self._unpacked_data.popleft()))
        for _ in range(4):
            self.air_pressure.append(int(self._unpacked_data.popleft()))

        self.engine_speed = float(self._unpacked_data.popleft())
        self.engine_torque = float(self._unpacked_data.popleft())

        self.aero_damage = int(self._unpacked_data.popleft())
        self.engine_damage = int(self._unpacked_data.popleft())

        self.ambient_temperature = int(self._unpacked_data.popleft())
        self.track_temperature = int(self._unpacked_data.popleft())
        self.rain_density = int(self._unpacked_data.popleft())
        self.wind_speed = int(self._unpacked_data.popleft())
        self.wind_direction_x = int(self._unpacked_data.popleft())
        self.wind_direction_y = int(self._unpacked_data.popleft())

        self.participant_info = list()
        for _ in range(56):
            self.participant_info.append(ParticipantInfo(
                self._unpacked_data))

        self.track_length = float(self._unpacked_data.popleft())
        self.wings = list()
        for _ in range(2):
            self.wings.append(int(self._unpacked_data.popleft()))
        self._d_pad = int(self._unpacked_data.popleft())
        
    @property
    def game_state(self) -> int:
        """
        GAME_EXITED = 0
        GAME_FRONT_END = 1
        GAME_INGAME_PLAYING = 2
        GAME_INGAME_PAUSED = 3
        """
        return self._game_session_state & int('00001111', 2)

    @property
    def session_state(self) -> int:
        """
        SESSION_INVALID = 0
        SESSION_PRACTICE = 1
        SESSION_TEST = 2
        SESSION_QUALITY = 3
        SESSION_FORMATION_LAP = 4
        SESSION_RACE = 5
        SESSION_TIME_ATTACK = 6
        """
        return (self._game_session_state & int('11110000', 2)) >> 4
    
    @property
    def race_state(self) -> int:
        """
        RACESTATE_INVALID = 0
        RACESTATE_NOT_STARTED = 1
        RACESTATE_RACING = 2
        RACESTATE_FINISHED = 3
        RACESTATE_DISQUALIFIED = 4
        RACESTATE_RETIRED = 5
        RACESTATE_DNF = 6
        """
        return self._race_state_flags & int('00000111', 2)

    @property
    def lap_invalidated(self) -> bool:
        return bool((self._race_state_flags & int('00001000', 2)) >> 3)

    @property
    def anti_lock_active(self) -> bool:
        return bool((self._race_state_flags & int('00010000', 2)) >> 4)

    @property
    def boost_active(self) -> bool:
        return bool((self._race_state_flags & int('00100000', 2)) >> 5)

    @property
    def highest_flag_color(self) -> int:
        """
        FLAG_COLOUR_NONE = 0
        FLAG_COLOUR_GREEN = 1
        FLAG_COLOUR_BLUE = 2
        FLAG_COLOUR_WHITE = 3
        FLAG_COLOUR_YELLOW = 4
        FLAG_COLOUR_DOUBLE_YELLOW = 5
        FLAG_COLOUR_BLACK = 6
        FLAG_COLOUR_CHEQUERED = 7
        """
        return self._highest_flag & int('00001111', 2)

    @property
    def highest_flag_reason(self) -> int:
        """
        FLAG_REASON_NONE = 0
        FLAG_REASON_SOLO_CRASH = 1
        FLAG_REASON_VEHICLE_CRASH = 2
        FLAG_REASON_VEHICLE_OBSTRUCTION = 3
        """
        return (self._highest_flag & int('11110000', 2)) >> 4

    @property
    def pit_mode(self) -> int:
        """
        PIT_MODE_NONE = 0
        PIT_MODE_DRIVING_INTO_PITS = 1
        PIT_MODE_IN_PIT = 2
        PIT_MODE_DRIVING_OUT_OF_PITS = 3
        PIT_MODE_IN_GARAGE = 4
        """
        return self._pit_mode_schedule & int('00001111', 2)

    @property
    def pit_schedule(self) -> int:
        """
        PIT_SCHEDULE_NONE = 0
        PIT_SCHEDULE_STANDARD = 1
        PIT_SCHEDULE_DRIVE_THROUGH = 2
        PIT_SCHEDULE_STOP_GO = 3
        """
        return (self._pit_mode_schedule & int('11110000', 2)) >> 4

    @property
    def car_headlight(self) -> bool:
        return bool(self._car_flags & int('00000001', 2))

    @property
    def car_engine_active(self) -> bool:
        return bool((self._car_flags & int('00000010', 2)) >> 1)

    @property
    def car_engine_warning(self) -> bool:
        return bool((self._car_flags & int('00000100', 2)) >> 2)

    @property
    def car_speed_limiter(self) -> bool:
        return bool((self._car_flags & int('00001000', 2)) >> 3)

    @property
    def car_abs(self) -> bool:
        return bool((self._car_flags & int('00010000', 2)) >> 4)

    @property
    def car_handbrake(self) -> bool:
        return bool((self._car_flags & int('00100000', 2)) >> 5)

    @property
    def car_stability(self):
        return bool((self._car_flags & int('01000000', 2)) >> 6)

    @property
    def car_traction_control(self):
        return bool((self._car_flags & int('10000000', 2)) >> 7)

    @property
    def gear(self) -> int:
        return self._gear_num_gears & int('00001111', 2)

    @property
    def num_gears(self) -> int:
        return (self._gear_num_gears & int('11110000', 2)) >> 4

    @property
    def tyre_attached(self):
        return [bool(tyre & int('00000001', 2)) for tyre in self._tyre_flags]

    @property
    def tyre_inflated(self):
        return [
            bool((tyre & int('00000010', 2)) >> 1) for tyre in self._tyre_flags]

    @property
    def tyre_is_on_ground(self):
        return [
            bool((tyre & int('00000100', 2)) >> 2) for tyre in self._tyre_flags]

    @property
    def joypad_buttons(self):
        """
        VALUE: PC, XB, PS4
        1: NA, NA, NA
        2: NA, NA, NA
        4: NA, NA, NA
        8: NA, NA, NA
        16: START, START, OPTION
        32: BACK, BACK, NA
        64: L3, L3, L3
        128: R3, R3, R3
        256: LB, LB, LB
        512: RB, RB, RB
        1024: NA, NA, NA
        2048: NA, NA, NA
        4096: A, A, CROSS
        8192: B, B, CIRCLE
        16384: X, X, SQUARE
        32768: Y, Y, TRIANGLE

        PAD: PC, XB, PS4
        1: UP, UP, UP
        2: DOWN, DOWN, DOWN
        4: LEFT, LEFT, LEFT
        8: RIGHT, RIGHT, RIGHT
        """
        buttons = list()

        joypad_list = [int(i) for i in bin(self._joypad)[:1:-1]]
        joypad_list += [0] * (16 - len(joypad_list))
        buttons.extend(joypad_list)

        d_pad_list = [
            int(i) for i in bin((self._d_pad & int('11110000', 2)) >> 4)[:1:-1]]
        d_pad_list += [0] * (4 - len(d_pad_list))
        buttons.extend(d_pad_list)

        crash_state_list = [
                int(i) for i
                in bin((self._crash_state & int('11110000', 2)) >> 4)[:1:-1]]
        crash_state_list += [0] * (4 - len(crash_state_list))
        buttons.extend(crash_state_list)

        return buttons

    @property
    def crash_state(self) -> int:
        """
        CRASH_DAMAGE_NONE = 0
        CRASH_DAMAGE_OFFTRACK = 1
        CRASH_DAMAGE_LARGE_PROP = 2
        CRASH_DAMAGE_SPINNING = 3
        CRASH_DAMAGE_ROLLING = 4
        """
        return self._crash_state & int('00001111', 2)

    def __new__(cls, packet_data):
        raise NotImplementedError

    def __str__(self):
        return "TelemetryDataPacket"


class ParticipantInfo:
    """
    Creates an object containing the participant info from the
    telemetry data.
    """
    def __init__(self, unpacked_data):
        self._world_position = list()
        for _ in range(3):
            self._world_position.append(int(unpacked_data.popleft()))

        self.current_lap_distance = int(unpacked_data.popleft())
        self._race_position = int(unpacked_data.popleft())
        self._laps_completed = int(unpacked_data.popleft())
        self.current_lap = int(unpacked_data.popleft())
        self._sector = int(unpacked_data.popleft())
        self.last_sector_time = float(unpacked_data.popleft())

    @property
    def world_position(self):
        """Returns world position (high accuracy for x and z)."""
        world_position = [float(x) for x in self._world_position]
        world_position[0] += float(
            ((self._sector & int('00011000', 2)) >> 3) / 4)
        world_position[2] += float(
            ((self._sector & int('01100000', 2)) >> 5) / 4)

        return world_position

    @property
    def race_position(self):
        """Determines the Participant's race position."""
        return self._race_position & int('01111111', 2)

    @property
    def is_active(self):
        """Determines if the Participant is active."""
        return bool((self._race_position & int('10000000', 2)) >> 7)

    @property
    def laps_completed(self):
        """Determines the laps completed by Participant."""
        return self._laps_completed & int('01111111', 2)

    @property
    def lap_invalidated(self):
        """
        Determines if the Participant's lap is valid.

        Project CARS flags the start of the race (Sector 3, before you
        reach the start-finish line to begin the 'first lap proper')
        as invalid, so we need to deal with that. Dumb.

        That will have sector equal to 3 (since you start the race
        in Sector 3) and a previous sector time of -123 (since you
        don't have a previous sector time).
        """
        lap_invalidated = bool((self._laps_completed & int('10000000', 2)) >> 7)

        if lap_invalidated and \
                self.sector == 3 and \
                self.last_sector_time == -123:
            return 0
        else:
            return lap_invalidated

    @property
    def sector(self):
        """Determines the Participant's current sector.
        SECTOR_INVALID = 0
        SECTOR_START = 1
        SECTOR_SECTOR1 = 2
        SECTOR_SECTOR2 = 3
        SECTOR_FINISH = 4
        SECTOR_STOP = 5
        """
        return self._sector & int('00000111', 2)

    @property
    def same_class(self) -> bool:
        return bool((self._sector & int('10000000', 2)) >> 7)
