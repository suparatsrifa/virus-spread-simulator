from abc import ABC, abstractmethod
from random import randint

from lib.deseases import SARSCoV2, SeasonalFluVirus, Cholera


class Drug(ABC):
    def apply(self, person):
        # somehow reduce person's symptoms
        pass


class AntipyreticDrug(Drug):
    pass


class Aspirin(AntipyreticDrug):
    """
        A cheaper version of the fever/pain killer.
    """

    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.5

    def apply(self, person):
        person.temperature = max(36.6, person.temperature - self.dose * self.efficiency)


class Ibuprofen(AntipyreticDrug):
    """A more efficient version of the fever/pain killer."""

    def __init__(self, dose):
        self.dose = dose

    def apply(self, person):
        person.temperature = 36.6


class RehydrationDrug(Drug):
    pass


class Glucose(RehydrationDrug):
    """A cheaper version of the rehydration drug."""

    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.1

    def apply(self, person):
        person.water = min(person.water + self.dose * self.efficiency,
                           0.6 * person.weight)


class Rehydron(RehydrationDrug):
    """A more efficient version of the rehydration drug."""

    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 1.0

    def apply(self, person):
        person._water = 0.6 * person.weight


class AntivirusDrug(Drug):
    pass


class Placebo(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose

    def apply(self, person):
        pass


class AntivirusSeasonalFlu(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 1.0

    def apply(self, person):
        if isinstance(person.virus, SeasonalFluVirus):
            person.virus.strength -= self.dose * self.efficiency

        elif isinstance(person.virus, SARSCoV2):
            person.virus.strength -= self.dose * self.efficiency / 10.0


class AntivirusSARSCoV2(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.1

    def apply(self, person):
        if isinstance(person.virus, SARSCoV2):
            person.virus.strength -= self.dose * self.efficiency


class AntivirusCholera(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.1

    def apply(self, person):
        if isinstance(person.virus, Cholera):
            person.virus.strength -= self.dose * self.efficiency


class DrugRepository(ABC):
    def __init__(self):
        self.treatment = []

    @abstractmethod
    def get_antifever(self, dose) -> Drug: pass

    @abstractmethod
    def get_rehydration(self, dose) -> Drug: pass

    @abstractmethod
    def get_seasonal_antivirus(self, dose) -> Drug: pass

    @abstractmethod
    def get_sars_antivirus(self, dose) -> Drug: pass

    @abstractmethod
    def get_cholera_antivirus(self, dose) -> Drug: pass

    def get_treatment(self):
        return self.treatment


class CheapDrugRepository(DrugRepository):
    def get_antifever(self, dose) -> Drug:
        return Aspirin(dose)

    def get_rehydration(self, dose) -> Drug:
        return Glucose(dose)

    def get_seasonal_antivirus(self, dose) -> Drug:
        return Placebo(dose)

    def get_sars_antivirus(self, dose) -> Drug:
        return Placebo(dose)

    def get_cholera_antivirus(self, dose) -> Drug:
        return Placebo(dose)


class ExpensiveDrugRepository(DrugRepository):
    def get_antifever(self, dose) -> Drug:
        return Ibuprofen(dose)

    def get_rehydration(self, dose) -> Drug:
        return Rehydron(dose)

    def get_seasonal_antivirus(self, dose) -> Drug:
        return AntivirusSeasonalFlu(dose)

    def get_sars_antivirus(self, dose) -> Drug:
        return AntivirusSARSCoV2(dose)

    def get_cholera_antivirus(self, dose) -> Drug:
        return AntivirusCholera(dose)

