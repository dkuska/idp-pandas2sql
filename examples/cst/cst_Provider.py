import libcst as cst


class Provider(cst.BatchableMetadataProvider):
    def __init__(self, cache: object = None) -> None:
        super().__init__(cache)
