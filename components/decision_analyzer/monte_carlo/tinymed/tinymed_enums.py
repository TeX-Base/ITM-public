from enum import Enum


class Actions(Enum):
    APPLY_TREATMENT = "apply treatment"
    CHECK_ALL_VITALS = "check all vitals"
    CHECK_PULSE = "check pulse"
    CHECK_RESPIRATION = "check respiration"
    DIRECT_MOBILE_CASUALTY = "direct mobile casualty"
    MOVE_TO_EVAC = "get to the choppah"
    TAG_CASUALTY = "tag casualty"
    SITREP = "sitrep"
    UNKNOWN = "unknown"


class MentalStates(Enum):
    DANDY = "dandy"
    FINE = "fine"
    PANICKED = "panicked"


class BreathingDescriptions(Enum):
    NORMAL = "normal"
    HEAVY = "heavy"
    COLLAPSED = "collapsed"


class Supplies(Enum):
    TOURNIQUET = "Tourniquet"
    PRESSURE_BANDAGE = "Pressure bandage"
    HEMOSTATIC_GAUZE = "Hemostatic gauze"
    DECOMPRESSION_NEEDLE = "Decompression Needle"
    NASOPHARYNGEAL_AIRWAY = "Nasopharyngeal airway"


class Locations(Enum):
    RIGHT_FOREARM = "right forearm"
    LEFT_FOREARM = "left forearm"
    RIGHT_CALF = "right calf"
    LEFT_CALF = "left calf"
    RIGHT_THIGH = "right thigh"
    LEFT_THIGH = "left thigh"
    RIGHT_STOMACH = "right stomach"
    LEFT_STOMACH = "left stomach"
    RIGHT_BICEP = "right bicep"
    LEFT_BICEP = "left bicep"
    RIGHT_SHOULDER = "right shoulder"
    LEFT_SHOULDER = "left shoulder"
    RIGHT_SIDE = "right side"
    LEFT_SIDE = "left side"
    RIGHT_WRIST = "right wrist"
    LEFT_WRIST = "left wrist"
    LEFT_FACE = "left face"
    RIGHT_FACE = "right face"
    LEFT_CHEST = "left chest"
    RIGHT_CHEST = "right chest"
    LEFT_NECK = "left neck"
    RIGHT_NECK = "right neck"
    UNSPECIFIED = "unspecified"


class Tags(Enum):
    BLACK = "black"
    RED = "red"
    BLUE = 'blue'
    GREEN = 'green'


class Injuries(Enum):
    FOREHEAD_SCRAPE = 'forehead scrape'
    EAR_BLEED = 'ear bleed'
    ASTHMATIC = 'asthmatic'
    LACERATION = 'laceration'
    PUNCTURE = 'puncture'
    SHRAPNEL = 'shrapnel'
    CHEST_COLLAPSE = 'chest collapse'
    AMPUTATION = 'amputation'
    BURN = 'burn'


class Demographics:
    def __init__(self, age: int, sex: str, rank: str):
        self.age: int = age
        self.sex: str = sex
        self.rank: str = rank


class Injury:
    def __init__(self, name: str, location: str, severity: float):
        self.name = name
        self.location = location
        self.severity = severity

    def progress(self, time_passed: int):
        if time_passed % 5 == 0:
            if self.severity < 2:
                pass  # very minor things dont get infected/advance
            elif self.severity < 4:
                self.severity += .04
            elif self.severity < 7:
                self.severity += .25
            else:
                self.severity += .64

    def recover(self):
        self.severity = 1  # I would recommend they still go to their primary after the battle


class Vitals:
    def __init__(self, conscious: bool, mental_status: str, breathing: str, hrpmin: int):
        self.conscious: bool = conscious
        self.mental_status: str = mental_status
        self.breathing: str = breathing
        self.hrpmin: int = hrpmin


class Casualty:
    def __init__(self, id: str, unstructured: str, name: str, relationship: str, demographics: Demographics,
                 injuries: list[Injury], vitals: Vitals, complete_vitals: Vitals, assessed: bool, tag: str):
        self.id: str = id
        self.unstructured: str = unstructured
        self.name: str = name
        self.relationship: str = relationship
        self.demographics: Demographics = demographics
        self.injuries: list[Injury] = injuries
        self.vitals: Vitals = vitals
        self.complete_vitals: Vitals = complete_vitals
        self.assessed: bool = assessed
        self.tag: str = tag
        self.time_elapsed: int = 0
        self.dead = False

    def check_if_dead(self):
        for i in self.injuries:
            if i.severity >= 10:
                self.dead = True

    def update_injury(self, success: bool, injury: Injury):
        self.time_elapsed += 1
        if success:
            injury.recover()
        else:
            injury.progress(self.time_elapsed)
        self.check_if_dead()
