import os

from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_table import Col, Table
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField

from config import Config, PROPERTIES

class MoleculeSearch(FlaskForm):

    search_string = StringField('Search String')
    search_field = SelectField('Search String Type', choices=[
        ('iupac_name', 'IUPAC Name'),
        ('cas', 'CAS Number'),
        ('molecular_formula', 'Molecular Formula'),
        ('isomeric_smiles', 'SMILES')
    ])
    show_predictions = BooleanField('Show Property Predictions')
    properties = list(PROPERTIES.keys())
    for prop in properties:
        locals()[prop] = BooleanField(prop)
    submit_search = SubmitField('Search Database')
    submit_csv = SubmitField('Export to CSV')


app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():

    search_form = MoleculeSearch()

    def render_index(results_table=None):
        return render_template('index.html', form=search_form,
                            results_table=results_table)

    if search_form.validate_on_submit():

        query = {}

        # Parse search string, if provided
        search_string = search_form.search_string.data
        search_field = search_form.search_field.data
        if search_field == 'cid':
            try:
                search_string = int(search_string)
            except:
                pass
        if search_string != '':
            query[search_field] = search_string

        # Determine which properties are being searched for
        props_to_search = []
        pred_props = []
        for prop in list(PROPERTIES.keys()):
            if search_form[prop].data:
                props_to_search.append(PROPERTIES[prop])
                pred_props.append(PROPERTIES[prop])
        props_to_search = [f'properties.{p}' for p in props_to_search]
        for prop in props_to_search:
            query[prop] = {'$exists': True}

        # Connect to MongoDB
        try:
            client = MongoClient(os.environ['MONGODB_CONNSTRING'])
        except ConnectionFailure as exc:
            flash(f'{exc}')
            return render_index()
        database = client['ecrl-db']
        collection = database['compounds']

        # Perform query
        results = []
        for res in collection.find(query):
            results.append(res)
        if len(results) == 0:
            flash(f'Compound {search_string} not found')
            return render_index()

        # Format results
        results = sorted(results, key=lambda r: int(r[u'cas'].split('-')[0]))
        formatted_results = []
        for res in results:
            res_dict = {
                'iupac_name': res[u'iupac_name'],
                'cas': res[u'cas'],
                'molecular_formula': res[u'molecular_formula'],
                'isomeric_smiles': res[u'isomeric_smiles'],
                'canonical_smiles': res[u'canonical_smiles'],
                'cid': res[u'cid'],
                'inchi': res[u'inchi'],
                'inchikey': res[u'inchikey']
            }
            for prop in props_to_search:
                key1, key2 = prop.split('.')
                if 'pred' in key1:
                    res_dict['pred_' + key2] = res[key1][key2]['value']
                else:
                    res_dict[key2] = res[key1][key2]['value']
            formatted_results.append(res_dict)

        # Display results
        if search_form.submit_search.data:

            class SearchResults(Table):

                iupac_name = Col('IUPAC Name')
                cas = Col('CAS #')
                isomeric_smiles = Col('SMILES')
                molecular_formula = Col('Formula')
                for prop in props_to_search:
                    key1, key2 = prop.split('.')
                    if 'pred' in key1:
                        key2 = 'pred_' + key2
                    locals()[key2] = Col(key2.title().replace('_', ' '))

            flash(f'{len(results)} compounds found')
            table = SearchResults(formatted_results)
            return render_index(table)

    return render_index()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
