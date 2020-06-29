from experta import *


class Defect(Fact):
    pass


class Condition(Fact):
    temperature = Field(float, mandatory=True)
    humidity = Field(float, mandatory=True)
    squeegee_pressure = Field(float, mandatory=True)
    stencil_condition = Field()


class SolderPastePrintingDefects:
    # Slump to Solder Paste in Through-Holes and Vias

    @Rule(Condition(temperature=float(), humidity=float(), squeegee_pressure=float()))
    def is_slump(self):
        self.declare(Defect('Slump'))

    @Rule(Defect('Slump'))
    def regulate_temp_and_humidity(self):
        pass


class ComponentPlacementDefects:
    # Solder Pasted Pushed Off Pads to Capacitor fitted in place of Resistor
    pass


class ReflowSolderingDefects:
    # Insufficient Solder or Dry Joint to Partial Solder Joint
    pass


class ExpertSystem(
    SolderPastePrintingDefects,
    ComponentPlacementDefects,
    ReflowSolderingDefects,
    KnowledgeEngine
):
    @DefFacts()
    def _initial_facts(self):
        yield Fact(malfunction=False)
        yield Condition()

    @Rule(NOT(Fact(malfunction=False)))
    def _(self):
        pass


engine = ExpertSystem()
engine.reset()
engine.run()
