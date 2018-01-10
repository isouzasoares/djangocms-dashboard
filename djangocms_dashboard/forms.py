# -*- coding: utf-8 -*-

from django import forms

choices_comparation =(("gte", 'Maior que'),
                    ("lte", 'Menor que'),
                    ("equ", "Igual a"))
choices_fields = (("total", "Quantidade Total"),
                  ("draft", "Quantidade Rascunho"),
                  ("published", "Quantidade Publicada"))

class DashboardFieldsForm(forms.Form):
    range = forms.IntegerField(label="Valor"),
    fields_search = forms.ChoiceField(
        choices=choices_fields,
        required=False
    )
    comparation = forms.ChoiceField(
        choices=choices_comparation,
        required=False)
    keyword = forms.CharField(label="Busca", max_length=32, widget=forms.TextInput(attrs={'placeholder': 'Palavra-chave'}))
