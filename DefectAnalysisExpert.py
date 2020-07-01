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
                'PCB': [
                    ('', 'Infrequent solder mask change'),
                    ('', 'Insufficient PCB support'),
                    ('', 'Poor gasketing between stencil and PCB')
                ],
                'Stencil': [
                    ('Is the stencil tension tight?', 'Insufficient stencil tension'),
                    ('Is the stencil undamaged?', 'Damaged stencil'),
                    ('Has the stencil been cleaned prior?', 'Unclean stencil'),
                    ('Are the stencil apertures smaller than the pads?', 'Stencil aperture design'),
                    'Poor gasketing between stencil and PCB'
                ],
                'Gasket': [
                    ('Is there a good seal between the stencil and the PCB?',
                     'Poor gasketing between stencil and PCB')
                ],
                'Screen Printer': [
                    'Screen printer misalignment',
                    'Bad separation speed',
                    ('Are the squeegee blades undamaged?', 'Damaged squeegee blades'),
                    'Bad/Inaccurate component placement'
                ],
                'Squeegee Blades': ['', 'Bad/Inaccurate component placement'],
                'Reflow Profile': [('', 'Incorrect reflow profile')],
                'Solder Paste': [
                    ('', 'Poor solder paste condition'),
                    ('', 'Dry solder paste')
                ]
            }
        },
    'Tombstoning': {
        'Causes': [
            ('', 'Component body not covering > 50% of both pads')
        ]
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
