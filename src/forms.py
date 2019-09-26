#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# src/routes.py
# Developed in 2019 by Travis Kessler <Travis_Kessler@student.uml.edu>
#
# Contains website routing information
#

# 3rd party imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField

# CombustDB web app imports
from src.properties import PROPERTIES


class MoleculeSearch(FlaskForm):
    ''' MoleculeSearch: flask_wtf.FlaskForm child object, handles user input,
    field selection, property filtering
    '''

    search_string = StringField('Search String')
    search_field = SelectField('Search String Type', choices=[
        ('iupac_name', 'IUPAC Name'),
        ('cas', 'CAS Number'),
        ('molecular_formula', 'Molecular Formula'),
        ('isomeric_smiles', 'SMILES')
    ])
    properties = list(PROPERTIES.keys())
    for prop in properties:
        locals()[prop] = BooleanField(prop.upper())
    submit_search = SubmitField('Search Database')
    submit_csv = SubmitField('Export Selection to CSV')
