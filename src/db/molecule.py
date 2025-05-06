import json
import os
import pathlib

from sqlalchemy import Column, Integer, String, PickleType, JSON

from src.db import Base, get_db


molecules_json_file = os.path.join(
    pathlib.Path(__file__).parent.resolve(),
    "molecules.json"
)


class Molecule(Base):

    __tablename__ = "molecules"
    id = Column(Integer, primary_key=True, nullable=False)
    cas = Column(String, nullable=False)
    cid = Column(String, nullable=False)
    iupac_name = Column(String, nullable=False)
    canonical_smiles = Column(String, nullable=False)
    isomeric_smiles = Column(String, nullable=False)
    inchi = Column(String, nullable=False)
    inchikey = Column(String, nullable=False)
    molecular_formula = Column(String, nullable=False)
    compound_groups = Column(PickleType, nullable=False, default=[])
    properties = Column(JSON, nullable=False, default={})


def populate_database() -> None:

    with open(molecules_json_file, "r") as jfile:
        content = json.load(jfile)
    jfile.close()
    db = next(get_db())
    for molecule in content:
        if db.query(Molecule).filter_by(cas=molecule["cas"]).first() is None:
            mol = Molecule(
                cas=molecule["cas"],
                cid=molecule["cid"],
                iupac_name=molecule["iupac_name"],
                canonical_smiles=molecule["canonical_smiles"],
                isomeric_smiles=molecule["isomeric_smiles"],
                inchi=molecule["inchi"],
                inchikey=molecule["inchikey"],
                molecular_formula=molecule["molecular_formula"]
            )
            if molecule.get("compound_groups"):
                mol.compound_groups = molecule["compound_groups"]
            if molecule.get("properties"):
                mol.properties = molecule["properties"]
            db.add(mol)
            db.commit()
