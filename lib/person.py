from random import randint
from abc import ABC, abstractmethod

from lib.basic_person import Person
from lib.health import GlobalContext


class DefaultPerson(Person):
    def _day_actions(self):
        min_j, max_j, min_i, max_i = GlobalContext().canvas
        new_position = (randint(min_j, max_j), randint(min_i, max_i))

        if GlobalContext().policy.try_move(self.position, new_position):
            self.position = new_position


class CommunityPerson(Person):
    def __init__(self, community_position=(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.community_position = community_position

    def attrs(self):
        basic_attrs = super(CommunityPerson, self).attrs()
        basic_attrs['community'] = self.community_position
        return basic_attrs

    def _day_actions(self):
        if GlobalContext().policy.try_move(self.position, self.community_position):
            self.position = self.community_position


class AbstractPersonFactory(ABC):
    def __init__(self, context):
        self.min_age, self.max_age = 1, 90
        self.min_weight, self.max_weight = 30, 120
        self.min_j, self.max_j, self.min_i, self.max_i = context

    @abstractmethod
    def get_person(self) -> Person:
        pass


class DefaultPersonFactory(AbstractPersonFactory):
    def get_person(self) -> Person:
        return DefaultPerson(
            home_position=(randint(self.min_j, self.max_j), randint(self.min_i, self.max_i)),
            age=randint(self.min_age, self.max_age),
            weight=randint(self.min_weight, self.max_weight),
        )


class CommunityPersonFactory(AbstractPersonFactory):
    def __init__(self, *args, community_position=(0, 0)):
        super().__init__(*args)
        self.community_position = community_position

    def get_person(self) -> Person:
        return CommunityPerson(
            home_position=(randint(self.min_j, self.max_j), randint(self.min_i, self.max_i)),
            age=randint(self.min_age, self.max_age),
            weight=randint(self.min_weight, self.max_weight),
            community_position=self.community_position
        )
