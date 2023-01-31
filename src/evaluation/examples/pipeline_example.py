from textwrap import dedent

PipelineCode = str


# Do you have better name for this? Maybe UseCase?
class PipelineExample:
    name: str
    code: PipelineCode
    optimized_code: PipelineCode

    def __init__(self, name: str, code: PipelineCode, optimized_code: PipelineCode):
        self.name = name
        self.code = dedent(code)
        self.optimized_code = dedent(optimized_code)
