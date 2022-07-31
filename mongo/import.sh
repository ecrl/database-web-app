#! /bin/bash

mongoimport --host mongo --db ecrl-db --collection compounds --type json --file /mongo/compounds.json --jsonArray