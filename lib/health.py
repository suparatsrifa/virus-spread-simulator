import random

from lib.perscriptor import get_prescription_method
from lib.observer import Observable, Events
from lib.logger import Logger


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


class Policy:
    def __init__(self, strength=0.0):
        self.strength = strength
        assert (self.strength >= 0) and (self.strength <= 1)

    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.strength == other.strength
        else:
            return False

    def __repr__(self):
        return '{}(p={:.2f})'.format(self.__class__.__name__, self.strength)

    def try_move(self, *args, **kwargs):
        return True

    def try_infect(self, *args, **kwargs):
        return True


class DistrictLockdownPolicy(Policy):
    def __init__(self, strength, max_dist=0.5):
        super(DistrictLockdownPolicy, self).__init__(strength)
        self.max_dist = max_dist
        assert (self.max_dist > 0) and (self.max_dist <= 1)

    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.strength == other.strength and self.max_dist == other.max_dist
        else:
            return False

    def __repr__(self):
        return '{}(p={:.2f}, max_dist={:.2f})'.format(self.__class__.__name__, self.strength, self.max_dist)

    def try_move(self, old_pos, new_pos):
        min_j, max_j, min_i, max_i = GlobalContext().canvas
        dx = (abs(old_pos[0] - new_pos[0]) / (max_j-min_j)) ** 2
        dy = (abs(old_pos[1] - new_pos[1]) / (max_i-min_i)) ** 2
        dist = (dx+dy) ** 0.5  # Movement distance normalized by canvas size

        if random.random() > self.strength:
            # Some people ignore restrictions...
            return True
        else:
            # Other people move only inside their district
            return dist < self.max_dist


class TotalLockdownPolicy(Policy):
    def try_move(self, old_pos, new_pos):
        # Government issue total lockdown policy.
        # Only the most brave (desperate, stupid?) people move during day time
        # P(movement) = 1 - policy_strength
        return random.random() > self.strength


class PPEPolicy(Policy):
    def try_infect(self):
        # Government issue PPE usage policy (masks, gloves) which prevent infection.
        # But some people claims PPE are uncomfortable and don`t use it...?
        # P(infection) = 1 - policy_strength
        return random.random() > self.strength


class CombinedPolicy(Policy):
    def __init__(self, policies):
        super().__init__(1.0)
        self.policies = policies

    def __repr__(self):
        return ' + '.join([repr(p) for p in self.policies])

    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            if len(self.policies) != len(other.policies):
                return False
            for i in range(len(self.policies)):
                if self.policies[i] != other.policies[i]:
                    return False
            return True
        else:
            return False

    def try_move(self):
        # Assume that multiple policies gain total efficiency
        res = True
        for policy in self.policies:
            res = res & policy.try_move()
        return res

    def try_infect(self):
        # Assume that multiple policies gain total efficiency
        res = True
        for policy in self.policies:
            res = res & policy.try_infect()
        return res


@singleton
class DepartmentOfHealth(Observable):
    def __init__(self, hospitals):
        super().__init__()
        self.hospitals = hospitals

    def hospitalize(self, person):
        for hospital in self.hospitals:
            if len(hospital.patients) < hospital.capacity:
                hospital.patients.append(person)
                self.notify_observer(Events.EV_HOSP_IN)
                return hospital

        return None

    def make_policy(self):
        decision = GlobalContext().policy
        if len(GlobalContext().observer.infected_hist) > 0:
            # Collect statistics over all infections for the last day
            new_recoveries = sum(GlobalContext().observer.recovered_hist[-1].values())
            new_infections = sum(GlobalContext().observer.infected_hist[-1].values())
            new_death = sum(GlobalContext().observer.dead_hist[-1].values())
            population = len(GlobalContext().persons)
            # Make decisions
            if new_infections > 0.05 * population:
                decision = PPEPolicy(0.8)

            if new_recoveries > new_infections:
                decision = Policy(0.0)

            if new_death > 0.01 * population:
                decision = TotalLockdownPolicy(0.7)

        if decision != GlobalContext().policy:
            self.notify_observer(Events.EV_POLICY, decision)

        GlobalContext().policy = decision


@singleton
class GlobalContext:
    def __init__(self, canvas, persons, health_dept, observer=None):
        self.canvas = canvas
        self.persons = persons
        self.health_dept = health_dept
        self.policy = Policy(0.0)
        self.observer = observer


class Hospital:
    def __init__(self, capacity, drug_repository, doctor=None):
        self.doctor = doctor
        self.drug_repository = drug_repository
        self.capacity = capacity
        self.patients = []
        self.tests = []

    def __repr__(self):
        return 'Hospital(cap={}, n_patients={}, drug_repo={})'.format(self.capacity, len(self.patients),
                                                                      str(self.drug_repository.__class__.__name__))

    def _treat_patient(self, patient):
        if patient.virus is not None:
            disease_type = patient.virus.get_type()
            dose1, dose2 = random.random(), random.random()
            prescription_method = get_prescription_method(disease_type, self.drug_repository, dose1, dose2)
            prescription_drugs = prescription_method.create_prescription()

            fmt = lambda x: x.__class__.__name__
            Logger().log('Hospital', 'Treating patient infected by "{}" with [{}={}, {}={}]'.format(
                fmt(disease_type), fmt(prescription_drugs[0]), dose1, fmt(prescription_drugs[1]), dose2))

            for drug in prescription_drugs:
                drug.apply(patient)

    def release_patient(self, person):
        try:
            idx = self.patients.index(person)
            del self.patients[idx]
        except IndexError:
            pass

    def treat_patients(self):
        Logger().log('Hospital', 'Treating all patients...')
        for patient in self.patients:
            self._treat_patient(patient)
