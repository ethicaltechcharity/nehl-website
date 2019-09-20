import uuid
import os


def get_most_senior_parent_competition(competition):
    direct_parent = competition.parent_competition

    if direct_parent is None:
        return competition

    return get_most_senior_parent_competition(direct_parent)


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('match_cards', filename)
