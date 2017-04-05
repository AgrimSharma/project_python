from django.db.models  import Sum, Count
from django.db import models
from model_utils.models import TimeStampedModel

from service_centre.models import Connection


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    .
    updating ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class ConsolidatedBag(TimeStampedModel):
    """
    status:
    0-deleted
    1-created from sc,
    2-closed from sc,
    3-included in connection at sc,
    4-created from hub,
    5-closed from hub,
    6-included in connection from hub,
    7-inscanned at hub,
    8-inscanned at destination
    """
    bag_number    = models.CharField(max_length=30, unique=True, db_index=True)
    origin        = models.ForeignKey('location.servicecenter')
    hub           = models.ForeignKey('location.servicecenter',
                                    null=True, blank=True,
                                    related_name='consolidated_bag_hub')
    current_sc    = models.ForeignKey('location.servicecenter',
                                    related_name='consolidated_bag_current_sc')
    destination   = models.ForeignKey('location.servicecenter',
                                    related_name='consolidated_bag_dest')
    actual_weight = models.FloatField(default=0.0)
    status        = models.SmallIntegerField(default=1, db_index=True)
    created_by    = models.ForeignKey('authentication.employeemaster')

    def __unicode__(self):
        return self.bag_number

    @property
    def get_ship_count(self):
        ship_count = ConsolidatedBagCollection.objects.filter(
            consolidated_bag=self
        ).aggregate(ct=Count('bag__shipments__id'))['ct']
        return ship_count if ship_count else 0

    def close_bag(self):
        weight = ConsolidatedBagCollection.objects.filter(
            consolidated_bag=self).aggregate(
            weight_sum=Sum('bag__actual_weight'))['weight_sum']
        self.actual_weight = weight if weight else 0 
        self.status = 2
        self.save()
        return True

    def add_to_connection(self, cid):
        # consolidated bag can be included to any connection, only if it is at created status
        if self.status not in [2, 5, 7]:
            return False
        connection = Connection.objects.get(id=cid)
        try:
            cbag_connection = ConsolidatedBagConnection.objects.get(
                connection=connection, consolidated_bag=self)

            # only removed bag can be updated from here
            if cbag_connection.status == 0:
                cbag_connection.status = 1
                cbag_connection.save()
            else:
                return None
        except ConsolidatedBagConnection.DoesNotExist:
            cbag_connection = ConsolidatedBagConnection.objects.create(
                connection=connection, consolidated_bag=self)

        if self.status == 2:
            self.status = 3
        elif self.status == 5:
            self.status = 6
        self.save()
        return cbag_connection 


class ConsolidatedBagCollection(TimeStampedModel):
    """
    This models is updated when bags are included into CBag
    status:
    0- deleted / excluded
    1- bag added 
    2- inscanned at hub,
    3- inscanned at dc
    """
    consolidated_bag = models.ForeignKey(ConsolidatedBag)
    bag              = models.ForeignKey('service_centre.bags')
    status           = models.SmallIntegerField(default=1, db_index=True)

    def __unicode__(self):
        return '{0} - {1}'.format(
            self.consolidated_bag.bag_number, self.bag.bag_number)


class ConsolidatedBagConnection(TimeStampedModel):
    """
    This models is updated when CBags are included into Connection
    0- deleted / excluded
    1- bag added 
    2- inscanned at hub,
    3- inscanned at dc
    """
    consolidated_bag = models.ForeignKey(ConsolidatedBag)
    connection       = models.ForeignKey('service_centre.connection')
    status           = models.SmallIntegerField(default=1, db_index=True)

    def __unicode__(self):
        return '{0} - {1}'.format(
            self.consolidated_bag.bag_number, self.connection.id)
