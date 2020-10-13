from collections import defaultdict
import pandas as pd
from enum import Enum

from lib.logger import Logger


class Observable:
    def __init__(self):
        self.observer = None

    def register_observer(self, observer):
        self.observer = observer

    def notify_observer(self, event, *args, **kwargs):
        self.observer.notify(event, *args, **kwargs)


class Events(Enum):
    EV_DAY_END = 1
    EV_INFECTION = 2
    EV_DEATH = 3
    EV_RECOVERY = 4
    EV_ANTIBODY = 5
    EV_HOSP_IN = 6
    EV_HOSP_OUT = 7
    EV_POLICY = 8


class Observer:
    def __init__(self, observables):
        self.observables = observables
        for obs in self.observables:
            obs.register_observer(self)

        self.infected_hist = []
        self.recovered_hist = []
        self.ab_hist = []
        self.dead_hist = []
        self.hospitalized_hist = []
        self.policies = []
        self.day = 0

        self.reset()

    def reset(self):
        self.infected = defaultdict(int)
        self.recovered = defaultdict(int)
        self.ab = defaultdict(int)
        self.dead = defaultdict(int)
        self.hositalized = 0

    def day_finished(self):
        self.infected_hist.append(self.infected)
        self.recovered_hist.append(self.recovered)
        self.ab_hist.append(self.ab)
        self.dead_hist.append(self.dead)
        self.hospitalized_hist.append(self.hositalized)
        self.day += 1
        self.reset()

    def infections_list(self):
        result = set()
        for lst in [self.infected_hist, self.recovered_hist, self.ab_hist, self.dead_hist]:
            for it in lst:
                result.update(list(it.keys()))
        return list(result)

    def export_df(self):
        infections_lst = self.infections_list()

        res = {
            'day': list(range(len(self.dead_hist))),
            'hospitalized': self.hospitalized_hist,
        }

        fmt = lambda x: x.name
        for lst in ['infected', 'recovered', 'ab', 'dead']:
            for infection_type in infections_lst:
                res[lst+'_'+fmt(infection_type)] = [d.get(infection_type, 0) for d in getattr(self, lst+'_hist')]

        res = pd.DataFrame(res)

        for lst in ['infected', 'recovered', 'ab', 'dead']:
            res[lst+'_all'] = sum([res[lst+'_'+fmt(inf_type)] for inf_type in infections_lst])

        return res

    def notify(self, event_type, *args, **kwargs):
        {
            Events.EV_DAY_END: self.notify_day_end,
            Events.EV_DEATH: self.notify_death,
            Events.EV_HOSP_IN: self.notify_hosp_in,
            Events.EV_HOSP_OUT: self.notify_host_out,
            Events.EV_RECOVERY: self.notify_recovery,
            Events.EV_ANTIBODY: self.notify_antibody,
            Events.EV_INFECTION: self.notify_infection,
            Events.EV_POLICY: self.notify_policy
        }[event_type](*args, **kwargs)

    def notify_policy(self, policy):
        self.policies.append((self.day, str(policy)))

    def notify_day_end(self, *args, **kwargs):
        Logger().log('Observer', '-' * 20 + ' Day end ' + '-' * 20)
        self.day_finished()

    def notify_infection(self, infection_type, *args, **kwargs):
        Logger().log('Observer', 'New infection of type ' + str(infection_type.name))
        self.infected[infection_type] += 1

    def notify_death(self, infection_type, *args, **kwargs):
        Logger().log('Observer', 'New death')
        self.dead[infection_type] += 1

    def notify_recovery(self, infection_type, *args, **kwargs):
        Logger().log('Observer', 'New recovery of type ' + str(infection_type.name))
        self.recovered[infection_type] += 1

    def notify_antibody(self, infection_type, *args, **kwargs):
        Logger().log('Observer', 'New antibody of type ' + str(infection_type.name))
        self.ab[infection_type] += 1

    def notify_hosp_in(self, *args, **kwargs):
        Logger().log('Observer', 'New hospitalization')
        self.hositalized += 1

    def notify_host_out(self, *args, **kwargs):
        Logger().log('Observer', 'Patient moved out from hospital')
        self.hositalized -= 1
