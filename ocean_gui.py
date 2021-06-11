"""
Matplotlibのグラフをsg.Imagenに埋め込む

"""
import io
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import oceanlib as oclib

import PySimpleGUI as sg

def read_data(csv_file):
    """
    Open csv file using pandas
    
    """
    dfexcel = pd.read_csv(str(csv_file), skiprows=0)
    # print(dfexcel)
    xs = dfexcel.iloc[:,0]
    ys = dfexcel.iloc[:,1]
    # print(xs)
    return  xs, ys

def make_fig(xs,ys,flag=True):
    if flag == True:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(xs, ys)

    elif flag == False:
        fig = plt.figure()
        
    return fig

def draw_plot_image(fig):
    item = io.BytesIO()
    plt.savefig(item, format='png')
    plt.clf()
    plt.close('all')
    return item.getvalue()

def now_datetime(type=1):
    """
    日時を文字列で返す
    type1:通常表示 "%Y-%m-%d %H:%M:%S"
    type2:"%Y%m%d%H%M%S"
    type3:"%Y%m%d_%H%M%S"
    type4:Base_file_nameで使用する形式 "%Y%m%d%H%M"

    elae:日付のみ "%Y%m%d"

    :return:
    """
    now = datetime.datetime.now()
    if type == 1:
        now_string = now.strftime("%Y-%m-%d %H:%M:%S")
    elif type == 2:
        now_string = now.strftime("%Y%m%d%H%M%S")
    elif type == 3:
        now_string = now.strftime("%Y%m%d_%H%M%S")
    elif type == 4:
        now_string = now.strftime("%Y%m%d%H%M")
    elif type == 5:
        now_string = now.strftime("%m%d_%H:%M:%S")
    elif type == 6:
        now_string = now.strftime("%Y%m%d")    
    else:
        now_string = now

    return  now_string

sg.theme('Light Blue 2')


layout = [[sg.Text('Ocean UV-VIS Measurement')],
            [sg.Text("refrence CSV file"), sg.InputText(key="-file-"), sg.FileBrowse(file_types=(("CSV Files", "*.csv"),))],
            [sg.Submit(key='-read-')],
            [sg.Text("Integration Time [ms]"),sg.InputText('10',size=(4,4),key="-it-"),
            sg.Text("Average max:5000"),sg.InputText('10',size=(5,4),key="-ave-"),
            sg.Text("Save Name"),sg.InputText('data_',size=(10,4),key="-saveN-")],
            [sg.Button('measure', key='-measure-'), sg.Button('ref set', key='-refset-'), sg.Button('calc', key='-calc-')],
            [sg.Button('save',key='-save-')],
            [sg.Cancel()],
            [sg.Output(size=(80, 4))],
            [sg.Image(filename='', key='-image-')]  
          ]

window = sg.Window('Ocean Measurment', layout, location=(100, 100), finalize=True)

oc_data = oclib.OceanMea()

while True:
    event, values = window.read()

    if event in (None, 'Cancel'):
        break
    
    elif event == '-read-':
        read_d_wave, read_reflec_ints = read_data(str(values['-file-']))
        
        d_wave = read_d_wave[40:].copy()
        ref_d_ints = read_reflec_ints[40:].copy()
       
        fig_ = make_fig(d_wave, reflec_ints)
        fig_bytes = draw_plot_image(fig_)
        window['-image-'].update(data=fig_bytes)

    elif event == '-measure-':
        # 0.1 seconds = 100000, 0.01s  =10000, 0.001s = 1000
        integtime = int(values['-it-'])*1000
        ave = int(values['-ave-'])
        oc_data.intgtime = integtime
        oc_data.ave = ave
        oc_data.set_integtime()
        
        print(f'Start: {now_datetime(type=5)}')
        dd_wave, dd_ints = oc_data.get_ave_data()
        
        d_wave = dd_wave[40:].copy()
        d_ints = dd_ints[40:].copy()
        fig_ = make_fig(d_wave, d_ints)
        fig_bytes = draw_plot_image(fig_)
        window['-image-'].update(data=fig_bytes)
        
        print(f'Finished: {now_datetime(type=5)}')

    elif event == '-save-':  
        saveName = f"{values['-saveN-']}_{now_datetime(type=3)}.csv"
        oc_data.save_csv(f'{saveName}')
        print(f'Save: {saveName}')
    
    elif event == '-refset-':
        ref_d_ints = d_ints.copy()
        print('Reference Set')

    elif event =='-calc-':
        reflec_ints = d_ints/ref_d_ints
        fig_ = make_fig(d_wave, reflec_ints)
        fig_bytes = draw_plot_image(fig_)
        window['-image-'].update(data=fig_bytes)
        print('Reflectance') 

    elif event == '-clear-':
        fig_ = make_fig(d_wave, d_ints, flag=False)
        fig_bytes = draw_plot_image(fig_)
        window['-image-'].update(data=fig_bytes)
        # print(values)      

window.close()

