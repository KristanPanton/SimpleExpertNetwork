from experta import *

# TODO:
# Add more questions
# Complete Bridging Rules
# Create GUI

DEFECTS_LIST = ['Bridging',
                'Insufficient Fill',
                'Random Solder Balls',
                'Solder Spattering',
                'Mid-Chip Solder Balls',
                'Tombstoning',
                'Voiding',
                'BGA Head-on-Pillow',
                'Grainy Joints']

DEFECTS = {
    'Bridging':
        {
            'Causes': {
                'PCB': {
                    'Solder mask present between adjacent pads': ['Are there solder masks between adjacent pads?'],
                    'Insufficient PCB support': ['Is the PCB not supported properly?'],
                },
                'Stencil': {
                    'Insufficient stencil tension': ['Is the stencil tension insufficient?'],
                    'Damaged stencil': ['Is the stencil damaged?'],
                    'Unclean stencil': [
                        'Is the minimum print pressure too low?',
                        'Is the stencil wiped infrequently?'
                    ],
                    'Inappropriate stencil aperture design': ['Are the stencil apertures smaller than the pads?'],
                },
                'Gasket': {
                    'Poor gasketing between stencil and PCB': [
                        'Is there a zero print gap between the stencil and PCB?',
                        'Is there an inconsistent paste smear underneath the stencil?'
                    ]
                },
                'Screen Printer': {
                    'Screen printer misalignment': ['Is the print inaccurate and inconsistent?'],
                    'Bad separation speed': ["Are there 'dog ears' on the components?"],
                    'Bad/Inaccurate component placement': []
                },
                'Squeegee Blades': {
                    'Damaged squeegee blades': ['Are the squeegee blades damaged?'],
                },
                'Component Placement': {
                    'Component placement inaccuracy': ['Are the component placements accurate?'],
                    'Excessive component placement pressure': [
                        'Has solder paste overflowed from the pad?',
                        'Is component placement height greater than ±1/3 of paste height?'
                    ]
                },
                'Reflow Profile': {
                    'Incorrect reflow profile': ["Was the reflow profile's soak extended?"]
                },
                'Solder Paste': {
                    'Wrong solder paste operating temperature': [
                        "Is there a mismatch between the solder paste's required temperature and the screen printer's temperature?"
                    ],
                    'Dry solder paste': [
                        'Has the solder paste expired?',
                        'Has old solder paste contaminated the new solder paste?'
                    ]
                }
            }
        }
}


def get_yorn(query):
    while True:
        inp = str(input(query))
        if inp[0].lower() in 'yn':
            if inp[0] == 'y':
                return True
            else:
                return False
        else:
            print("Invalid Input!")


class Defect(Fact):
    cause = Field(str)


class Cause(Fact):
    pass


class Component(Fact):
    condition = Field(str)


class Attribute(Fact):
    name = Field(str, mandatory=True)


class Action(Fact):
    pass


class BridgingRules:
    @Rule(Action('Investigate'), Defect(MATCH.name))
    def investigate(self, name):
        # Declare likely components and investigate them
        for key in DEFECTS[name]['Causes']:
            self.declare(Component(key))

    @Rule(Action('Investigate'), Defect('Bridging'), Component(MATCH.name))
    def investigate_components_bridging(self, name):
        pass


class InsufficientFillRules:
    pass


class InsufficientSolderRules:
    pass


class RandomSolderBallsRules:
    pass


class SolderSpatteringRules:
    pass


class MidChipSolderBallsRules:
    pass


class TombstoningRules:
    pass


class VoidingRules:
    pass


class BGAHeadOnPillowRules:
    pass


class GrainyJointsRules:
    pass


class DefectAnalysisExpert(BridgingRules, KnowledgeEngine):
    @DefFacts()
    def initiate(self):
        print("This is an expert system for defect analysis.")
        print("What type of defect occurred?")
        [print(f"{i}. {defect}") for i, defect in enumerate(DEFECTS_LIST, 1)]
        while True:
            try:
                defect = DEFECTS_LIST[abs(int(input("Enter number: ")) - 1)]
                print(f"Your choice is {defect}")
                yield Action('Investigate')
                yield Defect(defect)
                break
            except (ValueError, IndexError):
                print("Invalid Input!")

    @Rule(Action('Report'))
    def report_findings(self):
        pass


engine = DefectAnalysisExpert()
engine.reset()
watch('RULES', 'FACTS', 'ACTIVATIONS')
engine.run()
