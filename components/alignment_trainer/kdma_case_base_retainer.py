import json
from components import AlignmentTrainer
from domain.internal import AlignmentFeedback, Scenario, Action
from datetime import datetime

FEEDBACK_FILE="temp/feedback.json"

class KDMACaseBaseRetainer(AlignmentTrainer):
    
    def __init__(self, continue_search = True):
        self.scene_kdmas = {}
        self.final_occurred = False
        if not continue_search:
            with open(FEEDBACK_FILE, "w") as outfile:
                outfile.write("")

        
    def train(self, scenario: Scenario, actions: list[Action], feedback: AlignmentFeedback, 
              final: bool, scene_end: bool, trained_scene: str):
        if not scene_end:
            return
        if self.final_occurred:
            self.scene_kdmas = dict()
            self.final_occurred = False
        print(f"scenario_id: {scenario.id_}")
        print(f"feedback: {feedback}")
        print(f"scene: {trained_scene}")
        print(f"source probes: {feedback.source_probes}")
        for (scene, kdma) in self.scene_kdmas.items():
            if scene not in feedback.source_probes:
                # breakpoint()
                pass
        if trained_scene in self.scene_kdmas:
            breakpoint()
        self.scene_kdmas[trained_scene] = dict()
        for (kdma_name, kdma_value) in feedback.kdma_values.items():
            if kdma_value is None:
                continue
            total_so_far = sum([val.get(kdma_name, 0) for val in self.scene_kdmas.values()])
            scene_kdma = kdma_value * len(feedback.source_probes) - total_so_far
            self.scene_kdmas[trained_scene][kdma_name] = scene_kdma
            print(f"kdma[{kdma_name}]: {kdma_value}")
            print(f"scene kdma[{kdma_name}]: {scene_kdma}")
        
        if trained_scene not in feedback.source_probes:
            #MCM 20240819: This happens when Soartech alignment is sent, ADEPT's probes and scenes
            # are the same. We ignore Soartech kdmas.
            return

        with open(FEEDBACK_FILE, "a") as outfile:
            json.dump({"scenario_id": scenario.id_, 
                       "feedback": feedback.to_json(), 
                       "actions": [act.to_json() for act in actions],
                       "time": datetime.now().strftime("%Y%m%d%H%M%S"),
                       "scene": trained_scene,
                       "scene_kdmas": self.scene_kdmas[trained_scene],
                       "final": final},
                      outfile)
            outfile.write("\n")
        if final:
            self.final_occurred = True
