from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField


class MoleculeSearch(FlaskForm):

    search_string = StringField('Search String')
    search_field = SelectField('Search String Type', choices=[
        ('iupac_name', 'IUPAC Name'),
        ('cas', 'CAS Number'),
        ('molecular_formula', 'Molecular Formula'),
        ('isomeric_smiles', 'SMILES')
    ])
    cn = BooleanField('Experimental CN')
    ysi = BooleanField('Experimental YSI')
    mon = BooleanField('Experimental MON')
    ron = BooleanField('Experimental RON')
    kv = BooleanField('Experimental KV')
    submit_search = SubmitField('Search Database')
    submit_csv = SubmitField('Export Selection to CSV')
