from fixtures.models import Competition


def get_most_senior_parent_competition(competition: Competition):
    direct_parent = competition.parent_competition

    if direct_parent is None:
        return competition

    return get_most_senior_parent_competition(direct_parent)
