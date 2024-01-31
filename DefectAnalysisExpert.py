from pprint import PrettyPrinter
from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk, Image
from experta import *
from experta.utils import unfreeze
from graphviz import Digraph
from ttkthemes import ThemedTk

# ------------------------------------------------------------------------------ #
# Facts from https://www.alphaassembly.com/Products/Alpha-Troubleshooting-Guides #
# ------------------------------------------------------------------------------ #
# TODO
#   - Remove duplicated code

pprint = PrettyPrinter(indent=4).pprint

DEFECTS_LIST = ['Bridging',
                'Insufficient Fill',
                'Random Solder Balls',
                'Solder Spattering',
                'Mid-Chip Solder Balls',
                'Tombstoning',
                'Voiding',
                'BGA Head-on-Pillow',
                'Grainy Joints']

DEFECT_COMPONENTS = {
    'Bridging': {
        'PCB': {
            'solder_mask_removed_between_adjacent_pads': 'Solder mask between adjacent pads removed'
        },
        'Stencil': {
            'clean': 'Tight stencil tension',
            'aperture_smaller_than_landing_pad': 'Stencil aperture smaller than landing pad',
            'minimum_print_pressure_good': 'Sufficient minimum print pressure',
            'dry_after_clean': 'Stencil dry after cleaning',
            'dry_before_next_print': 'Stencil dry before next print',
            'wiped_frequently': 'Stencil wiped frequently',
        },
        'Screen Printer': {
            'zero_print_gap_present': 'Zero print gap present',
            'print_accurate': 'Prints are accurate',
            'print_consistent': 'Prints are consistent',
            'pcb_support_good': 'Sufficient PCB support',
            'separation_speed_good': "'Dog ears' present",
            'squeegee_blade_condition_good': 'Squeegee blades undamaged',
            'operating_temperature_good': 'Correct operating temperature',
            'operating_humidity_good': 'Correct operating humidity'
        },
        'Solder Paste': {
            'expired': 'Expired solder paste',
            'passed_hot_slump_test': 'Hot and cold slump test passed',
        },
        'Reflow Oven': {
            'reflow_profile_soak_extended': 'Extended soak in the reflow profile'
        },
        'Pick-and-Place Machine': {
            'component_placement_pressure_good': 'Solder paste squeezed out of pads'
        }
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


def MAYBE(*patterns):
    return AND(
        *[OR(p, NOT(p)) for p in patterns]
    )


class Defect(Fact):
    _0 = Field(str, mandatory=True)
    # possible_causes = Field(list, default=[])


class Issue(Fact):
    recommendations = Field(list, default=[])
    why = Field(list, default=[])
    end = Field(bool, default=True)
    # related_components = Field(list, default=[])


# class Action(Fact):
#     # Action type Eg. Investigate
#     _0 = Field(str, mandatory=True)
#     done = Field(bool, default=False)


class Component(Fact):
    pass


class PCB(Component):
    solder_mask_removed_between_adjacent_pads = Field(bool, default=True)


class Stencil(Component):
    clean = Field(bool, default=True)
    tension_tight = Field(bool, default=True)
    aperture_smaller_than_landing_pad = Field(bool, default=True)
    minimum_print_pressure_good = Field(bool, default=True)
    dry_after_clean = Field(bool, default=True)
    dry_before_next_print = Field(bool, default=True)
    wiped_frequently = Field(bool, default=True)


class ScreenPrinter(Component):
    # Bridging fields
    zero_print_gap_present = Field(bool, default=True)
    print_accurate = Field(bool, default=True)
    print_consistent = Field(bool, default=True)
    pcb_support_good = Field(bool, default=True)
    separation_speed_good = Field(bool, default=True)
    squeegee_blade_condition_good = Field(bool, default=True)
    operating_temperature_good = Field(bool, default=True)
    operating_humidity_good = Field(bool, default=True)
    # operating_temperature_celsius = Field(float, default=25.0)
    # operating_humidity_percent = Field(float, default=50)


class SolderPaste(Component):
    expired = Field(bool, default=False)
    passed_hot_cold_slump_test = Field(bool, default=True)


class ReflowOven(Component):
    reflow_profile_soak_extended = Field(bool, default=False)


class PickAndPlaceMachine(Component):
    component_placement_pressure_good = Field(bool, default=True)
    component_placement_accurate = Field(bool, default=True)

    # components_placement_height = Field(float)
    # solder_paste_height = Field(float)


COMPONENT_BINDINGS = {
    'PCB': PCB,
    'Stencil': Stencil,
    'Screen Printer': ScreenPrinter,
    'Solder Paste': SolderPaste,
    'Reflow Oven': ReflowOven,
    'Pick-and-Place Machine': PickAndPlaceMachine
}


class VertScrollFrame(Frame):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        self.canvas = Canvas(self)
        scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class HorScrollFrame(Frame):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        self.canvas = Canvas(self)
        self.scrollbar = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")


class DefectAnalysisEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.dot = Digraph(comment='Defect Analysis Tree',
                           node_attr={'color': 'lightblue2', 'style': 'filled', 'shape': 'box'})
        self.dot.format = 'png'
        self.dot.filename = 'graph-output/defect-analysis-tree.gv'
        self.defect = ''
        self.issues = []

    # def declare(self, f):
    #     self.issues.append(f)
    #     self.declare(f)

    def find_issue(self, s):
        for i, issue in self.facts.items():
            if isinstance(issue, Issue) and s == issue[0]:
                print('Issue:', issue[0])
                return issue
        return None

    @Rule(Defect(MATCH.name))
    def set_defect(self, name):
        self.defect = name

    def create_graph(self):
        # print(self.issues)
        for i, issue in self.facts.items():
            if isinstance(issue, Issue):
                self.dot.node(issue[0])
                for why in issue['why']:
                    self.dot.node(why)
                    self.dot.edge(why, issue[0])
                # self.dot.edge(issue[0], self.defect)

    def clear_graph(self):
        self.dot.body.clear()

    @Rule(PCB(solder_mask_removed_between_adjacent_pads=False))
    def declare_coplanarity(self):
        self.declare(Issue('Coplanarity', recommendations=['Remove solder mask between adjacent pads'],
                           why=['Solder mask between adjacent pads not removed']))

    @Rule(Stencil(tension_tight=False))
    def declare_poor_stencil_tension(self):
        self.declare(
            Issue('Poor stencil tension', recommendations=['Ensure there is sufficient stencil tension'],
                  why=['Stencil tension loose']))

    @Rule(Stencil(aperture_smaller_than_landing_pad=False))
    def declare_faulty_aperture_design(self):
        self.declare(Issue('Faulty stencil aperture design',
                           recommendations=[
                               'Ensure that the stencil aperture is smaller than the landing pad'],
                           why=['Aperture not slightly smaller than landing pad']))

    @Rule(ScreenPrinter(zero_print_gap_present=False))
    def declare_zero_print_gap_absent(self):
        self.declare(
            Issue('Zero print gap absent', recommendations=['Ensure that there is a zero print gap'], why=[]))

    @Rule(OR(
        AS.iss_param1 << Issue('Coplanarity'),
        AS.iss_param2 << Issue('Poor stencil tension'),
        AS.iss_param3 << Issue('Faulty stencil aperture design'),
        AS.iss_param4 << Issue('Zero print gap absent')
    ))
    def declare_poor_stencil_to_pcb_gasketing(self, iss_param1=None, iss_param2=None, iss_param3=None, iss_param4=None):
        current_param = unfreeze([i for i in [iss_param1, iss_param2, iss_param3, iss_param4] if i][0])
        current_recs = unfreeze(current_param['recommendations'])
        if tbmodified := self.find_issue('Poor stencil to PCB gasketing'):
            tbmodified_whys = unfreeze(tbmodified['why'])
            tbmodified_whys.append(current_param[0])
            recs = unfreeze(tbmodified['recommendations'])
            for rec in current_recs:
                if rec not in tbmodified['recommendations']:
                    recs.append(rec)
            self.modify(tbmodified, recommendations=recs, why=tbmodified_whys)

        else:
            self.declare(
                Issue('Poor stencil to PCB gasketing', recommendations=current_recs, why=current_param['why']))

    @Rule(OR(
        AS.sten_param1 << Stencil(minimum_print_pressure_good=False),
        AS.sten_param2 << Stencil(clean=False),
        AS.sten_param3 << Stencil(wiped_frequently=False)
    ))
    def declare_unclean_stencil(self, sten_param1=None, sten_param2=None, sten_param3=None):
        recs = []
        whys = []

        if sten_param1:
            whys.append('Minimum print pressure insufficient')
            recs.append('Verify minimum print pressure')

        elif sten_param2:
            whys.append('Unclean stencil')
            recs.append('Clean stencil')

        elif sten_param3:
            whys.append('Wipe frequency too low')
            recs.append('Increase wipe frequency')

        if tbmodified := self.find_issue('Dry solder paste'):
            ci_recs = unfreeze(tbmodified['recommendations'])
            ci_whys = unfreeze(tbmodified['why'])

            if not any(why in ci_whys for why in whys):
                ci_whys.extend(whys)
                ci_recs.extend(recs)

                self.modify(tbmodified, recommendations=ci_recs, why=ci_whys)

        else:
            self.declare(Issue('Unclean stencil', recommendations=recs, why=whys))

    @Rule(NOT(ScreenPrinter(print_accurate=True, print_consistent=True)))
    def declare_misaligned_print(self):
        self.declare(Issue('Screen printer misalignment',
                           recommendations=[
                               'Ensure print accuracy and consistency for both print and strokes'],
                           why=['Print is not accurate or consistent']))

    @Rule(NOT(Stencil(dry_after_clean=True, dry_before_next_print=True)))
    def declare_smearing(self):
        self.declare(Issue('Smearing during printing process',
                           recommendations=['Ensure stencil is dry after cleaning and before next print'],
                           why=['Stencil is was not dry after cleaning or before next print']))

    @Rule(ScreenPrinter(separation_speed_good=False))
    def declare_peaking(self):
        self.declare(
            Issue('Peaking', recommendations=['Adjust separation speed'], why=['Incorrect separation speed']))

    @Rule(ScreenPrinter(squeegee_blade_condition_good=False))
    def declare_uneven_print_pressure(self):
        self.declare(
            Issue('Uneven print pressure', recommendations=['Replace squeegee blade'], why=['Squeegee blade damaged']))

    @Rule(OR(
        AS.iss_param1 << Issue('Peaking'),
        AS.iss_param2 << Issue('Uneven print pressure'),
        AS.sp_param << ScreenPrinter(pcb_support_good=False)
    ))
    def declare_poor_print_definition(self, iss_param1=None, iss_param2=None, sp_param=None):
        recs = []
        whys = []

        if iss_param1:
            whys.append(iss_param1[0])
            recs.extend(iss_param1['recommendations'])

        elif iss_param2:
            whys.append(iss_param2[0])
            recs.extend(iss_param2['recommendations'])

        else:
            whys.append('Bad PCB support')
            recs.append('Ensure good PCB support')

        if tbmodified := self.find_issue('Poor print definition'):
            # print(tbmodified)
            ci_recs = unfreeze(tbmodified['recommendations'])
            ci_whys = unfreeze(tbmodified['why'])

            if not any(why in ci_whys for why in whys):
                ci_whys.extend(whys)
                ci_recs.extend(recs)

                self.modify(tbmodified, recommendations=ci_recs, why=ci_whys)

        else:
            self.declare(Issue('Poor print definition', recommendations=recs, why=whys))

    @Rule(PickAndPlaceMachine(component_placement_accurate=False))
    def declare_narrow_gap_between_pads(self):
        self.declare(Issue('Narrow gap between pads',
                           recommendations=['Verify component placement pressure',
                                            'Use X-ray to verify BGA placement',
                                            'Use microscope for QFPs'],
                           why=['Inaccurate component placement']))

    @Rule(PickAndPlaceMachine(component_placement_pressure_good=False))
    def declare_excessive_component_pressure(self):
        self.declare(Issue('Excessive component placement pressure', recommendations=[
            'Verify actual component height data entered in the Pick-and-Place machine',
            'Ensure that component placement height is ±1/3 of paste height'],
                           why=['Bad component placement pressure']))

    @Rule(ReflowOven(reflow_profile_soak_extended=True))
    def declare_hot_paste_slump(self):
        self.declare(
            Issue('Hot paste slump', recommendations=['Reduce soak'], why=['Reflow profile soak extended']))

    @Rule(SolderPaste(expired=True))
    def declare_solder_paste_expired(self):
        self.declare(Issue('Solder paste expired',
                           recommendations=['Replace solder paste', 'Do not mix old and new solder paste'],
                           why=['Expired solder paste']))

    @Rule(OR(
        AS.iss_param << Issue('Solder paste expired'),
        AS.sp_param1 << ScreenPrinter(operating_temperature_good=False),
        AS.sp_param2 << ScreenPrinter(operating_humidity_good=False)
    ))
    def declare_dry_solder_paste(self, iss_param=None, sp_param1=None, sp_param2=None):
        recs = []
        whys = []

        if iss_param:
            whys.append(iss_param[0])
            recs.append('Replace solder paste')

        elif sp_param1:
            whys.append('Wrong operating temperature')
            recs.append('Check temeperature inside screen printer')

        else:
            whys.append('Wrong operating humidity')
            recs.append('Check humidity inside screen printer')

        if tbmodified := self.find_issue('Dry solder paste'):
            ci_recs = unfreeze(tbmodified['recommendations'])
            ci_whys = unfreeze(tbmodified['why'])

            if not any(why in ci_whys for why in whys):
                ci_whys.extend(whys)
                ci_recs.extend(recs)

                self.modify(tbmodified, recommendations=ci_recs, why=ci_whys)

        else:
            self.declare(Issue('Dry solder paste', recommendations=recs, why=whys))


class GUI(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.engine = DefectAnalysisEngine()

        master.title("DefectAnalysisExpert")
        # master.configure(bg='darkgrey')

        self.user_input = {}

        # ~~~~~~~~~~< Styling >~~~~~~~~~~
        self.texts_frames_bg_color = 'black'
        self.header_font = ('Helvetica', 14)
        self.element_font = ('Ga', 12)
        # self.element_font = (12)

        self.header_label_style = Style()
        self.header_label_style.configure('TextLabels.TLabel', font=self.header_font, background='#EEEEEF')

        self.label_style = Style()
        self.label_style.configure('TLabel', font=self.element_font, background='#EEEEEF')

        self.checkbutton_style = Style()
        self.checkbutton_style.configure('TCheckbutton', font=self.element_font, background='#EEEEEF')

        # ~~~~~~~~~~~< Left Frame >~~~~~~~~~~
        self.left_frame = Frame(master, borderwidth=0, padding=10)

        self.defect_query_label = Label(self.left_frame,
                                        text='What type of defect occurred?',
                                        style='TextLabels.TLabel',
                                        padding=[0, 0, 10, 0])
        self.defect_query_label.pack(side=TOP, anchor=NW)

        self.defect_options = Combobox(self.left_frame, state='readonly',
                                       values=DEFECTS_LIST)
        self.defect_options.pack(side=TOP, anchor=NW, fill=X)

        self.defect_options.current(0)

        self.left_frame.pack(side=LEFT, anchor=N, fill=Y)

        # ~~~~~~~~~~< Right Frame >~~~~~~~~~~
        self.right_frame = Frame(master, borderwidth=0, padding=10)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # ~~~~~~~~~~< Questions Frame >~~~~~~~~~~
        self.questions_label = Label(self.right_frame, text='Questions (Select all that apply)', padding=[0, 0, 0, 5],
                                     style='TextLabels.TLabel')
        self.questions_label.grid(row=0, column=0, sticky='w')

        self.right_frame.columnconfigure(0, minsize=540, weight=2)
        self.right_frame.columnconfigure(1, minsize=540, weight=2)
        self.right_frame.rowconfigure(1, minsize=450, weight=2)
        self.right_frame.rowconfigure(2, weight=1)

        self.questions_frame = VertScrollFrame(self.right_frame)
        self.questions_frame.canvas.configure(background='#F5F6F7', highlightthickness=0)
        self.questions_frame.grid(row=1, column=0, sticky='nsew')
        # self.questions_frame.canvas.configure(width=540, background='#F5F6F7')

        # self.header_label_style.configure('TextLabels.TLabel', font=self.header_font, background='#EEEEEF')
        # self.questions_frame.canvas.config(bg='#F0F0F0')
        # self.questions_frame.config(bg='#F0F0F0')
        # self.questions_frame.scrollable_frame.config(bg='#F0F0F0')

        # ~~~~~~~~~~< Results Frame >~~~~~~~~~~
        self.results_label = Label(self.right_frame, text='Results', padding=[5, 0], style='TextLabels.TLabel')
        self.results_label.grid(row=0, column=1, sticky='w')

        self.results_frame = VertScrollFrame(self.right_frame)
        self.results_frame.canvas.configure(background='#F5F6F7', highlightthickness=0)
        self.results_frame.grid(row=1, column=1, sticky='nsew')

        self.image_frame = HorScrollFrame(self.right_frame)
        self.image_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')

        self.submit_btn = Button(self.right_frame, text='Submit', command=self.run_engine)
        self.submit_btn.grid(row=3, column=1, sticky='e')

        self.defect_options.bind('<<ComboboxSelected>>', self.load_components)

        self.create_check_btns(self.defect_options.get())

    def run_engine(self, event=None):
        self.engine.clear_graph()

        for comp, attrs in self.user_input.items():
            for attr, bool_var in attrs.items():
                if isinstance(bool_var, BooleanVar):
                    self.user_input[comp][attr] = bool_var.get()

        pprint(self.user_input)

        self.engine.reset()
        self.engine.declare(Defect(self.defect_options.get()))

        # Declare component with attributes
        for comp, attrs in self.user_input.items():
            self.engine.declare(COMPONENT_BINDINGS[comp](**attrs))

        # watch('RULES', 'FACTS', 'ACTIVATIONS')
        self.engine.run()

        self.engine.create_graph()

        self.engine.dot.render()
        # print(self.engine.facts)

        self.load_results()
        self.load_graph_image()

    def load_graph_image(self):
        for widget in self.image_frame.scrollable_frame.winfo_children():
            widget.destroy()
        # img = PhotoImage(file='graph-output\defect-analysis-tree.gv.png')
        self.img = ImageTk.PhotoImage(Image.open('graph-output/defect-analysis-tree.gv.png'))
        # img = ImageTk.PhotoImage(Image.open('graph-output/test.png'))
        # print(self.img_widget)
        self.img_widget = Label(self.image_frame.scrollable_frame, image=self.img)

        # Label(self.image_frame.scrollable_frame, text='Hello').pack()
        # self.img_widget.pack(side=LEFT, expand=True, fill='both')
        self.img_widget.grid(sticky='nsew')

        # Label(self.right_frame, text='hi').grid(row=2, column=0, columnspan=2)
        # self.image_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')

    def load_results(self):
        results = ''
        for i, _fact in self.engine.facts.items():
            if isinstance(_fact, Issue):
                results += f"Issue: {_fact[0]}\nRecommendations:\n"
                for num, rec in enumerate(_fact['recommendations'], 1):
                    results += f"{num}. {rec}\n"
                results += '\n'

        results_output = Label(self.results_frame.scrollable_frame, text=results, background='#F5F6F7')
        results_output.pack(side=BOTTOM, fill=BOTH, expand=TRUE)

    def load_components(self, event):
        for widget in self.questions_frame.scrollable_frame.winfo_children():
            widget.destroy()

        for widget in self.results_frame.scrollable_frame.winfo_children():
            widget.destroy()

        self.engine.clear_graph()
        self.create_check_btns(self.defect_options.get())

    def create_check_btns(self, defect):
        component_queries = DEFECT_COMPONENTS[defect]

        max_width = 0
        for comp, attrs in component_queries.items():
            # print(comp, attrs)
            self.user_input[comp] = {}
            Label(self.questions_frame.scrollable_frame, text=comp).pack(side=TOP, anchor=NW)
            for attr, query in attrs.items():
                self.user_input[comp][attr] = BooleanVar()
                cb = Checkbutton(self.questions_frame.scrollable_frame, text=query,
                                 onvalue=True, offvalue=False,
                                 variable=self.user_input[comp][attr])
                # current_width = cb.winfo_reqwidth()
                # max_width = current_width if current_width > max_width else max_width
                # print(max_width)
                cb.pack(side=TOP, anchor=NW)
        # self.questions_label.grid(row=0, column=0, sticky='w')
        # self.questions_frame.canvas['width'] = max_width


root = ThemedTk(theme='arc')
gui = GUI(master=root)

root.update()
# now root.geometry() returns valid size/placement
root.minsize(root.winfo_width(), root.winfo_height())


def create_graph(*args):
    dot = Digraph()
    for arg in args:
        dot.node(arg)


gui.mainloop()

# print("FACTS:", DAEngine.facts)
# print('FACTLIST TYPE:', type(DAEngine.facts))
