import numpy as np
import os
from enum import Enum
import pandas as pd
from copy import deepcopy
import json

class ExperimentType(str, Enum):
    COMPRESSION = 'c'
    TENSION = 't'


class Diagramm:
    def __init__(self, t=[], e=[], s=[], de=[], etype=ExperimentType.COMPRESSION,
                 T=20):
        self._t: np.ndarray = np.array(t, dtype=np.float32)
        self._e: np.ndarray = np.array(e, dtype=np.float32)
        self._s: np.ndarray = np.array(s, dtype=np.float32)
        self._de: np.ndarray = np.array(de, dtype=np.float32)
        self.etype = etype
        self.ds: float = 0
        self.T = T
        self.set_initial_values()
    
    def set_initial_values(self):
        self._ep1: float = -1
        self._ep2: float = -1
        self._ep1_idx: int = -1
        self._ep2_idx: int = -1
        self._E_multiplier: float = 1.0
        self._delta_e: float = 0.0
        self.exp_code = ''

    def load_from_txt(self, filepath: str):
        if not os.path.exists(filepath):
            print(f'Не найден файл {filepath}')
            return
        self.set_initial_values()
        self._t, self._e, self._s, self._de = np.genfromtxt(
            filepath,
            skip_header=1,
            unpack=True,
            usecols=[0, 1, 2, 3],
            )

    def load_from_xls(self, xls_path: str, sheet_name: str):
        if not os.path.exists(xls_path):
            print(f'Не найден файл {xls_path}')
            return
        self.set_initial_values()
        data = pd.read_excel(
            xls_path,
            sheet_name=sheet_name,
            usecols=[0, 5, 6, 7],
            names=['t', 'e', 's', 'de']
        )
        self._t = data.t.to_numpy()
        self._e = data.e.to_numpy()
        self._s = data.s.to_numpy()
        self._de = data.de.to_numpy()
        self.exp_code = sheet_name
        self.etype = sheet_name[0]

    @property
    def ep1(self) -> float:
        return self._ep1

    @property
    def ep2(self) -> float:
        return self._ep2

    @property
    def ep1_idx(self) -> float:
        return self._ep1_idx
    
    @property
    def ep2_idx(self) -> float:
        return self._ep2_idx
    
    @ep1.setter
    def ep1(self, value: float):
        self._ep1 = value
        for i, e in enumerate(self._e):
            if e >= self._ep1:
                break
        else:
            self._ep1_idx = -1
            return
        self._ep1_idx = i

    @ep2.setter
    def ep2(self, value: float):
        self._ep2 = value
        for i, e in enumerate(self._e):
            if e >= self._ep2:
                break
        else:
            self._ep2_idx = -1
            return
        self._ep2_idx = i
    
    @property
    def e(self) -> np.ndarray:
        res = np.zeros(len(self._e))
        for i in range(len(self._e)):
            if i <= self._ep1_idx:
                res[i] = self._e[i]*self._E_multiplier
            else:
                res[i] = self._e[i]-self._e[self._ep1_idx]*(1-self._E_multiplier)
        return res + self._delta_e
    
    @property
    def s(self) -> np.ndarray:
        return self._s + self.ds
    
    @property
    def ep_eng(self) -> np.ndarray:
        if self.ep1_idx == -1:
            return np.array([])
        if self.ep2_idx == -1:
            return np.array([])
        rez = np.array(self._e[self.ep1_idx:self.ep2_idx])
        rez -= rez[0]
        return rez

    @property
    def sp_eng(self) -> np.ndarray:
        if self.ep1_idx == -1:
            return np.array([])
        if self.ep2_idx == -1:
            return np.array([])
        return self.s[self.ep1_idx:self.ep2_idx]

    @property
    def dep_eng(self) -> np.ndarray:
        if self.ep1_idx == -1:
            return np.array([])
        if self.ep2_idx == -1:
            return np.array([])
        return self.s[self.ep1_idx:self.ep2_idx]

    @property
    def ep_true(self) -> np.ndarray:
        sign = -1 if self.etype == ExperimentType.COMPRESSION else 1
        return sign*np.log(1+sign*self.ep_eng)

    @property
    def sp_true(self) -> np.ndarray:
        sign = -1 if self.etype == ExperimentType.COMPRESSION else 1
        return self.sp_eng*(1+sign*self.ep_eng)
    
    @property
    def dep_true(self) -> np.ndarray:
        sign = -1 if self.etype == ExperimentType.COMPRESSION else 1
        return self.dep_eng/(1+sign*self.ep_eng)
    
    @property
    def as_dict(self) -> dict:
        rez = deepcopy(self.__dict__)
        rez['_t'] = list(self._t)
        rez['_e'] = list(self._e)
        rez['_s'] = list(self._s)
        rez['_de'] = list(self._de)
        return rez

    def load_from_json(self, json_path: str):
        if not os.path.exists(json_path):
            return
        data = json.load(open(json_path, 'r'))
        self._t = np.array(data['_t'])
        self._e = np.array(data['_e'])
        self._s = np.array(data['_s'])
        self._de = np.array(data['_de'])
        self._E_multiplier = data['_E_multiplier']
        self._delta_e = data['_delta_e']
        self.ep1 = data['_ep1']
        self.ep2 = data['_ep2']
        self.exp_code = data['exp_code']
        self.ds = data.get('ds', 0)
        self.T = data.get('T', 20)

    @property
    def mean_de_eng(self) -> float:
        return self.dep_eng.mean()

    @property
    def mean_de_true(self) -> float:
        return self.dep_true.mean()
        
    
if __name__=='__main__':
    # import matplotlib.pylab as plt
    d = Diagramm()
    d.load_from_json('../example/c714-01.json')
    print(d._ep1_idx)
    print(d._ep2_idx)
    print(d.mean_de_eng)
    print(d.mean_de_true)
    # plt.plot(d._e, d._s)
    # plt.axvline(d._ep1, color='k')
    # plt.axvline(d._ep2, color='k')
    # d._E_multiplier = 0.5
    # plt.plot(d.e, d._s)
    # d._E_multiplier = 0.3
    # plt.plot(d.e, d._s)
    # plt.show()