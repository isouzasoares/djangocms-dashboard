# -*- coding: utf-8 -*-

from django import forms

choices_comparation =(("gte", 'maior que'),
                    ("lte", 'menor que'),
                    ("equ", "igual a"))
choices_fields = (("total", "Qtd Total"),
                  ("draft", "Qtd Rascunho"),
                  ("published", "Qtd Publicada"))

class DashboardFieldsForm(forms.Form):
    range = forms.IntegerField(label="Valor"),
    fields_search = forms.ChoiceField(
        choices=choices_fields,
        required=False
    )
    comparation = forms.ChoiceField(
        choices=choices_comparation,
        required=False)
    keyword = forms.CharField(label="Busca", max_length=32)
