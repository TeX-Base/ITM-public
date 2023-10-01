import csv
from components.case_formation.acf.argument_case import ArgumentCase
import yaml
import domain.internal as internal
import domain.external as external
import domain.ta3 as ta3

# from components.case_formation.acf.util.read_csv import CSVReader # TODO: move the csv conversion to the CSVReader class

# set the numbers to return when conversion fails
FAILED_INT = 999
FAILED_FLOAT = 0.0


class CaseBase:
    def __init__(self, _input_file, _yaml_file) -> None:
        self._csv_file_path = _input_file
        self._yaml_file_path = _yaml_file
        self._csv_cases = self._read_csv_multi()
        self.scenario = self._import_scenario()
        self.cases: list[ArgumentCase] = []
        self._create_internal_multicas_cases()

    def _read_csv_multi(self):
        csv_rows: list[dict] = []
        with open(self._csv_file_path, "r") as f:
            reader = csv.reader(f, delimiter=",")
            headers: list[str] = next(reader)
            # the first header had some special characters in it
            headers[0] = "Case_#"

            for i in range(len(headers)):
                headers[i] = headers[i].strip().replace("'", "").replace('"', "")

            kdmas = headers[
                headers.index("mission-Ave") : headers.index("timeurg-M-A") + 1
            ]

            for line in reader:
                case = {}
                for i, entry in enumerate(line):
                    case[headers[i]] = entry.strip().replace("'", "").replace('"', "")
                # Clean KDMAs
                _kdmas = self._replace(case, kdmas, "kdmas")
                for kdma in list(_kdmas.keys()):
                    if kdma.endswith("-Ave"):
                        _kdmas[kdma.split("-")[0]] = _kdmas[kdma]
                    del _kdmas[kdma]
                # Skip any entires that don't have KDMA values
                if list(_kdmas.values())[0].lower() == "na":
                    continue

                # Clean supplies
                sup_type = case.pop("Supplies: type")
                sup_quant = case.pop("Supplies: quantity")
                case["supplies"] = {sup_type: sup_quant}

                # Clean action
                case["action"] = {
                    "type": case.pop("Action type"),
                    "params": [
                        param.strip() for param in case.pop("Action").split(",")
                    ][1:],
                }

                # the casualties are 5 groups of 19 columns starting from column 21
                casualty_data = []
                for i in range(5):
                    casualty_group = {}

                    for j in range(19):
                        casualty_group[headers[21 + i * 19 + j]] = line[21 + i * 19 + j]

                    # Clean casualty data
                    cas_id = casualty_group.pop("Casualty_id")
                    cas_name = casualty_group.pop("casualty name")
                    cas_unstructured = casualty_group.pop("Casualty unstructured")
                    cas_relation = casualty_group.pop("casualty_relationship")
                    casualty_group["casualty"] = {
                        "id": cas_id,
                        "name": cas_name,
                        "unstructured": cas_unstructured,
                        "relationship": cas_relation,
                    }

                    # Clean tag
                    TRIAGE_CATEGORIES = ["MINIMAL", "DELAYED", "IMMEDIATE", "EXPECTANT"]
                    cas_triage_category = self._convert_to_int(
                        casualty_group.pop("triage category")
                    )
                    # some triage categories in the data exceed the index
                    if cas_triage_category == 4:
                        cas_triage_category = 3
                    if cas_triage_category <= 3:
                        casualty_group["tag"] = TRIAGE_CATEGORIES[cas_triage_category]
                    else:
                        casualty_group["tag"] = None
                    # Clean demographics
                    demo_age = casualty_group.pop("age")
                    demo_sex = casualty_group.pop("IndividualSex")
                    demo_rank = casualty_group.pop("IndividualRank")
                    casualty_group["demographics"] = {
                        "age": demo_age,
                        "sex": demo_sex,
                        "rank": demo_rank,
                    }

                    # Clean Injury
                    injury_name = casualty_group.pop("Injury name")
                    injury_location = casualty_group.pop("Injury location")
                    injury_severity = casualty_group.pop("severity")
                    casualty_group["injury"] = {
                        "name": injury_name,
                        "location": injury_location,
                        "severity": injury_severity,
                    }

                    # Clean vitals
                    casualty_group["vitals"] = {
                        "responsive": casualty_group.pop("vitals:responsive"),
                        "breathing": casualty_group.pop("vitals:breathing"),
                        "hrpm": casualty_group.pop("hrpmin"),
                        "mmhg": casualty_group.pop("mmHg"),
                        "rr": casualty_group.pop("RR"),
                        "spo2": casualty_group.pop("Spo2"),
                        "pain": casualty_group.pop("Pain"),
                    }
                    casualty_data.append(casualty_group)
                case["casualties"] = casualty_data
                # clean up the casualty data from the last group
                items_to_remove = [
                    "Casualty_id",
                    "casualty name",
                    "Casualty unstructured",
                    "age",
                    "IndividualSex",
                    "casualty_relationship",
                    "IndividualRank",
                    "Injury name",
                    "Injury location",
                    "severity",
                    "vitals:responsive",
                    "vitals:breathing",
                    "hrpmin",
                    "mmHg",
                    "RR",
                    "Spo2",
                    "Pain",
                    "casualty_assessed",
                    "triage category",
                ]
                for item in items_to_remove:
                    del case[item]

                csv_rows.append(case)
        return csv_rows

    # convert a case to internal representation
    def _import_scenario(self):
        scenario_from_file = yaml.load(open(self._yaml_file_path), Loader=yaml.Loader)

        state_from_file = self._convert_state(scenario_from_file["state"])

        scenario = external.Scenario(
            name=scenario_from_file["name"],
            id=scenario_from_file["id"],
            state=state_from_file,
            probes=[],
        )
        return scenario

    def _convert_state(self, state: dict):
        state["scenario_complete"] = False
        state["elapsed_time"] = 0.0
        # rename dictionary key from aidDelay to aid_delay
        state["environment"]["aid_delay"] = state["environment"].pop("aidDelay")
        state["environment"]["weather"] = None
        state["environment"]["location"] = None
        state["environment"]["terrain"] = None
        state["environment"]["flora"] = None
        state["environment"]["fauna"] = None
        state["environment"]["soundscape"] = None
        state["environment"]["temperature"] = None
        state["environment"]["humidity"] = None
        state["environment"]["lighting"] = None
        state["environment"]["visibility"] = None
        state["environment"]["noise_ambient"] = None
        state["environment"]["noise_peak"] = None
        for casualty in state["casualties"]:
            casualty["name"] = casualty["id"]
            casualty["injuries"] = []
            casualty["relationship"] = None
            casualty["vitals"] = {
                "conscious": None,
                "mental_status": None,
                "breathing": None,
                "hrpmin": None,
            }
            casualty["visited"] = False
            casualty["tag"] = None

        return state

    def _convert_csv_ta3vitals(self, data: dict) -> ta3.Vitals:
        ta3_concious = bool(data["responsive"])
        ta3_mental_status = "responsive" if ta3_concious else "unresponsive"
        ta3_breathing = data["breathing"]
        ta3_hrpmin = self._convert_to_int(data["hrpm"])
        return ta3.Vitals(
            conscious=ta3_concious,
            mental_status=ta3_mental_status,
            breathing=ta3_breathing,
            hrpmin=ta3_hrpmin,
        )

    def _convert_csv_ta3casualties(self, casualty_data: dict) -> ta3.Casualty:
        injuries = [ta3.Injury(**i) for i in casualty_data["injuries"]]
        demographics = ta3.Demographics(**casualty_data["demographics"])
        vitals = ta3.Vitals(**casualty_data["vitals"])
        return ta3.Casualty(
            casualty_data["id"],
            casualty_data["name"],
            injuries,
            demographics,
            vitals,
            casualty_data["tag"],
            casualty_data["treatments"],
            casualty_data["assessed"],
            casualty_data["unstructured"],
            casualty_data["relationship"],
        )

    def _convert_ta3injury(self, data: dict) -> ta3.Injury:
        if "location" in data:
            injury_location = data["location"]
        else:
            injury_location = "unspecified"
        if "name" in data:
            injury_name = data["name"]
        else:
            injury_name = "unspecified"
        if "severity" in data:
            injury_severity = self._convert_to_float(data["severity"])
        else:
            injury_severity = FAILED_FLOAT
        ta3_injury = ta3.Injury(
            location=injury_location, name=injury_name, severity=injury_severity
        )
        return [ta3_injury]

    def _convert_csv_single_casualty(self, data: dict) -> ta3.Casualty:
        ta3_id = data["casualty"]["id"]
        ta3_name = data["casualty"]["name"]
        ta3_unstructured = data["casualty"]["unstructured"]
        ta3_relationship = data["casualty"]["relationship"]
        ta3_injuries = self._convert_ta3injury(data["injury"])
        ta3_demographics = ta3.Demographics(**data["demographics"])
        ta3_vitals = self._convert_csv_ta3vitals(data["vitals"])

        ta3_tag = data["tag"] if "tag" in data else None
        ta3_treatments = []
        ta3_assessed = False

        ta3_casualty = ta3.Casualty(
            id=ta3_id,
            name=ta3_name,
            injuries=ta3_injuries,
            demographics=ta3_demographics,
            vitals=ta3_vitals,
            tag=ta3_tag,
            unstructured=ta3_unstructured,
            relationship=ta3_relationship,
            treatments=ta3_treatments,
            assessed=ta3_assessed,
        )
        return ta3_casualty

    def _convert_csv_ta3supply(self, supply_data: dict) -> ta3.Supply:
        # get the first key and value in the dictionary
        supply_type = list(supply_data.keys())[0]
        supply_quantity = list(supply_data.values())[0]
        ta3_supply = ta3.Supply(supply_type, supply_quantity)
        return ta3_supply

    def _convert_csv_ta3state(self, data: dict) -> ta3.TA3State:
        unstructured = data["unstructured"] if "unstructured" in data else ""
        start_time = data["time"] if "time" in data else 0
        casualty_data = data["casualties"] if "casualties" in data else []
        actions_performed = []
        supplies = []

        if "actions_performed" in data:
            actions_performed = data["actions_performed"]
        elif "action" in data:
            actions_performed = [data["action"]]

        if "casualty" in data:
            casualty = self._convert_csv_single_casualty(data)
            casualty_data = [casualty]
        elif "casualties" in data:
            casualty_data = [
                self._convert_csv_single_casualty(c) for c in data["casualties"]
            ]
        else:
            # create a default casualty
            data["casualties"] = {"test": 1}
            casualty_data = [ta3.Casualty(**data["casualties"])]

        # if there is only one supply in the csv
        if "supplies" in data:
            if len(data["supplies"]) == 1:
                supplies = [self._convert_csv_ta3supply(data["supplies"])]
            else:
                supplies = [ta3.Supply(**s) for s in data["supplies"]]
        else:
            # create a default supply
            data["supplies"] = {"test": 1}
            supplies = [ta3.Supply(**data["supplies"])]

        return ta3.TA3State(
            unstructured, start_time, casualty_data, supplies, actions_performed
        )

    def _to_internal(self, case: dict) -> ArgumentCase:
        return ArgumentCase(case)

    def _create_internal_multicas_cases(self):
        for csv_case in self._csv_cases:
            decisions: list[internal.Decision] = []
            # if decisions are in data
            if "action" in csv_case:
                decision = internal.Decision(
                    id_=csv_case["Case_#"],
                    value=internal.Action(
                        name_=csv_case["action"]["type"],
                        params=({"action1": csv_case["action"]["params"]}),
                    ),
                )
                decisions.append(decision)

            case_no = csv_case["Case_#"]
            id = case_no
            prompt = csv_case["prompt"]

            prompt = csv_case["prompt"]
            state = self._convert_csv_ta3state(csv_case)

            probe = internal.Probe(
                id_=id, state=state, prompt=prompt, decisions=decisions
            )

            self.scenario.probes.append(probe)

            # extras
            probe_type = csv_case["Probe Type"]

            # casualty assessed will be in single casualty data but for each casualty in multicas
            if "casualty_assessed" in csv_case:
                if casualty_assessed == "NA":
                    casualty_assessed = False
                else:
                    casualty_assessed = csv_case["casualty_assessed"]
            else:
                casualty_assessed = False

            action_text = csv_case["Action text"]
            # extended_vitals = csv_case["vitals"]

            argument_case = ArgumentCase(
                id=id,
                case_no=case_no,
                csv_data=csv_case,
                scenario=self.scenario,
                probe=probe,
                response=decisions[0]
                if len(decisions) > 0
                else internal.Decision("None", []),
                additional_data={
                    "probe_type": probe_type,
                    # "casualty_assessed": casualty_assessed,
                    "action_text": action_text,
                    # "extended_vitals": extended_vitals,
                },
                kdmas=csv_case["kdmas"],
            )
            self.cases.append(argument_case)

    def _create_internal_cases(self):
        for csv_case in self._csv_cases:
            decisions: list[internal.Decision] = []
            # if decisions are in data
            if "action" in csv_case:
                decision = internal.Decision(
                    id_=csv_case["Case_#"],
                    value=internal.Action(
                        name_=csv_case["action"]["type"],
                        params=({"action1": csv_case["action"]["params"]}),
                    ),
                )
                decisions.append(decision)

            case_no = csv_case["Case_#"]

            prompt = csv_case["prompt"]
            state: ta3.TA3State = self._convert_csv_ta3state(csv_case)

            probe = internal.Probe(
                id_=id, state=state, prompt=prompt, decisions=decisions
            )

            # some analytics look for probes in the scenario
            self.scenario.probes.append(probe)

            # extras
            probe_type = csv_case["Probe Type"]
            casualty_assessed = csv_case["casualty_assessed"]
            action_text = csv_case["Action text"]
            extended_vitals = csv_case["vitals"]

            argument_case = ArgumentCase(
                id=id,
                case_no=case_no,
                csv_data=csv_case,
                scenario=self.scenario,
                probe=probe,
                response=decisions[0]
                if len(decisions) > 0
                else internal.Decision("None", []),
                additional_data={
                    "probe_type": probe_type,
                    "casualty_assessed": casualty_assessed,
                    "action_text": action_text,
                    "extended_vitals": extended_vitals,
                },
                kdmas=csv_case["kdmas"],
            )
            self.cases.append(argument_case)

    @staticmethod
    def _replace(case: dict, headers: list[str], name_: str) -> dict[str, any]:
        sub_dict = {}
        for header in headers:
            sub_dict[header] = case[header]
            del case[header]
        case[name_] = sub_dict
        return sub_dict

    @staticmethod
    # convert input to integer if possible else return 999
    def _convert_to_int(input):
        try:
            return int(input)
        except ValueError:
            return FAILED_INT

    @staticmethod
    # convert to float if possible else return 0.0
    def _convert_to_float(input):
        try:
            return float(input)
        except ValueError:
            return FAILED_FLOAT
