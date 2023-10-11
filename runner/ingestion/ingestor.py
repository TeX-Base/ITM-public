from components.decision_selector.mvp_cbr import Case
from domain import Scenario


class Ingestor:
    def __init__(self, data_dir: str):
        self.data_dir: str = data_dir

    def ingest_as_cases(self) -> list[Case]:
        raise NotImplementedError

    def ingest_as_domain(self) -> Scenario:
        raise NotImplementedError
