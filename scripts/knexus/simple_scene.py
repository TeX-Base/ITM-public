from components.decision_analyzer.monte_carlo.mc_sim import SimResult
from components.decision_analyzer.monte_carlo.medsim import MedsimState, MedicalSimulator, MedsimAction
import components.decision_analyzer.monte_carlo.medsim.util.medsim_enums as tenums
from components.decision_analyzer.monte_carlo.medsim.util.medsim_enums import *
from components.decision_analyzer.monte_carlo.util.ta3_converter import reverse_convert_state, _convert_action, _reverse_convert_action
from domain.external import ITMProbe, ProbeType, Scenario
from runner.ta3_driver import TA3Driver
from domain.internal import KDMAs
from util import logger, dict_difference
from domain.external import Action


def get_simple_casualties():
    bicep_tear = Injury(name=Injuries.LACERATION.value, location=Locations.LEFT_BICEP.value, severity=4.0, treated=False)
    jt_vitals = Vitals(conscious=True, mental_status=MentalStates_KNX.CONFUSED.value,
                       breathing=BreathingDescriptions_KNX.NORMAL.value, hrpmin=69)
    casualties = [
        Casualty('JT', 'JT tore his bicep', name='JT',
                       relationship='same-unit',
                       demographics=Demographics(age=33, sex='M', rank='vip'),
                       injuries=[bicep_tear],
                       vitals=jt_vitals,
                       complete_vitals=jt_vitals,
                       assessed=False,
                       tag="tag")]
    return casualties


def get_simple_supplies() -> list[Supply]:
    supplies = [Supply(Supplies.TOURNIQUET.value, False, 0),
                Supply(Supplies.PRESSURE_BANDAGE.value, False, 3),
                Supply(Supplies.HEMOSTATIC_GAUZE.value, False, 0),
                Supply(Supplies.DECOMPRESSION_NEEDLE.value, False, 0),
                Supply(Supplies.NASOPHARYNGEAL_AIRWAY.value, False, 0),
                # Supply(Supplies.PULSE_OXIMETER.value, False, 1),
                # Supply(Supplies.BLANKET.value, False, 3),
                # Supply(Supplies.EPI_PEN.value, False, 2),
                # Supply(Supplies.VENTED_CHEST_SEAL.value, False, 3),
                # Supply(Supplies.PAIN_MEDICATIONS.value, False, 3),
                # Supply(Supplies.BLOOD.value, False, 3)
                ]
    return supplies


class SimpleClient:
    CASUALTIES = [{'id': 'JT', 'unstructured': 'JT has a minor eft bicep puncture',
                   'name': 'JT', 'relationship': None, 'demographics': {'age': 33, 'sex': 'M',
                                                                        'rank': 'director of social media'},
                   'injuries': [{'name': tenums.Injuries.LACERATION, 'location': tenums.Locations.LEFT_BICEP, 'severity': .4}],
                   'vitals': {'conscious': None, 'mental_status': None, 'breathing': None, 'hrpmin': None},
                   'complete_vitals': None, 'assessed': False, 'tag': None}]
    UNSTRUCTURED = 'JT has injured his left bicep lifting weights'
    ELAPSED_TIME = 0.0
    SCENARIO_COMPLETE = False
    MISSION = {'unstructured': 'Heal JTs ripped, injured muscles.', 'mission_type': 'Disaster Relief'}
    ENVIRONMENT = {'unstructured': 'Sewers under Rockville', 'weather': None, 'location': None, 'terrain': None,
                   'flora': None, 'fauna': 'Cat and Dog', 'soundscape': 'Janis Joplin', 'aid_delay': None, 'temperature': None,
                   'humidity': None, 'lighting': None, 'visibility': None, 'noise_ambient': None,
                   'noise_peak': None}
    THREAT_STATE = {'threats': [{'severity': 0.1, 'type': 'Cat'}],
                    'unstructured': 'Dmitri is peckish'}

    def __init__(self, alignment_target: KDMAs, max_actions=9, evalTargetNames = None):
        self.align_tgt: KDMAs = alignment_target
        self.actions: dict[str, Action] = {}
        casualties: list[Casualty] = get_simple_casualties()
        supplies: list[Supply] = get_simple_supplies()
        self.init_state: MedsimState = MedsimState(casualties, supplies, time=0.0,
                                                   unstructured="JT tore his bicep getting ripped.")
        self.current_state: MedsimState = self.init_state
        self.simulator = MedicalSimulator(init_state=self.init_state)
        self.probe_count: int = 0
        self.max_actions: int = max_actions

    def get_init(self) -> MedsimState:
        return self.init_state

    def get_probe(self, state: MedsimState | None) -> ITMProbe | None:
        if self.probe_count > self.max_actions:
            return None
        state = state if state is not None else self.init_state

        ta3_state = reverse_convert_state(state)
        actions: list[MedsimAction] = self.simulator.actions(state)
        ta3_actions: list[Action] = []
        for i, internal_action in enumerate(actions):
            ta3_action = _reverse_convert_action(internal_action, action_num=i)
            ta3_actions.append(ta3_action)
        supplies_as_dict = []
        for supply in ta3_state.supplies:
            supplies_as_dict.append({'quantity': supply.quantity, 'type': supply.type})
        casualties_as_dict = []
        for cas in ta3_state.casualties:
            injuries_as_dict = []
            for injury in cas.injuries:
                inj_dict = {'location': injury.location, 'name': injury.name,
                            'severity': injury.severity, 'treated': injury.treated}
                injuries_as_dict.append(inj_dict)
            demographs_as_dict = {'age': cas.demographics.age, 'sex': cas.demographics.sex, 'rank': cas.demographics.rank}
            vitals_as_dict = {'conscious': cas.vitals.conscious, 'mental_status': cas.vitals.mental_status,
                              'breathing': cas.vitals.breathing, 'hrpmin': cas.vitals.hrpmin}
            casualties_as_dict.append({'id': cas.id, 'name': cas.name, 'injuries': injuries_as_dict,
                                     'demographics': demographs_as_dict, 'vitals': vitals_as_dict, 'tag': cas.tag,
                                     'assessed': cas.assessed, 'unstructured': cas.unstructured, 'relationship': cas.relationship})
        swagger_state = {'unstructured': self.UNSTRUCTURED, 'elapsed_time': ta3_state.time_, 'scenario_complete': False,
                         'mission': {'unstructured': self.UNSTRUCTURED, 'mission_type': 'Extraction'},
                         'environment': self.ENVIRONMENT, 'threat_state': self.THREAT_STATE,
                         'supplies': supplies_as_dict, 'characters': casualties_as_dict}
        probe: ITMProbe = ITMProbe(id=f'simple-{self.probe_count}', type=ProbeType.MC, prompt="what do?",
                                   state=swagger_state, options=ta3_actions)
        self.probe_count += 1  # increment for next
        return probe

    def take_action(self, action: Action) -> ITMProbe:
        tinymed_action = _convert_action(act=action)
        sim_results: list[SimResult] = self.simulator.exec(self.current_state, action=tinymed_action)
        new_state = sim_results[0].outcome  # This is fine
        self.current_state = new_state
        new_probe = self.get_probe(new_state)
        return new_probe


def probe_stripper(probe):
    '''
    remove probes that aren't supported in hra
    '''
    new_options = [x for x in probe.options if x.type != 'SITREP' and x.type != 'DIRECT_MOBILE_CASUALTY']
    probe.options = new_options
    return probe


def main():
    kdmas: KDMAs = KDMAs([])

    class SIMPLEARGS:
        def __init__(self):
            self.human = False
            self.ebd = False
            self.hra = True
            self.kedsd = False
            self.verbose = False
            self.decision_verbose = False
            self.mc = True
            self.rollouts = 1234
            self.csv = True
            self.bayes = True
            self.variant = 'aligned'
    tmnt_args = SIMPLEARGS()

    driver = TA3Driver(tmnt_args)
    client = SimpleClient(kdmas)
    driver.set_alignment_tgt(kdmas)
    logger.debug("Driver and Simple Client loaded.")

    initial_state: MedsimState = client.get_init()
    probe = client.get_probe(initial_state)
    scenario = Scenario(name='SIMPLE DEMO', id='simple-demo', state=probe.state, probes=[])
    driver.set_scenario(scenario=scenario)

    while probe is not None:

        logger.info(f"Responding to probe-{probe.id}")
        # take out the direct_mobile and sitrep
        probe = probe_stripper(probe)
        action = driver.decide(probe)
        logger.info(f"Chosen Action-{action}")
        new_probe = client.take_action(action)

        if new_probe:
            difference = dict_difference(probe.state, new_probe.state, {'id', 'type'})
            logger.debug(f"-State Additions: {difference}")
            difference = dict_difference(new_probe.state, probe.state, {'id', 'type'})
            logger.debug(f"-State Removals: {difference}")
        probe = new_probe


if __name__ == '__main__':
    main()
