from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
import pandas as pd
from sqlalchemy import literal_column, text

from src.config import SECRET_KEY
from src.db import create_db_and_tables, get_db
from src.db.molecule import populate_database, Molecule
from src.forms import MoleculeSearchForm, PROPERTIES


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
bootstrap = Bootstrap(app)
create_db_and_tables()
populate_database()


@app.route("/", methods=["GET", "POST"])
def index():

    search_form = MoleculeSearchForm()

    def render_index(results_table=None):
        return render_template(
            "index.html",
            form=search_form,
            results_table=results_table
        )

    if search_form.validate_on_submit():

        db = next(get_db())

        search_string = search_form.search_string.data
        search_field = search_form.search_field.data

        props_to_search = []
        for prop in PROPERTIES.keys():
            if search_form[prop].data:
                props_to_search.append(PROPERTIES[prop])

        query = db.query(Molecule)
        if search_string != "":
            query = query.filter(literal_column(search_field) == search_string)
        for prop in props_to_search:
            query = query.filter(text(f"properties->'{prop}' IS NOT NULL"))
        results = query.all()

        results = sorted(results, key=lambda r: int(r.cas.split("-")[0]))
        formatted_results = []
        for res in results:
            res_dict = {
                "CAS #": res.cas,
                "IUPAC Name": res.iupac_name,
                "SMILES": res.isomeric_smiles,
                "Formula": res.molecular_formula
            }
            for prop in props_to_search:
                res_dict[
                    list(PROPERTIES.keys())[
                        list(PROPERTIES.values()).index(prop)
                    ]
                ] = res.properties[prop]["value"]
            formatted_results.append(res_dict)
        table = pd.DataFrame(formatted_results).to_html(index=False)

        flash(f"{len(results)} molecules found")
        return render_index(table)

    return render_index()
