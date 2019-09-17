from src import app
from src.forms import MoleculeSearch
from flask import render_template, flash, Response
from flask_table import Table, Col
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from tempfile import NamedTemporaryFile
from csv import DictWriter
from os import unlink


class SearchResults(Table):

    iupac_name = Col('IUPAC Name\t')
    cas = Col('CAS #\t')
    molecular_formula = Col('Molecular Formula\t')
    isomeric_smiles = Col('SMILES\t')
    cn = Col('CN\t')
    ysi = Col('YSI\t')
    mon = Col('MON\t')
    ron = Col('RON\t')
    kv = Col('KV\t')


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
        if search_form.cn.data:
            query['properties.cetane_number'] = {'$exists': True}
        if search_form.ysi.data:
            query['properties.ysi_unified'] = {'$exists': True}
        if search_form.mon.data:
            query['properties.motor_octane_number'] = {'$exists': True}
        if search_form.ron.data:
            query['properties.research_octane_number'] = {'$exists': True}
        if search_form.kv.data:
            query['properties.kinematic_viscosity'] = {'$exists': True}

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
            try:
                result_dict['cn'] = result[u'properties'][
                    'cetane_number'
                ]['value']
            except KeyError:
                result_dict['cn'] = ''
            try:
                result_dict['ysi'] = result[u'properties'][
                    'ysi_unified'
                ]['value']
            except KeyError:
                result_dict['ysi'] = ''
            try:
                result_dict['mon'] = result[u'properties'][
                    'motor_octane_number'
                ]['value']
            except KeyError:
                result_dict['mon'] = ''
            try:
                result_dict['ron'] = result[u'properties'][
                    'research_octane_number'
                ]['value']
            except KeyError:
                result_dict['ron'] = ''
            try:
                result_dict['kv'] = result[u'properties'][
                    'kinematic_viscosity'
                ]['value']
            except KeyError:
                result_dict['kv'] = ''
            formatted_results.append(result_dict)

        if search_form.submit_search.data:
            flash('Compounds found: {}'.format(results.count()))
            table = SearchResults(formatted_results)
            return render_index(table)
        elif search_form.submit_csv.data:
            temp_file = NamedTemporaryFile(suffix='.csv', mode='w',
                                           delete=False)
            writer = DictWriter(temp_file, [
                'iupac_name', 'cas', 'molecular_formula', 'isomeric_smiles',
                'canonical_smiles', 'cid', 'inchi', 'inchikey', 'cn', 'ysi',
                'mon', 'ron', 'kv'
            ], delimiter=',', lineterminator='\n')
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
