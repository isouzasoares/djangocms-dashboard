# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unicodedata import normalize


def remover_espacos(n):
    return ' '.join(n.split())


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def limpar_nome(nome):
    sem_espacos = remover_espacos(nome)
    return remover_acentos(sem_espacos).lower()
