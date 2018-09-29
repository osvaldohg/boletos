# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from django.http import HttpResponse
from django.core.urlresolvers import reverse
import pandas as pd
import numpy as np

def index(request):
    return HttpResponse("<h>this is the books homepage</h>")


class Boleto (models.Model):
    def get_absolute_url(self):
        return reverse('boletos:detail', kwargs={'pk':self.pk})

    def get_weight(self,numero):
       
        if numero<100:
            return 10
        elif numero >100 and numero <400:
            return 20
        else:
            return 30

