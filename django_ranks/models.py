from typing import Union, List

from django import dispatch
from django.db import models
from django.db.models import QuerySet
from openskill import rate, Rating, ordinal as _ordinal
from .base import NumericModel


# Create your models here.
def get_default_mu():
    r = Rating()
    return r.mu


def get_default_sig():
    r = Rating()
    return r.sigma


rate_changed = dispatch.Signal()


class Rank(NumericModel):
    """
    a class for Ranks
    """
    def get_number(self):
        return self.score

    mu = models.FloatField(default=get_default_mu)
    sigma = models.FloatField(default=get_default_sig)
    score = models.FloatField(default=0.0)

    class Meta:
        app_label = "graffrank"
        ordering = ["score"]

    # https://github.com/OpenDebates/openskill.py

    def sent_rate_changed(self, new_score):
        print(f"{self.__class__}:({self}) fired new_score with {new_score}")
        rate_changed.send(sender=self.__class__, new_score=new_score)

    def save(self, *args, **kwargs):
        self.score = self.ordinal
        if self.score != self.original_score:
            self.sent_rate_changed(new_score=self.score)

        super(Rank, self).save(*args, **kwargs)
        self.original_score = self.score

    def __init__(self, *args, **kwargs):
        super(Rank, self).__init__(*args, **kwargs)
        self.original_score = self.score

    @classmethod
    def get_default(cls):
        r = Rating()
        mu = r.mu
        sigma = r.sigma
        o = _ordinal(r)
        return Rank(mu=mu, sigma=sigma, ordinal=o)

    @classmethod
    def get_default_pk(cls):
        r = cls.get_default()
        rank, created = cls.objects.get_or_create(mu=r.mu, sigma=r.sigma, ordinal=r.ordinal)
        return rank.pk

    @property
    def rating(self):
        return Rating(mu=self.mu, sigma=self.sigma)

    @property
    def ordinal(self):
        return _ordinal(self.rating)

    def __str__(self):
        return f"{self.ordinal} | {self.rating}"

    def set_rate(self, r, do_save=True):
        self.mu = r.mu
        self.sigma = r.sigma
        if do_save:
            self.save()


def rate_single_member_teams(teams: Union[List['Rank'], QuerySet['Rank']], scores: List[int]):
    """
    Expects teams with only one member, recalculates the rank for each `team` and returns the resulting ranks
    teams: List[List[Rating]], **options) -> List[List[Rating]
    :param teams: List[Ratable]
    :param scores: List[int]
    :return: List[List[Rating]]
    """
    # score = [t.get_score() for t in teams]
    if len(teams[0]) > 1:
        raise NotImplementedError(f"{rate_single_member_teams} expects teams of 1")
    result = [[a2], [b2], [c2], [d2]] = rate([[t.rating] for t in teams], score=scores)
    for nr, team in zip(result, teams):
        team.set_rate(nr[0])
        team.save()
    return result
