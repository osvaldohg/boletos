# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views import generic
from django.views.generic.edit import CreateView
from .models import Boleto
from sorteo import rank_tickets

class IndexView(generic.ListView):
    template_name='boletos/index.html'

    def get_queryset(self):	
        
        return "hola"

class ContactView(generic.ListView ):
    template_name='boletos/contact.html'
    model=Boleto
    def get_queryset(self):	
        return "hola2"

def numbersv(request):
    
    info = request.GET.get('numbersList','nada')
    output = ""
    #parsed= info.split(",")
    validated_data=validation(info)
    if len(validated_data)==0:
        output="Boletos invalidos, intente de nuevo"
        results=[]
    else:
        results=rank_tickets(validated_data)
        if len(validated_data)==1:
            output="1 Boleto rankeado"
        else:
            output=str(len(validated_data))+" Boletos rankeados"

    #is valid number
    #for validnum in numbers:
    #calculate value:

    return render(request, 'boletos/numbers.html', {
        'info': results,
        'output': output,
      })

def validation(info):
    values=[]
    verifiedValues=[]
        
    if "," in info: 
        values=info.strip().split(",")
    else:
        values=info.strip().split()

    for value in values:
        value=value.strip()
        if len(value)==6 and value.isdigit():
            if int(value)<=280000:
                verifiedValues.append(value)
    
    return verifiedValues



