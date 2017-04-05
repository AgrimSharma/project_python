from django.db import models
from customer.models import Customer

# Create your models here.

#Suprotip 15-12-2014
class ProductItemMasterManager(models.Manager):
    '''TODO'''
    def create_PI(self, product_description, product_weight,product_height,product_breadth,product_length,squ_id, customer):
        ProductItemMaster = self.create(product_description=product_description,product_weight=product_weight,product_height=product_height,product_breadth=product_breadth,product_length=product_length,squ_id=squ_id, customer=customer)
        return ProductItemMaster

class ProductItemMaster (models.Model):
    '''class ProductItemMaster'''

    '''Attributes:
    a. Product Description
    b. Weight 
    c. Height 
    d. Breadth
    e. length
    f. squ_id
    g. Customer - Foreign key'''
    product_description = models.CharField (max_length=200, null=True, blank=True) #db_index = True
    product_weight = models.FloatField(default=0.0, blank=True, null=True)
    product_height = models.FloatField(default=0.0, blank=True, null=True)
    product_breadth = models.FloatField(default=0, blank=True, null=True)
    product_length = models.FloatField(default=0, blank=True, null=True)
    squ_id = models.CharField(max_length=100, unique=True, null=True) #db_index = True
    customer = models.ForeignKey (Customer) #filter customer id as digit: 4
    #add four more field:
    # 1. added_on
    #2. added_by
    #3. updated_on
    #4. updated_by

    objects = ProductItemMasterManager()
    
#    def clean(self):
#        print 'run'
#        if not self.product_description.isalpha():
#            raise ValidationError('%s contains numbers or special characters' % value)

    '''possible methods:
       2. View/Download all
       3. Upload to update / add new'''
    
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in ProductItemMaster._meta.fields]
    
    def __unicode__(self):
        return str(self.squ_id) + " - " + str(self.product_description)

    class Meta:
        verbose_name = "pimaster"
        # db_table = 