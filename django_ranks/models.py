from typing import Union, List

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet
from openskill import rate, Rating, ordinal as _ordinal
from .base import NumericModel
from .signals import rate_changed
import logging

# Create your models here.
def get_default_mu():
    r = Rating()
    return r.mu


def get_default_sig():
    r = Rating()
    return r.sigma


class Rank(NumericModel):
    """
    A class for Ranks.

    Attributes:
    -----------
    mu : float
        The default value of mu.
    sigma : float
        The default value of sigma.
    score : float
        The default value of score.
    content_type : ForeignKey
        A foreign key to ContentType model.
    object_id : PositiveIntegerField
        An integer field for object id.
    content_object : GenericForeignKey
        A generic foreign key to content object.
    ordering : list
        A list of fields to order by.
    indexes : list
        A list of indexes to create.

    Methods:
    --------
    get_number()
        Returns the score.
    get_for_model(model_class: ContentType)
        Returns the Rank objects filtered by content_type.
    sent_rate_changed(new_score)
        Sends the rate changed signal.
    save(*args, **kwargs)
        Saves the Rank object.
    get_default()
        Returns a Rank object with default values.
    get_default_pk()
        Returns the primary key of the default Rank object.
    rating()
        Returns a Rating object with mu and sigma values.
    ordinal()
        Returns the ordinal value of the Rank object.
    set_rate(r, do_save=True)
        Sets the mu and sigma values of the Rank object.
    __str__()
        Returns a string representation of the Rank object.
    """

    def get_number(self):
        """
        Returns the score.

        Returns:
        --------
        float
            The score of the Rank object.
        """
        return self.score

    mu = models.FloatField(default=get_default_mu)
    sigma = models.FloatField(default=get_default_sig)
    score = models.FloatField(default=0.0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["score"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    # https://github.com/OpenDebates/openskill.py

    @classmethod
    def get_for_model(cls, model_class: ContentType):
        """
        Returns the Rank objects filtered by content_type.

        Parameters:
        -----------
        model_class : ContentType
            The content type of the model.

        Returns:
        --------
        QuerySet
            The Rank objects filtered by content_type.
        """
        ct = ContentType.objects.get_for_model(model_class)
        return cls.objects.filter(content_type=ct)

    def sent_rate_changed(self, new_score):
        """
        Sends the rate changed signal.

        Parameters:
        -----------
        new_score : float
            The score to set.
        """
        logging.info(f"{self.__class__}:({self}) fired new_score with {new_score}")
        rate_changed.send(sender=self.__class__, new_score=new_score)

    def save(self, *args, **kwargs):
        """
        Saves the Rank object.

        Parameters:
        -----------
        args : tuple
            The positional arguments.
        kwargs : dict
            The keyword arguments.
        """
        self.score = self.ordinal
        if self.score != self.original_score:
            self.sent_rate_changed(new_score=self.score)

        super(Rank, self).save(*args, **kwargs)
        self.original_score = self.score

    def __init__(self, *args, **kwargs):
        """
        Initializes the Rank object.

        Parameters:
        -----------
        args : tuple
            The positional arguments.
        kwargs : dict
            The keyword arguments.
        """
        super(Rank, self).__init__(*args, **kwargs)
        self.original_score = self.score

    @classmethod
    def get_default(cls):
        """
        Returns a Rank object with default values.

        Returns:
        --------
        Rank
            A Rank object with default values.
        """
        r = Rating()
        mu = r.mu
        sigma = r.sigma
        o = _ordinal(r)
        return Rank(mu=mu, sigma=sigma, ordinal=o)

    @classmethod
    def get_default_pk(cls):
        """
        Returns the primary key of the default Rank object.

        Returns:
        --------
        int
            The primary key of the default Rank object.
        """
        r = cls.get_default()
        rank, created = cls.objects.get_or_create(mu=r.mu, sigma=r.sigma, ordinal=r.ordinal)
        return rank.pk

    @property
    def rating(self):
        """
        Returns a Rating object with mu and sigma values.

        Returns:
        --------
        Rating
            A Rating object with mu and sigma values.
        """
        return Rating(mu=self.mu, sigma=self.sigma)

    @property
    def ordinal(self):
        """
        Returns the ordinal value of the Rank object.

        Returns:
        --------
        float
            The ordinal value of the Rank object.
        """
        return _ordinal(self.rating)

    def __str__(self):
        """
        Returns a string representation of the Rank object.

        Returns:
        --------
        str
            A string representation of the Rank object.
        """
        return f"{self.ordinal} | {self.rating}"

    def set_rate(self, r, do_save=True):
        """
        Sets the mu and sigma values of the Rank object.

        Parameters:
        -----------
        r : Rating
            The Rating object to set.
        do_save : bool
            A boolean value to save the Rank object or not.
        """


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
