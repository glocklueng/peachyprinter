from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanelItem, TabbedPanel
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.core.window import Window


class AlignmentPanel(TabbedPanelItem):
    def __init__(self, **kwargs):
        super(AlignmentPanel, self).__init__(**kwargs)


class OrientationPanel(TabbedPanelItem):
    orient_rotated = StringProperty("False")
    orient_xflip = StringProperty("False")
    orient_yflip = StringProperty("False")

    def __init__(self, **kwargs):
        super(OrientationPanel, self).__init__(**kwargs)

    def update_orientation(self, rotate, xflip, yflip):
        self.orient_rotated = "True" if rotate else "False"
        self.orient_xflip = "True" if xflip else "False"
        self.orient_yflip = "True" if yflip else "False"


class CalibrationPanel(TabbedPanelItem):
    calibration_height = NumericProperty(0)
    calibration_point = ListProperty([0, 0])
    example_point = ListProperty([0, 0])
    example_dot = ListProperty([0, 0])
    printer_point = ListProperty([0.0, 0.0])
    center_point = ListProperty([0.0, 0.0])

    def __init__(self, **kwargs):
        super(CalibrationPanel, self).__init__(**kwargs)
        self.is_accurate = False
        self.bind(example_point=self.on_example_point)

    def on_upper_left(self):
        self.example_point = [0, 1]

    def on_upper_right(self):
        self.example_point = [1, 1]

    def on_lower_right(self):
        self.example_point = [1, 0]

    def on_lower_left(self):
        self.example_point = [0, 0]

    def on_example_point(self, *args):
        image_size = min(self.ids.example_grid.size)
        pos_x = self.ids.example_grid.x + (self.ids.example_grid.width - image_size) / 2
        pos_y = self.ids.example_grid.y + (self.ids.example_grid.height - image_size) / 2
        self.example_dot = [
            pos_x - 4 + (self.example_point[0] * image_size),
            pos_y - 4 + (self.example_point[1] * image_size),
            ]

    def set_printer_pos_from_screen(self, x, y):
        if self.is_accurate:
            peachyx = self.center_point[0] + (x * 0.1)
            peachyy = self.center_point[1] + (y * 0.1)
            peachyx = max(-1.0, min(1.0, peachyx))
            peachyy = max(-1.0, min(1.0, peachyy))
        else:
            peachyx = x
            peachyy = y

        self.printer_point = [peachyx, peachyy]
        Logger.info('%s, %s' % (peachyx, peachyy))

    def super_accurate_mode(self, instance):
        if instance.state == 'normal':
            self.is_accurate = False
            self.center_point = [0.0, 0.0]
            self.set_screen_point_from_printer()
        else:
            self.is_accurate = True
            self.center_point = self.printer_point
            self.calibration_point = self.ids.top_calibration_grid.center

    def set_screen_point_from_printer(self):
        (grid_width, grid_height) = self.ids.top_calibration_grid.size
        rel_x_percent = (self.printer_point[0] + 1.0) / 2.0
        rel_y_percent = (self.printer_point[1] + 1.0) / 2.0
        rel_x = rel_x_percent * grid_width
        rel_y = rel_y_percent * grid_height
        (x, y) = self.ids.top_calibration_grid.pos
        self.calibration_point = [x + rel_x, y + rel_y]

    def on_motion(self, etype, motionevent, mouse_pos):
        grid_extents = min(self.ids.top_calibration_grid.size) / 2.0
        grid_center = self.ids.top_calibration_grid.center
        rel_x = mouse_pos.pos[0] - grid_center[0]
        rel_y = mouse_pos.pos[1] - grid_center[1]
        if abs(rel_x) <= grid_extents and abs(rel_y) <= grid_extents:
            self.set_printer_pos_from_screen(rel_x / grid_extents, rel_y / grid_extents)
            self.calibration_point = mouse_pos.pos

    def on_enter(self):
        Window.bind(on_motion=self.on_motion)

    def on_leave(self):
        Window.unbind(on_motion=self.on_motion)


class TestPatternPanel(TabbedPanelItem):
    def __init__(self, **kwargs):
        super(TestPatternPanel, self).__init__(**kwargs)
        self.loaded = False

    def on_enter(self):
        if not self.loaded:
            Logger.info(':IDS: %s' % str( self.ids) )
            items = ["Test #%s" % str(i + 1) for i in range(0, 12)]
            for item in items:
                self.ids.patterns.add_widget(ToggleButton(group='test_patterns', text=item))
            self.loaded = True

Builder.load_file('ui/calibrate_ui.kv')


class CalibrateUI(Screen):

    def __init__(self, **kwargs):
        super(CalibrateUI, self).__init__(**kwargs)

    def on_pre_enter(self):
        pass

    def on_pre_leave(self):
        pass
