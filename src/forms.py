from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from src.properties import PROPERTIES


class MoleculeSearch(FlaskForm):

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
