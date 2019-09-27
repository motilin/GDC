import datetime
import constants as c
import copy


class Document:

    def __init__(self, document):
        self.document = copy.deepcopy(document)

    def get(self, name, var_type):

        name = name.strip()

        if (var_type != list) and \
                (var_type != set) and \
                (var_type != str) and \
                (var_type != int) and \
                (var_type != bool) and \
                (var_type != datetime.datetime):
            raise TypeError('unfamiliar variable type')

        if (name not in self.document.keys()) or \
                (self.document[name] is None) or \
                (len(self.document[name]) == 0):
            if var_type == list:
                return []
            elif var_type == set:
                return set()
            else:
                return None

        if ((type(self.document[name]) == list) or (type(self.document[name]) == set)) and \
                (var_type != list) and (var_type != set):
            if type(self.document[name] == list):
                result = self.document[name][-1]
                self.document[name] = self.document[name][:-1]
            else:
                result = self.document[name].pop()
        else:
            result = self.document.pop(name)

        if result is None:
            pass
        elif var_type == list:
            result = list(result)
        elif var_type == set:
            result = set(result)
        elif var_type == str:
            result = str(result)
        elif var_type == int:
            result = int(result)
        elif var_type == bool:
            result = (str(result).strip().lower() == c.TRUE)
        elif var_type == datetime.datetime and type(self.document[name]) == datetime.datetime:
            pass
        else:
            result = None

        return result
