#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# src/routes.py
# Developed in 2019 by Travis Kessler <Travis_Kessler@student.uml.edu>
#
# Contains website routing information
#

# 3rd party imports
from flask import flash, render_template, Response
from flask_table import Col, Table
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Stdlib. imports
from tempfile import NamedTemporaryFile
from csv import DictWriter
from os import unlink

# CombustDB web app imports
from src import app
from src.forms import MoleculeSearch
from src.properties import PROPERTIES


class SearchResults(Table):
    ''' SearchResults: flask_table.Table child object, houses compound
    information to be displayed in web app's results section

    Args:
        list: each element is a dictionary with keys corresponding to object
            attributes, values are database values
    '''

    iupac_name = Col('IUPAC Name')
    cas = Col('CAS #')
    for prop in list(PROPERTIES.keys()):
        locals()[prop] = Col(prop.upper())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    ''' index: main page of web app; handles database queries based on user
    input, serving results to HTML template, allows downloading of results as
    CSV file
    '''

    # Initialize form for user input
    search_form = MoleculeSearch()

    def render_index(results_table=None):
        ''' render_index: renders the main page's HTML

        Args:
            results_table (SearchResults): queried results in flask_table.Table
                format

        Returns:
            Rendered HTML via templates/index.html
        '''
        return render_template(
            'index.html', form=search_form, results_table=results_table
        )

    # If form's submit button pressed:
    if search_form.validate_on_submit():

        # Obtain user input, specified field to query with
        search_string = search_form.search_string.data
        search_field = search_form.search_field.data

        # Convert user input to `int` if user specifid CID query field
        if search_field == 'cid':
            try:
                search_string = int(search_string)
            except:
                pass

        # Connect to CombustDB MongoDB Atlas database
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

        # Assemble the query
        query = {}
        # If user specified information in text box, include it
        if search_string != '':
            query[search_field] = search_string
        # Check for specific property check-boxes
        for prop in list(PROPERTIES.keys()):
            if search_form[prop].data:
                query['properties.{}'.format(PROPERTIES[prop])] = {
                    '$exists': True
                }
        # Perform query
        results = collection.find(query)

        # Nothing found
        if results.count() == 0:
            flash('Compound not found')
            return render_index()
        num_compounds = results.count()

        # Sort by CAS, ascending
        results = sorted(results, key=lambda r: int(r[u'cas'].split('-')[0]))

        # Format results, one dict per result
        formatted_results = []
        for result in results:
            # Obtain identifying information
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
            # Obtain property values, if they exist
            for prop in list(PROPERTIES.keys()):
                try:
                    result_dict[prop] = result[u'properties'][
                        PROPERTIES[prop]
                    ]['value']
                except KeyError:
                    result_dict[prop] = ''
            formatted_results.append(result_dict)

        # If search was performed, display it
        if search_form.submit_search.data:
            flash('Compounds found: {}'.format(num_compounds))
            table = SearchResults(formatted_results)
            return render_index(table)

        # If CSV was requested, create temporary file, have user download it
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

        # Else, just in case
        else:
            raise Exception('Unknown form submission.')

    # Render index.html
    return render_index()
