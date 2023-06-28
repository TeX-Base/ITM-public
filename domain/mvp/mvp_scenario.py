from domain.internal import Scenario
from .mvp_state import MVPState


class MVPScenario(Scenario):
    def __init__(self, name: str, id: str, prompt: str, state: MVPState):
        super().__init__(name)
        self.name: str = name
        self.id: str = id
        self.prompt: str = prompt
        self.state: MVPState = state

    def get_similarity(self, other_scenario: 'MVPScenario') -> float:
        return self.state.get_similarity(other_scenario.state)
