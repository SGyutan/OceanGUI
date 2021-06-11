import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from seabreeze.spectrometers import Spectrometer

class OceanMea():
    def __init__(self,intgtime=1000,ave=10):
        self.intgtime = intgtime
        self.ave = ave
        self.spec = Spectrometer.from_first_available()
        # 0.1 seconds = 100000, 0.01s  =10000, 0.001s = 1000
        self.set_integtime()
        
    
    def get_ref(self):
        self.ref_wave, self.ref_ave_ints = self.get_ave_data()  
    
    def set_integtime(self):
        self.spec.integration_time_micros(self.intgtime) # 0.1 seconds = 100000, 0.01
    
    @classmethod
    def calc_reflectance(cls,wave,ints,ref_ints):
        reflec_ints = ints/ref_ints
        plt.plot(wave,reflec_ints)
        # plt.show(block=False)
        plt.show()
        return reflec_ints    
        
    def get_data(self):
        self.wave = self.spec.wavelengths()
        self.ints= self.spec.intensities()
        return self.wave, self.ints
        
    def get_ave_data(self):
        
        self.wave = self.spec.wavelengths()
        self.ave_ints = np.zeros_like(self.wave )
        
        for i in range(self.ave):
            
            self.ints= self.spec.intensities()
            # print(self.ints[20])
            self.ave_ints =  (self.ave_ints + self.ints)/(i+1)

            
        return  self.wave, self.ave_ints
    
    def df_return(self):
        self.df_data =pd.DataFrame({'wave':self.wave,
                                    'intensity':self.ave_ints})
        return self.df_data
        
    def save_csv(self,filename):
        """
        filename:
        example  'data/dst/to_csv_out.csv'
        """
        self.df_ = self.df_return()
        self.df_.to_csv(filename,index=False)
    
    def get_ref_file(self,filename):
        self.df_ref = pd.read_csv(filename)
        self.ref_wave = self.df_ref['wave']
        self.ref_ave_ints = self.df_ref['intensity']
        return self.df_ref
    
    def save_raw_to_csv(self, base_file_name, file_option, ref_file, SAVE_DATA_HOLDER=None):
        """
        Spectra data save
        metadata save
        reflectance
        :param SAVE_DATA_HOLDER:
        :return:
        """
        
        if SAVE_DATA_HOLDER == None:
            SAVE_DATA_HOLDER = './data'

        file_data_name = "{}_uvu_{}.csv".format(base_file_name, file_option)

        save_data_path = Path(SAVE_DATA_HOLDER, file_data_name)
        
 
        df_data = self.save_csv(save_data_path)

        meta_device = {'device': {'modul_name': 'ocean optics usb2000+'}}

        meta_condition = {'conditions': {'integration time': str(self.intgtime) + 'ms',
                                         'average': str(self.ave),
                                         'referanec': None}}

        meta_csv = {'csv_data': {'column': ['wavelength', 'absolute_count'],
                                 'unit': ['nm', 'uW/cm^2/nm']}}
        meta_option = meta_device.copy()
        meta_option.update(meta_condition)
        meta_option.update(meta_csv)

        # meta_file_name = "{}_uvu_meta.txt".format(base_file_name)
        # meta_file_path = Path(SAVE_DATA_HOLDER + meta_file_name)

        # with meta_file_path.open( 'w') as fmeta:
        #     fmeta.write(meta_condition)

        return file_data_name, meta_option
        
    def save_cal_to_csv(self, base_file_name, file_option, ref_file, SAVE_DATA_HOLDER=None):
        """
        Spectra data save
        metadata save
        reflectance
        :param SAVE_DATA_HOLDER:
        :return:
        """
        
        if SAVE_DATA_HOLDER == None:
            SAVE_DATA_HOLDER = './data'

        file_data_name = "{}_Ruvu_{}.csv".format(base_file_name, file_option)

        save_data_path = Path(SAVE_DATA_HOLDER, file_data_name)
        #
        df_ref = self.get_ref_file(ref_file)
        df_data = self.df_return()

        reflectance = df_data[1] / df_ref[1]
        
        df_out = pd.DataFrame({'wave': df_ref[0],'absolute_count': df_data[1],'reflectance': reflectance})
        df_out.to_csv(save_data_path,index=False)

        meta_device = {'device': {'modul_name': 'ocean optics usb2000+'}}

        meta_condition = {'conditions': {'integration time': str(self.intgtime) + 'ms',
                                         'average': str(self.ave),
                                         'referanec': ref_file}}

        meta_csv = {'csv_data': {'column': ['wavelength', 'absolute_count', 'reflectance'],
                                 'unit': ['nm', 'uW/cm^2/nm', 'au']}}
        meta_option = meta_device.copy()
        meta_option.update(meta_condition)
        meta_option.update(meta_csv)

        # meta_file_name = "{}_uvu_meta.txt".format(base_file_name)
        # meta_file_path = Path(SAVE_DATA_HOLDER + meta_file_name)

        # with meta_file_path.open( 'w') as fmeta:
        #     fmeta.write(meta_condition)

        return file_data_name, meta_option
        

if __name__ == '__main__':
    import time
    ref=OceanMea()
    rwave,rints= ref.get_ave_data()
    ref.save_csv('ref.csv')
    
    print('-----')
    time.sleep(5)
    print('--remain 3--')
    time.sleep(3)
    _,ints =ref.get_ave_data()
    
    ref.calc_reflectance(rwave,ints,rints)

    
    
    