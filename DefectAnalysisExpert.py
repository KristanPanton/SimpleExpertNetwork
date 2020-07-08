from experta import *
from experta.utils import unfreeze
# from tkinter import *
# from tkinter.ttk import Style, Button, Frame

# ------------------------------------------------------------------------------ #
# Facts from https://www.alphaassembly.com/Products/Alpha-Troubleshooting-Guides #
# ------------------------------------------------------------------------------ #

# TODO:
# Add more defects
# Add related components to each Issue()
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


def MAYBE(*patterns):
    return AND(
        *[OR(p, NOT(p)) for p in patterns]
    )


class Defect(Fact):
    _0 = Field(str, mandatory=True)
    possible_causes = Field(list, default=[])


class Issue(Fact):
    recommendations = Field(list, default=[])
    possible_cause = Field(str)
    related_components = Field(list, default=[])


class Action(Fact):
    # Action type Eg. Investigate
    _0 = Field(str, mandatory=True)
    done = Field(bool, default=False)


class Component(Fact):
    pass


class PCB(Component):
    solder_mask_removed_between_adjacent_pads = Field(bool, default=True)
    # coplanarity_present = Field(bool, default=False)


class Stencil(Component):
    clean = Field(bool, default=True)
    tension_tight = Field(bool, default=True)
    aperture_smaller_than_landing_pad = Field(bool, default=True)
    minimum_print_pressure_good = Field(bool, default=True)
    dry_after_clean = Field(bool, default=True)
    dry_before_next_print = Field(bool, default=True)
    wiped_frequently = Field(bool, default=True)


class ScreenPrinter(Component):
    zero_print_gap_present = Field(bool, default=True)
    print_accurate = Field(bool, default=True)
    print_consistent = Field(bool, default=True)
    pcb_support_good = Field(bool, default=True)
    separation_speed_good = Field(bool, default=True)
    squeegee_blade_condition_good = Field(bool, default=True)
    operating_temperature_good = Field(bool, default=True)
    # operating_temperature_celsius = Field(float, default=25.0)
    operating_humidity_good = Field(bool, default=True)
    # operating_humidity_percent = Field(float, default=50)


class SolderPaste(Component):
    expired = Field(bool, default=False)
    passed_hot_cold_slump_test = Field(bool, default=True)


class ReflowOven(Component):
    reflow_profile_soak_extended = Field(bool, default=False)


class PickAndPlaceMachine(Component):
    component_placement_pressure_good = Field(bool, default=True)
    components_placement_height = Field(float)
    solder_paste_height = Field(float)


class DefectAnalysisEngine(KnowledgeEngine):
    @DefFacts()
    def initiate_analysis(self):
        print("This is an expert system for defect analysis.")
        print('Answer the following questions.')

        print("What type of defect occurred?")
        [print(f"{i}. {defect}") for i, defect in enumerate(DEFECTS_LIST, 1)]
        while True:
            try:
                defect = DEFECTS_LIST[abs(int(input("Enter number: ")) - 1)]
                print(f"\nYour choice is {defect}")
                # yield Action('Investigate')
                yield Action('Investigate', Defect(defect))
                break
            except (ValueError, IndexError):
                print("Invalid Input!")

    # ~~~~~~~~~~< Bridging Rules >~~~~~~~~~~
    @Rule(Action('Investigate', Defect('Bridging')))
    def investigate_bridging(self):
        print("Investigating 'Bridging' defect...")
        self.declare(PCB(solder_mask_removed_between_adjacent_pads=get_yorn(
            'Have the solder mask between adjacent pads been removed?')))
        self.declare(
            Stencil(clean=get_yorn('Is the stencil clean?'), tension_tight=get_yorn('Is the stencil tension tight?'),
                    aperture_smaller_than_landing_pad=get_yorn('Is the stencil aperture smaller than the landing pad?'),
                    minimum_print_pressure_good=get_yorn('Is the minimum print pressure sufficient?'),
                    dry_after_clean=get_yorn('Was the stencil dry after cleaning?'),
                    dry_before_next_print=get_yorn('Was the stencil dry before the next print?'),
                    wiped_frequently=get_yorn('Is the stencil wiped frequently?')
                    ))

        self.declare(ScreenPrinter(zero_print_gap_present=get_yorn('Is there a zero print gap?'),
                                   print_accurate=get_yorn('Are the prints accurate?'),
                                   print_consistent=get_yorn('Are the prints consistent?'),
                                   pcb_support_good=get_yorn('Are the PCBs sufficiently supported?'),
                                   separation_speed_good=not get_yorn("Are there any 'dog ears' on the board?"),
                                   squeegee_blade_condition_good=not get_yorn('Are the squeegee blades damaged?'),
                                   operating_temperature_good=get_yorn('Are the operating temperatures verified?')
                                   ))

        self.declare(SolderPaste(expired=get_yorn('Has the solder paste expired?'),
                                 passed_hot_slump_test=get_yorn(
                                     'Has the solder paste passed the cold and hot slump test?')))

        self.declare(
            ReflowOven(reflow_profile_soak_extended=get_yorn('Is there an extended soak in the reflow profile?')))

        comp_placement_pressure_bool = get_yorn(
            'Is there any solder paste squeezed out of the pads?')

        while True:
            try:
                self.declare(PickAndPlaceMachine(
                    component_placement_pressure_good=comp_placement_pressure_bool,
                    components_placement_height=float(input('Component placement height: ')),
                    solder_paste_height=float(input('Solder paste height: '))))
                break
            except (ValueError, OverflowError):
                print('Invalid Input!')

    # AS.i1 << Issue('Component damaged before placement')
    @Rule(PCB(solder_mask_removed_between_adjacent_pads=False))
    def declare_coplanarity(self):
        # if i1:
        # reccs.append('Set up coplanarity check on Pick-and-Place machine')
        self.declare(Issue('Coplanarity', recommendations=['Remove solder mask between adjacent pads']))

    @Rule(Stencil(tension_tight=False))
    def declare_poor_stencil_tension(self):
        self.declare(Issue('Poor stencil tension', recommendations=['Ensure there is sufficient stencil tension']))

    @Rule(Stencil(aperture_smaller_than_landing_pad=False))
    def declare_faulty_aperture_design(self):
        self.declare(Issue('Faulty stencil aperture design',
                           recommendations=['Ensure that the stencil aperture is smaller than the landing pad']))

    @Rule(ScreenPrinter(zero_print_gap_present=False))
    def declare_zero_print_gap_absent(self):
        self.declare(Issue('Zero print gap absent', recommendations=['Ensure that there is a zero print gap']))

    @Rule(
        AND(
            MAYBE(
                Issue('Coplanarity', recommendations=MATCH.reccs1),
                Issue('Poor stencil tension', recommendations=MATCH.reccs2),
                Issue('Faulty stencil aperture design', recommendations=MATCH.reccs3),
                Issue('Zero print gap absent', recommendations=MATCH.reccs4)
            ),
            OR(
                Issue('Coplanarity', recommendations=W()),
                Issue('Poor stencil tension', recommendations=W()),
                Issue('Faulty stencil aperture design', recommendations=W()),
                Issue('Zero print gap absent', recommendations=W())
            )
        )
    )
    def declare_poor_stencil_to_pcb_gasketing(self, reccs1=[], reccs2=[], reccs3=[], reccs4=[]):
        list_reccs = [reccs1, reccs2, reccs3, reccs4]
        list_reccs = [unfreeze(r) for r in list_reccs]
        print('Poor stencil to PCB gasketing rule: ', list_reccs)
        # Flattens list of recommendations
        reccs = [recc
                 for sublist in list_reccs
                 for recc in sublist]
        print('Poor stencil to PCB gasketing rule: ', reccs)
        related_components = []

        self.declare(Issue('Poor stencil to PCB gasketing', recommendations=reccs))

    @Rule(Stencil(aperture_smaller_than_landing_pad=False))
    def declare_poor_aperture_design(self):
        self.declare(Issue('Stencil aperture design',
                           recommendations=['E']))

    # If stencil has any of these attributes and issues does or doesn't exist declare or modify unclean stencil
    @Rule(
        AND(
            MAYBE(
                AS.sp1 << ScreenPrinter(zero_print_gap_present=False),
                AS.s2 << Stencil(minimum_print_pressure_good=False),
                AS.s3 << Stencil(clean=False),
                AS.s4 << Stencil(wiped_frequently=False)
            ),
            OR(
                ScreenPrinter(zero_print_gap_present=False),
                Stencil(minimum_print_pressure_good=False),
                Stencil(clean=False),
                Stencil(wiped_frequently=False)
            )
        )
    )
    def declare_unclean_stencil(self, sp=None, s1=None, s2=None, s3=None):
        reccs = []
        if sp:
            reccs.append('Ensure zero print gap')
        if s1:
            reccs.append('Ensure minimum print pressure')
        if s2:
            reccs.append('Clean stencil')
        if s3:
            reccs.append('Increase wipe frequency')

        self.declare(Issue('Unclean stencil', recommendations=reccs))

    @Rule(NOT(ScreenPrinter(print_accurate=True, print_consistent=True)))
    def declare_misaligned_print(self):
        self.declare(Issue('Screen printer misalignment',
                           recommendations=['Ensure print accuracy and consistency for both print and strokes']))

    @Rule(NOT(Stencil(dry_after_clean=True, dry_before_next_print=True)))
    def declare_smearing(self):
        self.declare(Issue('Smearing during printing process',
                           recommendations=['Ensure stencil is dry after cleaning and before next print']))

    @Rule(ScreenPrinter(separation_speed_good=False))
    def declare_peaking(self):
        self.declare(Issue('Peaking', recommendations=['Adjust separation speed']))

    @Rule(ScreenPrinter(squeegee_blade_condition_good=False))
    def declare_uneven_print_pressure(self):
        self.declare(Issue('Uneven print pressure', recommendations=['Replace squeegee blade']))

    @Rule(
        AND(
            MAYBE(
                Issue('Peaking', recommendations=MATCH.reccs1),
                Issue('Uneven print pressure', recommendations=MATCH.reccs2),
                AS.sp << ScreenPrinter(pcb_support_good=False)
            ),
            OR(
                Issue('Peaking', recommendations=W()),
                Issue('Uneven print pressure', recommendations=W()),
                ScreenPrinter(pcb_support_good=False)
            )
        )
    )
    def declare_poor_print_definition(self, reccs1=None, reccs2=None, sp=None):
        reccs = []
        if reccs1:
            reccs.extend(reccs1)
        if reccs2:
            reccs.extend(reccs2)
        if sp:
            reccs.append('Ensure sufficient PCB support')

        self.declare(Issue('Poor print definition', recommendations=reccs))

    @Rule(PickAndPlaceMachine(component_placement_pressure_good=False))
    def declare_narrow_gap_between_pads(self):
        self.declare(Issue('Narrow gap between pads',
                           recommendations=['Verify component placement pressure',
                                            'Use X-ray to verify BGA placement',
                                            'Use microscope for QFPs']))

    @Rule(PickAndPlaceMachine(components_placement_height=MATCH.cph, solder_paste_height=MATCH.sph))
    def declare_excessive_component_pressure(self):
        pass

    @Rule(ReflowOven(reflow_profile_soak_extended=True))
    def declare_hot_paste_slump(self):
        self.declare(Issue('Hot paste slump', recommendations=['Reduce soak']))

    @Rule(SolderPaste(expired=True))
    def declare_solder_paste_expired(self):
        self.declare(Issue('Solder paste expired',
                           recommendations=['Replace solder paste', 'Do not mix old and new solder paste']))

    @Rule(MAYBE(Issue('Solder paste expired', recommendations=MATCH.recc),
                ScreenPrinter(operating_temperature_good=False, operating_humidity_good=False)))
    def declare_dry_solder_paste(self, recc=None):
        if recc:
            list_reccs = unfreeze(recc)
            list_reccs.extend(['Check temperature and humidity inside screen printer'])
            self.declare(Issue('Dry solder paste', recommendations=list_reccs))
        else:
            self.declare(
                Issue('Dry solder paste', recommendations=['Check temperature and humidity inside screen printer']))


DAEngine = DefectAnalysisEngine()
DAEngine.reset()
watch('RULES', 'FACTS', 'ACTIVATIONS')
DAEngine.run()
# print("FACTS:", DAEngine.facts)
# print('FACTLIST TYPE:', type(DAEngine.facts))
