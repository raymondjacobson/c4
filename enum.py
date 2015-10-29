'''
This method defines enum functionality and can
be used as follows:

Enum = enum(RED=1, BLUE=2, GREEN=3')

'''


def enum(**enums):
    return type('Enum', (), enums)
