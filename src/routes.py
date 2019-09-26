from src import app
from src.forms import MoleculeSearch
from src.properties import PROPERTIES
from flask import render_template, flash, Response
from flask_table import Table, Col
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from tempfile import NamedTemporaryFile
from csv import DictWriter
from os import unlink


class SearchResults(Table):

    iupac_name = Col('IUPAC Name')
    cas = Col('CAS #')
    for prop in list(PROPERTIES.keys()):
        locals()[prop] = Col(prop.upper())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    search_form = MoleculeSearch()

    def render_index(results_table=None):
        return render_template(
            'index.html', form=search_form, results_table=results_table
        )

    if search_form.validate_on_submit():

        search_string = search_form.search_string.data
        search_field = search_form.search_field.data

        if search_field == 'cid':
            try:
                search_string = int(search_string)
            except:
                pass

        try:
            client = MongoClient(
                'mongodb+srv://heroku_client:bfp4QhRlFf7L2ouT@combustdb-xofe6.'
                'mongodb.net/test?retryWrites=true&w=majority'
            )
        except ConnectionFailure:
            flash('ConnectionFailure: unable to connect to database')
            return render_index()
        database = client.combustdb
        collection = database.compounds

        query = {}
        if search_string != '':
            query[search_field] = search_string
        for prop in list(PROPERTIES.keys()):
            if search_form[prop].data:
                query['properties.{}'.format(PROPERTIES[prop])] = {
                    '$exists': True
                }
        results = collection.find(query)

        if results.count() == 0:
            flash('Compound not found')
            return render_index()

        formatted_results = []
        for result in results:
            result_dict = {
                'iupac_name': result[u'iupac_name'],
                'cas': result[u'cas'],
                'molecular_formula': result[u'molecular_formula'],
                'isomeric_smiles': result[u'isomeric_smiles'],
                'canonical_smiles': result[u'canonical_smiles'],
                'cid': result[u'cid'],
                'inchi': result[u'inchi'],
                'inchikey': result[u'inchikey']
            }
            for prop in list(PROPERTIES.keys()):
                try:
                    result_dict[prop] = result[u'properties'][
                        PROPERTIES[prop]
                    ]['value']
                except KeyError:
                    result_dict[prop] = ''
            formatted_results.append(result_dict)

        if search_form.submit_search.data:
            flash('Compounds found: {}'.format(results.count()))
            table = SearchResults(formatted_results)
            return render_index(table)
        elif search_form.submit_csv.data:
            temp_file = NamedTemporaryFile(suffix='.csv', mode='w',
                                           delete=False)
            csv_keys = ['iupac_name', 'cas', 'molecular_formula',
                        'isomeric_smiles', 'canonical_smiles', 'cid', 'inchi',
                        'inchikey']
            csv_keys.extend(list(PROPERTIES.keys()))
            writer = DictWriter(temp_file, csv_keys, delimiter=',',
                                lineterminator='\n')
            writer.writeheader()
            writer.writerows(formatted_results)
            temp_file.close()

            with open(temp_file.name, 'r') as csv_file:
                content = csv_file.read()
            csv_file.close()
            return Response(content, mimetype='text/csv', headers={
                'Content-Disposition':
                'attachment;filename=combustdb_results.csv'
            })
            unlink(temp_file.name)
        else:
            raise Exception('Unknown form submission.')

    return render_index()
