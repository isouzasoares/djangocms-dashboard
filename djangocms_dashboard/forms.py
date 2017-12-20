# -*- coding: utf-8 -*-

from django import forms

choices_comparation =(("gte", 'maior que'),
                    ("lte", 'menor que'),
                    ("equ", "igual a"))

class DashboardFieldsForm(forms.Form):
    range = forms.IntegerField(label="Valor"),
    comparation = forms.ChoiceField(
        choices=choices_comparation,
        required=False)
