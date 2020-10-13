from abc import ABC, abstractmethod
from lib.health import DepartmentOfHealth, GlobalContext
from lib.observer import Observable, Events
from lib.logger import Logger
from lib.deseases import get_infectable

class Person:
    pass


def dist(pos1, pos2):
    min_j, max_j, min_i, max_i = GlobalContext().canvas
    dx = ((pos1[0]-pos2[0]) / (max_j-min_j)) ** 2
    dy = ((pos1[1]-pos2[1]) / (max_i-min_i)) ** 2
    return (dx + dy) ** 0.5


class State(ABC):
    def __init__(self, person):
        self.person = person

    @abstractmethod
    def day_actions(self): pass

    @abstractmethod
    def night_actions(self): pass

    @abstractmethod
    def interact(self, other): pass

    @abstractmethod
    def get_infected(self, virus): pass


class Healthy(State):
    def day_actions(self):
        self.person._day_actions()

    def night_actions(self):
        self.person.position = self.person.home_position

    def interact(self, other: Person): pass

    def get_infected(self, virus):
        if virus.get_type() not in self.person.antibody_types:
            Logger().log('Healthy', self.person.antibody_types)
            self.person.virus = get_infectable(virus.get_type())
            self.person.set_state(AsymptomaticSick(self.person))


class AsymptomaticSick(State):
    DAYS_SICK_TO_FEEL_BAD = 4

    def __init__(self, person):
        super().__init__(person)
        self.days_sick = 0

    def day_actions(self):
        self.person._day_actions()

        if self.person.is_life_incompatible_condition():
            self.person.set_state(Dead(self.person))

    def night_actions(self):
        self.person.position = self.person.home_position
        if self.days_sick == AsymptomaticSick.DAYS_SICK_TO_FEEL_BAD:
            self.person.set_state(SymptomaticSick(self.person))
        self.days_sick += 1

    def interact(self, other):
        if GlobalContext().policy.try_infect():
            other.get_infected(self.person.virus)

    def get_infected(self, virus): pass


class SymptomaticSick(State):
    def __init__(self, person):
        super().__init__(person)
        self.person.notify_observer(Events.EV_INFECTION, person.virus.get_type())

    def day_actions(self):
        self.person.progress_disease()

        if self.person.is_life_threatening_condition() and (self.person.hospital is None):
            health_dept = DepartmentOfHealth(None)
            self.person.hospital = health_dept.hospitalize(self.person)

        if self.person.is_life_incompatible_condition():
            self.person.set_state(Dead(self.person))

    def night_actions(self):
        # try to fight the virus
        self.person.fightvirus()
        if self.person.virus.strength <= 0:
            self.person.set_state(Healthy(self.person))
            self.person.antibody_types.add(self.person.virus.get_type())

            self.person.notify_observer(Events.EV_RECOVERY, self.person.virus.get_type())
            self.person.notify_observer(Events.EV_ANTIBODY, self.person.virus.get_type())
            self.person.virus = None

            if self.person.hospital:
                self.person.hospital.release_patient(self.person)
                self.person.hospital = None
                self.person.notify_observer(Events.EV_HOSP_OUT)

    def interact(self, other):
        pass

    def get_infected(self, virus):
        pass


class Dead(State):
    def __init__(self, person):
        super().__init__(person)
        self.person.notify_observer(Events.EV_DEATH, self.person.virus.get_type())

        if self.person.hospital:
            self.person.hospital.release_patient(self.person)
            self.person.hospital = None
            self.person.notify_observer(Events.EV_HOSP_OUT)

    def day_actions(self): pass

    def night_actions(self): pass

    def interact(self, other): pass

    def get_infected(self, virus): pass


class Person(Observable):
    MAX_TEMPERATURE_TO_SURVIVE = 44.0
    LOWEST_WATER_PCT_TO_SURVIVE = 0.4

    LIFE_THREATENING_TEMPERATURE = 40.0
    LIFE_THREATENING_WATER_PCT = 0.5

    def __init__(self, home_position=(0, 0), age=30, weight=70):
        super().__init__()
        self.virus = None
        self.antibody_types = set()
        self.temperature = 36.6
        self.weight = weight
        self.water = 0.6 * self.weight
        self.age = age
        self.home_position = home_position
        self.position = home_position
        self.state = Healthy(self)
        self.hospital = None

    def attrs(self):
        return {
            'virus': self.virus,
            'antibodies': [ab.name for ab in self.antibody_types],
            'temp': round(self.temperature, 1),
            'weight': round(self.weight, 1),
            'water': round(self.water, 1),
            'age': self.age,
            'home': self.home_position,
            'pos': self.position,
            'state': self.state.__class__.__name__
        }

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join(['{}={}'.format(k, v) for k, v in self.attrs().items()]))

    def day_actions(self):
        self.state.day_actions()

    def _day_actions(self):
        pass

    def night_actions(self):
        self.state.night_actions()

    def interact(self, other):
        self.state.interact(other)

    def get_infected(self, virus):
        self.state.get_infected(virus)

    def is_close_to(self, other):
        return dist(self.position, other.position) <= 0.01

    def fightvirus(self):
        if self.virus:
            self.virus.strength -= (3.0 / self.age)
            # Logger().log('Person', 'New virus strength = '+str(self.virus.strength))

    def progress_disease(self):
        if self.virus:
            self.virus.cause_symptoms(self)

    def set_state(self, state):
        self.state = state

    def is_life_threatening_condition(self):
        return self.temperature >= Person.LIFE_THREATENING_TEMPERATURE or \
               self.water / self.weight <= Person.LIFE_THREATENING_WATER_PCT

    def is_life_incompatible_condition(self):
        return self.temperature >= Person.MAX_TEMPERATURE_TO_SURVIVE or \
               self.water / self.weight <= Person.LOWEST_WATER_PCT_TO_SURVIVE
