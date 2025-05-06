from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField


PROPERTIES = {
    "Cetane number": "cetane_number",
    "Yield sooting index": "ysi_unified",
    "Lower heating value": "lower_heating_value",
    "Motor octane number": "motor_octane_number",
    "Research octane number": "research_octane_number",
    "Octane sensitivity": "octane_sensitivity",
    "Kinematic viscosity": "kinematic_viscosity",
    "Autoignition temp.": "autoignition_temp",
    "Boiling point": "boiling_point",
    "Flash point": "flash_point",
    "Heat of vaporization": "heat_of_vaporization",
    "Melting point": "melting_point"
}


class MoleculeSearchForm(FlaskForm):

    search_string = StringField("Search String")
    search_field = SelectField(
        "Search String Type",
        choices=[
            ("cas", "CAS Number"),
            ("cid", "PubChem CID"),
            ("iupac_name", "IUPAC Name"),
            ("canonical_smiles", "Canonical SMILES"),
            ("isomeric_smiles", "Isomeric SMILES"),
            ("inchi", "InChI"),
            ("inchikey", "InChIKey"),
            ("molecular_formula", "Molecular Formula")
        ]
    )
    properties = list(PROPERTIES.keys())
    for prop in properties:
        locals()[prop] = BooleanField(prop)
    submit_search = SubmitField("Search Database")
    submit_csv = SubmitField("Export to CSV")
