__author__ = "reed@reedjones.me"

import abc
import operator

from django.db import models

ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,  # use operator.div for Python 2
    '%': operator.mod,
    '^': operator.xor,
    '>=': operator.ge,
    '>': operator.gt,
    '<=': operator.le,
    '<': operator.lt,
    '==': operator.eq,
    '!=': operator.ne
}


def check_op(oper):
    if oper not in ops:
        raise NotImplementedError(f"No Operator for {oper}")


def run_operator(oper, *args):
    check_op(oper)
    return ops[oper](*args)


class AbstractModelMeta(abc.ABCMeta, type(models.Model)):
    pass


class NumericModel(models.Model, metaclass=AbstractModelMeta):
    """
    Abstract Model class that defines a generic 'numeric' model - anything that can be scored or ranked
    """

    # You may have common fields here.

    class Meta:
        abstract = True

    @abc.abstractmethod
    def get_number(self):
        """Must Implement"""
        pass

    def numerical(self, other, compare_type):
        check_op(compare_type)
        if type(other) is type(self):
            return run_operator(compare_type, self.get_number(), other.get_number())
        elif type(other) is int or type(other) is float:
            return run_operator(compare_type, self.get_number(), int(other))
        elif other.__dict__().get("__int__"):
            return run_operator(compare_type, self.get_number(), other.__int__())
        elif other.__dict__().get("__float__"):
            return run_operator(compare_type, self.get_number(), other.__float__())
        else:
            raise NotImplementedError(f"Comparison between {type(self)} and {type(other)} Invalid")

    def __eq__(self, other):
        if not other:
            return False
        return self.numerical(other, '==')

    # Probably a better way to do this

    def __lt__(self, other):
        return self.numerical(other, '<')

    def __le__(self, other):
        return self.numerical(other, '<=')

    def __ge__(self, other):
        return self.numerical(other, '>=')

    def __gt__(self, other):
        return self.numerical(other, '>')

    def __ne__(self, other):
        return self.numerical(other, '!=')

    def __add__(self, other):
        return self.numerical(other, '+')

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        return self.numerical(other, '*')

    def __truediv__(self, other):
        return self.numerical(other, '/')

    def __sub__(self, other):
        return self.numerical(other, '-')

    def __mod__(self, other):
        return self.numerical(other, '%')

    def __xor__(self, other):
        return self.numerical(other, '^')
