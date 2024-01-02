import dearpygui.dearpygui as dpg
from diagramm_lib import Diagramm
import pandas as pd
import json
import sys
from glob import glob
from dpgfiledialog import dpgDirFileDialog

# if len(sys.argv) >= 2:
#     xls_path = sys.argv[1]
# else:
#     xls_path = './с714.xls'
# xls_data = pd.read_excel(xls_path, usecols=[0], names=['exp_code'])
diagramm = Diagramm()
exp_data = None
# diagramm.load_from_txt('./diagr.txt')

dpg.create_context()
dpg.create_viewport(height=820)
dpg.setup_dearpygui()

# with dpg.theme() as choosen_button:
#     with dpg.theme_component(dpg.mvButton):
#         dpg.add_theme_color(dpg.mvThemeCol_Button, (91, 164, 169))

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, y=6)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, y=10)

dpg.bind_theme(global_theme)


# def choose_xls(sender, app_data, user_data):
#     dpg.bind_item_theme(sender, choosen_button)

with dpg.font_registry():
    with dpg.font("c:/Windows/Fonts/arial.ttf", 16, default_font=True) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.bind_font(default_font)
def choose_sheet(sender, app_data, user_data):
    global diagramm
    global exp_data
    if exp_data is None:
        return
    diagramm.load_from_xls(xls_path, app_data)
    dpg.set_value(corrected_diag, [[],[]])
    dpg.set_value(plastic_diag_eng, [[],[]])
    dpg.set_value(plastic_diag_true, [[],[]])
    dpg.set_value(
        diag,
        [
            list(diagramm._e),
            list(diagramm._s),
            ]
    )
    dpg.fit_axis_data(x1)
    dpg.fit_axis_data(y1)


def apply_markers(seder, app_data, user_data):
    ep1_value = dpg.get_value(ep1)
    ep2_value = dpg.get_value(ep2)
    if ep1_value == ep2_value:
        return
    if ep1_value > ep2_value:
        ep1_value, ep2_value = ep2_value, ep1_value
        dpg.set_value(ep1, ep1_value)
        dpg.set_value(ep2, ep2_value)
    diagramm.ep1 = ep1_value
    diagramm.ep2 = ep2_value
    dpg.set_value(
        plastic_diag_eng,
        [
            list(diagramm.ep_eng),
            list(diagramm.sp_eng),
        ]
    )
    dpg.set_value(
        plastic_diag_true,
        [
            list(diagramm.ep_true),
            list(diagramm.sp_true),
        ]
    )
    dpg.fit_axis_data(x2)
    dpg.fit_axis_data(y2)

def update_E(sender, app_data, user_data):
    if len(diagramm._e) == 0:
        return
    smax = diagramm._s.max()
    emax = smax/app_data
    dpg.set_value(
        e_line,
        [[0, emax], [0, smax]]
    )

def correct_elastic(sender, app_data, user_data):
    diagramm._E_multiplier = app_data
    dpg.set_value(
        corrected_diag,
        [
            list(diagramm.e),
            list(diagramm._s),
        ]
    )
    
def shift_curves(sendedr, app_data, user_data):
    diagramm._delta_e = app_data
    dpg.set_value(
        corrected_diag,
        [
            list(diagramm.e),
            list(diagramm._s),
        ]
    )
    dpg.fit_axis_data(x1)


def stress_level_callback(sender, app_data, user_data):
    sl = dpg.get_value(stress_level_line)
    dpg.set_value(stress_level_text, f'{sl: g}')


def save_callback(sender, app_data, user_data):
    if not diagramm.exp_code:
        return
    json.dump(
        diagramm.as_dict,
        open(f'{diagramm.exp_code}.json', 'w')
    )


def update_group_plot(sender, app_data, user_data):
    dpg.delete_item(yg1, children_only=True)
    dpg.delete_item(yg2, children_only=True)
    dpg.delete_item(yg3, children_only=True)
    for f in glob('*.json'):
        data = json.load(open(f, 'r'))
        dgr = Diagramm(t=data['_t'], e=data['_e'], s=data['_s'], de=data['_de'])
        dgr._E_multiplier = data['_E_multiplier']
        dgr._delta_e = data['_delta_e']
        dgr.ep1 = data['_ep1']
        dgr.ep2 = data['_ep2']
        dgr.exp_code = data['exp_code']
        dpg.add_line_series(dgr.e.tolist(), dgr.s.tolist(), label=dgr.exp_code, parent=yg1)
        dpg.add_line_series(dgr.ep_eng.tolist(), dgr.sp_eng.tolist(), label=dgr.exp_code, parent=yg2)
        dpg.add_line_series(dgr.ep_true.tolist(), dgr.sp_true.tolist(), label=dgr.exp_code, parent=yg3)
    dpg.fit_axis_data(xg1)
    dpg.fit_axis_data(yg1)
    dpg.fit_axis_data(xg2)
    dpg.fit_axis_data(yg2)
    dpg.fit_axis_data(xg3)
    dpg.fit_axis_data(yg3)


def choose_xls_file(sender, app_data, user_data):
    fd = dpgDirFileDialog()
    fd.show()

with dpg.window(label="Correct module", width=800, height=700, tag='main'):
    with dpg.menu_bar():
        with dpg.menu(label='Инструменты'):
            dpg.add_menu_item(label='Выбрать xlsx', callback=choose_xls_file)
            dpg.add_menu_item(label='Установить рабочую директорию')
            dpg.add_separator()
            dpg.add_menu_item(label='Выход', callback=dpg.stop_dearpygui)
        dpg.add_spacer(width=100)
        dpg.add_text('Код испытания: ')
        xls_sheets_cb = dpg.add_combo(
            items=[],#xls_data.exp_code.to_list(),
            callback=choose_sheet,
            width=300,
            )
        dpg.add_spacer(width=100)
        dpg.add_text('Уровень напряжения: ')
        stress_level_text = dpg.add_text('')

    with dpg.group(horizontal=True):
        dpg.add_slider_float(vertical=True, width=10, format='', height=300, min_value=-100, max_value=100)
        dpg.add_spacer(width=5)
        with dpg.subplots(1, 2, width=-1):
            with dpg.plot():
                x1 = dpg.add_plot_axis(dpg.mvXAxis, label='strain')
                y1 = dpg.add_plot_axis(dpg.mvYAxis, label='stress, MPa')
                diag = dpg.add_line_series(
                    x=[],
                    y=[],
                    parent=y1
                    )
                corrected_diag = dpg.add_line_series(
                    x=[],
                    y=[],
                    parent=y1
                    )
                e_line = dpg.add_line_series(
                    [],
                    [],
                    parent=y1
                )
                ep1 = dpg.add_drag_line(label='ep1', color=(255, 0, 0), show_label=False)
                ep2 = dpg.add_drag_line(label='ep2', color=(0, 255, 0), show_label=False)
                stress_level_line = dpg.add_drag_line(
                    label='stress level', color=(255, 255, 255),
                    vertical=False, default_value=200,
                    show_label=False, callback=stress_level_callback
                    )
            with dpg.plot():
                x2 = dpg.add_plot_axis(dpg.mvXAxis, label='strain')
                y2 = dpg.add_plot_axis(dpg.mvYAxis, label='stress, MPa')
                plastic_diag_eng = dpg.add_line_series([], [], parent=y2, label='eng')
                plastic_diag_true = dpg.add_line_series([], [], parent=y2, label='true')
                dpg.add_plot_legend()
    with dpg.group(horizontal=True, height=30):
        dpg.add_button(label='Apply markers', width=100, height=30, callback=apply_markers)
    dpg.add_drag_float(
        label='E_etalon',
        min_value=10,
        max_value=200000,
        default_value=100000,
        speed=100,
        callback=update_E,
        clamped=True,
        )

    dpg.add_drag_float(
        label='correct_E',
        min_value=0.001,
        max_value=1,
        default_value=1,
        speed=0.01,
        callback=correct_elastic,
        clamped=True,
        )
    dpg.add_drag_float(
        label='shift',
        min_value=-0.05,
        max_value=0.05,
        default_value=0,
        speed=0.0001,
        callback=shift_curves,
        clamped=True,
    )
    with dpg.group(horizontal=True):
        dpg.add_button(label='Save', width=60, height=30, callback=save_callback)
        dpg.add_button(label='Update', width=60, height=30, callback=update_group_plot)
    with dpg.subplots(1, 3, width=-1):
        with dpg.plot():
            xg1 = dpg.add_plot_axis(dpg.mvXAxis, label='strain')
            yg1 = dpg.add_plot_axis(dpg.mvYAxis, label='stress')
            dpg.add_plot_legend()
        with dpg.plot():
            xg2 = dpg.add_plot_axis(dpg.mvXAxis, label='ep eng')
            yg2 = dpg.add_plot_axis(dpg.mvYAxis, label='stress eng')
            dpg.add_plot_legend()
        with dpg.plot():
            xg3 = dpg.add_plot_axis(dpg.mvXAxis, label='ep true')
            yg3 = dpg.add_plot_axis(dpg.mvYAxis, label='stress true')
            dpg.add_plot_legend()


dpg.show_style_editor()

dpg.show_viewport()
dpg.set_primary_window('main', True)
dpg.start_dearpygui()
dpg.destroy_context()