from abc import ABC, abstractmethod
from random import expovariate
from enum import Enum
from lib.logger import Logger

class Person:
    pass


class Infectable(ABC):
    def __init__(self, strength=1.0, contag=1.0):
        # contag is for contagiousness so we have less typos
        self.strength = strength
        self.contag = contag
        Logger().log('Infectable', 'New virus with stregth='+str(round(self.strength, 2)))

    @abstractmethod
    def cause_symptoms(self, person: Person):
        pass


class SeasonalFluVirus(Infectable):
    def cause_symptoms(self, person):
        person.temperature += 0.25

    @staticmethod
    def get_type():
        return InfectableType.SeasonalFlu


class SARSCoV2(Infectable):
    def cause_symptoms(self, person):
        person.temperature += 0.5

    @staticmethod
    def get_type():
        return InfectableType.SARSCoV2


class Cholera(Infectable):
    def cause_symptoms(self, person):
        person.water -= 1.0

    @staticmethod
    def get_type():
        return InfectableType.Cholera


class InfectableType(Enum):
    SeasonalFlu = 1
    SARSCoV2 = 2
    Cholera = 3


def get_infectable(infectable_type: InfectableType):
    if InfectableType.SeasonalFlu == infectable_type:
        return SeasonalFluVirus(strength=expovariate(10.0), contag=expovariate(10.0))

    elif InfectableType.SARSCoV2 == infectable_type:
        return SARSCoV2(strength=expovariate(0.42), contag=expovariate(0.42))

    elif InfectableType.Cholera == infectable_type:
        return Cholera(strength=expovariate(2.0), contag=expovariate(2.0))

    else:
        raise ValueError()
