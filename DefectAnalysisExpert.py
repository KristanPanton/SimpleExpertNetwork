from experta import *

# Facts from https://www.alphaassembly.com/Products/Alpha-Troubleshooting-Guides

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

COMPONENT_CAUSES = {
    'Bridging': {
        'PCB': [
            'Coplanarity'
        ],
        'Stencil': [
            'Insufficient stencil tension',
            'Damaged stencil',
            'Unclean stencil',
            'Inappropriate stencil aperture design',
        ],
        'Gasket': [
            'Poor seal between stencil and PCB'
        ],
        'Screen Printer': [
            'Screen printer misalignment',
            'Poor print definition',
            'Bad/Inaccurate component placement'
        ],
        'Squeegee Blades': [
            'Damaged squeegee blades',
        ],
        'Pick-and-Place Machine': [
            'Component placement inaccuracy',
            'Excessive component placement pressure'
        ],
        'Reflow Oven': [
            'Incorrect reflow profile'
        ],
        'Solder Paste': [
            'Dry solder paste'
        ]
    }
}

# Causes and their related components
CAUSE_COMPONENTS = {
    'Bridging': {
        'Coplanarity': ['PCB'],
        'Insufficient stencil tension': ['Stencil'],
        'Damaged stencil': ['Stencil'],
        'Unclean stencil': ['Stencil'],
        'Inappropriate stencil aperture design': ['Stencil'],
        'Poor seal between stencil and PCB': ['Gasket', 'PCB', 'Stencil'],
        'Screen printer misalignment': ['Screen Printer'],
        'Poor print definition': ['Screen Printer'],
        'Bad/Inaccurate component placement': ['Screen Printer'],
        'Damaged squeegee blades': ['Squeegee Blades'],
        'Component placement inaccuracy': ['Pick-and-Place Machine'],
        'Excessive component placement pressure': ['Pick-and-Place Machine'],
        'Incorrect reflow profile': ['Reflow Oven'],
        'Dry solder paste': ['Solder Paste']
    }
}
# user input has to equal corresponding bool for cause to be declared
CAUSE_QUERIES = {
    'Bridging': {
        'Coplanarity': [
            ('Have the solder masks been removed between adjacent pads?', False)
        ],
        'Insufficient stencil tension': [('Is the stencil tension sufficient?', False)],
        'Damaged stencil': [('Is the stencil undamaged?', False)],
        'Unclean stencil': [
            ('Is the stencil cleaned frequently?', False)
        ],
        'Inappropriate stencil aperture design': [('Are the stencil apertures slightly smaller than the pads?', False)],
        'Poor seal between stencil and PCB': [
            ('Is there a zero print gap between the stencil and PCB?', False),
            ('Is the solder paste smear underneath the stencil consistent?', False)
        ],
        'Screen printer misalignment': [('Is the print accurate and consistent?', False)],
        'Poor print definition': [("Is the solder paste on the components relatively flat and straight?", False)],
        'Bad/Inaccurate component placement': [('Is there a relatively narrow gap between pads?', True)],
        'Damaged squeegee blades': [('Are the squeegee blades undamaged?', False)],
        'Component placement inaccuracy': [('Are the component placements accurate?', False)],
        'Excessive component placement pressure': [
            ('Has solder paste been squeezed out of pads?', True)
        ],
        'Incorrect reflow profile': [("Is there an extended soak in the reflow profile?", True)],
        'Dry solder paste': [
            ('Has the solder paste expired?', True),
        ]
    }
}

CAUSE_RECOMMENDATIONS = {
    'Bridging': {
        'Coplanarity': [
            'Remove solder mask between adjacent pads'
        ],
        'Insufficient stencil tension': [
            'Ensure stencil tension is tight'
        ],
        'Damaged stencil': [
            'Replace stencil'
        ],
        'Unclean stencil': [
            'Clean stencil',
            'Use different cleaning chemicals',
            'Increase wipe frequency',
            'Ensure minimum print pressure'
        ],
        'Inappropriate stencil aperture design': [
            'Ensure that the aperture size is smaller than the landing pad size'
        ],
        'Poor seal between stencil and PCB': [
            'Ensure zero print gap between stencil and PCB',
            'Shrink print gap between the stencil and PCB',
            'Check paste smear underneath stencil',
            'Ensure there is sufficient stencil tension'
        ],
        'Screen printer misalignment': [
            'Ensure print accuracy and consistency for both print and strokes'
        ],
        'Poor print definition': [
            'Check board support',
            'Adjust separation speed; dependent on solder paste chemistry',
        ],
        'Bad/Inaccurate component placement': [
            'Verify component placement pressure',
            'Use X-ray to verify BGA placement',
            'Use microscope for QFPs'
        ],
        'Damaged squeegee blades': [
            'Replace squeegee blades'
        ],
        'Component placement inaccuracy': [],
        'Excessive component placement pressure': [
            'Verify actual component height against height in component placement machine',
            'Component placement height should be ±1/3 of solder paste height'
        ],
        'Incorrect reflow profile': [
            'Adopt a straight ramp to spike profile, without soak zone if possible'
        ],
        'Dry solder paste': [
            'Do not mix old solder paste with new solder paste'
        ]
    }
}


def get_yorn(query):
    while True:
        inp = str(input(f"{query} "))
        if len(inp) > 0 and inp[0].lower() in 'yn':
            if inp[0] == 'y':
                return True
            else:
                return False
        else:
            print("Invalid Input!")


class Cause(Fact):
    # list of recommendations on how to resolve defect
    recommendations = Field(list)
    # Corresponding question
    why = Field(str)
    related_components = Field(list)


class Defect(Fact):
    # list of possible defect causes
    # causes_list = Field(list, mandatory=True)
    pass


# class Component(Fact):
#     # condition = Field(str)
#     pass


class Action(Fact):
    pass


class BridgingRules:
    @Rule(AS.action << Action('Investigate'),
          AS.defect << Defect())
    def investigate_components(self, action, defect):
        causes = []
        for cause_key, queries in CAUSE_QUERIES[defect[0]].items():
            for query in queries:
                print()
                ans = get_yorn(query[0])
                if ans == query[1]:
                    cause = Cause(cause_key,
                                  why=f"Your answer to '{query[0]}' was {'YES' if ans else 'NO'}",
                                  related_components=CAUSE_COMPONENTS[defect[0]][cause_key],
                                  recommendations_list=CAUSE_RECOMMENDATIONS[defect[0]][cause_key])
                    causes.append(cause)

        causes = list(set(causes))

        self.modify(defect, causes_list=causes)
        self.modify(action, _0='Report')

    @Rule(AS.action << Action('Report'), AS.defect << Defect())
    def report_findings(self, action, defect):
        print()
        print(defect[0].upper(), 'CAUSES:')
        print('=' * 80)
        for cause in defect['causes_list']:
            print("\nPOSSIBLE CAUSE:", cause[0])
            print('WHY:', cause['why'])
            print('RELATED COMPONENT(S): ', end='')
            print(*cause['related_components'], sep=', ')
            print("RECOMMENDATIONS(S):")
            for i, recommendations in enumerate(cause['recommendations_list'], 1):
                print(f"{i}. {recommendations}")
            print('-' * 80)
        self.retract(action)


class DefectAnalysisExpert(BridgingRules, KnowledgeEngine):
    @DefFacts()
    def initiate(self):
        # print("This is an expert system for defect analysis.")
        # print("What type of defect occurred?")
        # [print(f"{i}. {defect}") for i, defect in enumerate(DEFECTS_LIST, 1)]
        # while True:
        #     try:
        #         defect = DEFECTS_LIST[abs(int(input("Enter number: ")) - 1)]
        #         print(f"\nYour choice is {defect}")
        #         yield Action('Investigate')
        #         yield Defect(defect, causes_list=[])
        #         break
        #     except (ValueError, IndexError):
        #         print("Invalid Input!")
        print('This is an expert system for SMT bridging analysis.')
        print('Answer the following questions.')
        yield Action('Investigate')
        yield Defect('Bridging')


engine = DefectAnalysisExpert()
engine.reset()
# watch('RULES', 'FACTS', 'ACTIVATIONS')
engine.run()
