from experta import *

DEFECTS = ['Bridging', 'Insufficient Fill', 'Random Solder Balls', 'Solder Spattering', 'Mid-Chip Solder Balls',
           'Tombstoning', 'Voiding', 'BGA Head-on-Pillow', 'Grainy Joints']


def get_option():
    while True:
        try:
            inp = int(input('What type of defect occurred: '))
            if 0 > inp > len(DEFECTS) + 1:
                raise ValueError
            return inp
        except ValueError:
            print("Invalid Input!")

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
    pass


class Cause(Fact):
    pass


class Action(Fact):
    pass


class BridgingRules:
    @Rule(Action('Investigate'), Defect('Bridging'), Cause('PCB'))
    def bridge_investigate_pcb(self):
        response = get_yorn("Have you removed solder masks between adjacent pads? (yes/no) ")
        self.declare(Fact(remove_solder_masks=response))
        response = get_yorn("Is the PCB support sufficient? (yes/no) ")
        self.declare(Fact(pcb_support_sufficient=response))
        response = get_yorn("Is the gasketing between the PCB and the stencil acceptable? (yes/no) ")
        self.declare(Fact(pcb_stencil_gasketing_acceptable=response))
        if response:
            self.retract(Cause('PCB'))

    @Rule(Defect('Bridging'), Cause('Stencil'))
    def bridge_investigate_stencil(self):
        response = get_yorn("Is the ")

    @Rule(Defect('Bridging'), Cause('Screen Printer'))
    def bridge_investigate_screen_printer(self):
        pass

    @Rule(Defect('Bridging'), Cause('Component Placement'))
    def bridge_investigate_component_placement(self):
        pass

    @Rule(Defect('Bridging'), Cause('Reflow Profile'))
    def bridge_investigate_reflow_profile(self):
        pass

    @Rule(Defect('Bridging'), Cause('Solder Paste'))
    def bridge_investigate_solder_paste(self):
        pass


class InsufficientFillRules:
    @Rule(Defect('Insufficient Fill'), Cause('Stencil'))
    def ins_fill_investigate_stencil(self):
        pass

    @Rule(Defect('Insufficient Fill'), Cause('Screen Printer'))
    def ins_fill_investigate_screen_printer(self):
        pass


class InsufficientSolderRules:
    @Rule(Defect('Insufficient Solder'), Cause('Stencil'))
    def ins_solder_investigate_istencil(self):
        pass

    @Rule(Defect('Insufficient Solder'), Cause('Screen Printer'))
    def ins_solder_investigate_screen_printer(self):
        pass

    @Rule(Defect('Insufficient Solder'), Cause('Reflow Profile'))
    def ins_solder_investigate_reflow_profile(self):
        pass

    @Rule(Defect('Insufficient Solder'), Cause('Solder Paste'))
    def ins_solder_investigate_solder_paste(self):
        pass


class RandomSolderBallsRules:
    @Rule(Defect('RandomSolderBalls'), Cause('Stencil'))
    def rsb_investigate_stencil(self):
        pass

    @Rule(Defect('RandomSolderBalls'), Cause('Reflow Profile'))
    def rsb_investigate_reflow_profile(self):
        pass

    @Rule(Defect('RandomSolderBalls'), Cause('PCB Moisture'))
    def rsb_investigate_pcb_moisture(self):
        pass

    @Rule(Defect('RandomSolderBalls'), Cause('Solder Paste'))
    def rsb_investigate_solder_paste(self):
        pass


class SolderSpatteringRules:
    @Rule(Defect('Solder Spattering'), Cause('PCB'))
    def solder_spatter_investigate_pcb(self):
        pass

    @Rule(Defect('Solder Spattering'), Cause('Screen Printer'))
    def solder_spatter_investigate_screen_printer(self):
        pass

    @Rule(Defect('Solder Spattering'), Cause('Reflow Profile'))
    def solder_spatter_investigate_reflow_profile(self):
        pass


class MidChipSolderBallsRules:
    @Rule(Defect('Mid-Chip Solder Balls'), Cause('PCB'))
    def mcsb_investigate_pcb(self):
        pass

    @Rule(Defect('Mid-Chip Solder Balls'), Cause('Stencil Design'))
    def mcsb_investigate_stencil_design(self):
        pass

    @Rule(Defect('Mid-Chip Solder Balls'), Cause('Screen Printer'))
    def mcsb_investigate_screen_printer(self):
        pass

    @Rule(Defect('Mid-Chip Solder Balls'), Cause('Reflow Profile'))
    def mcsb_investigate_reflow_profile(self):
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
    def _initial_conditions(self):
        yield Action('Investigate')

    @Rule(Defect('Bridging'))
    def investigate_bridging(self):
        self.declare(Cause('PCB'))
        self.declare(Cause('Stencil'))
        self.declare(Cause('Screen Printer'))
        self.declare(Cause('Component Placement'))
        self.declare(Cause('Reflow Profile'))
        self.declare(Cause('Solder Paste'))

    @Rule(Defect('Insufficient Fill'))
    def insufficient_fill(self):
        self.declare(Cause('Stencil'))
        self.declare(Cause('Screen Printer'))


engine = DefectAnalysisExpert()
engine.reset()
for i, defect in enumerate(DEFECTS, 1):
    print(f'{i}.', defect)
print(f'{len(DEFECTS) + 1}.', "Not sure")
ans = get_option()
if ans > len(DEFECTS):
    engine.declare(Action('Investigate'))
else:
    engine.declare(Defect(DEFECTS[ans-1]))

watch('RULES', 'FACTS', 'ACTIVATIONS')
engine.run()
