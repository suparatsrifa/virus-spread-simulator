import random

from lib.drugs import ExpensiveDrugRepository, CheapDrugRepository
from lib.person import DefaultPersonFactory, CommunityPersonFactory
from lib.health import Hospital


def simulate_day(context):
    persons, health_dept, hospitals = context.persons, context.health_dept, context.health_dept.hospitals

    health_dept.make_policy()

    for hospital in hospitals:
        hospital.treat_patients()

    for person in persons:
        person.day_actions()

    for person in persons:
        for other in persons:
            if person is not other and person.is_close_to(other):
                person.interact(other)

    for person in persons:
        person.night_actions()

    context.observer.notify_day_end()


def create_hospitals(n_hospitals, capacity=100):
    hospitals = [
        Hospital(capacity=capacity,
                 drug_repository=ExpensiveDrugRepository()
                                 if random.random() <= 0.3
                                 else CheapDrugRepository())
        for i in range(n_hospitals)
    ]
    return hospitals


def create_persons(min_j, max_j, min_i, max_i, n_persons):
    factory_params = (min_j, max_j, min_i, max_i)

    default_factory = DefaultPersonFactory(factory_params)
    community_factory = CommunityPersonFactory(factory_params, community_position=(50, 50))

    n_default_persons = int(n_persons * 0.75)
    n_community_persons = n_persons - n_default_persons

    persons = []
    for i in range(n_default_persons):
        persons.append(default_factory.get_person())

    for i in range(n_community_persons):
        persons.append(community_factory.get_person())

    return persons
