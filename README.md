[![UML Energy & Combustion Research Laboratory](https://sites.uml.edu/hunter-mack/files/2021/11/ECRL_final.png)](http://faculty.uml.edu/Hunter_Mack/)

# ECRL's database/web-app

A comprehensive database of combustion properties for over 1,200 compounds that can be run locally or in the cloud. All you need is Docker.

https://database.uml-ecrl.org/

## Installation

```
$ git clone https://github.com/ecrl/database-web-app
$ cd database-web-app
$ chmod +x /mongo/import.sh
$ docker compose up -d
```

After composing, the *ecrl-db-mongo-seed* container can be removed.

If containers are created locally, the web app is available at *http://localhost:8080* and the MongoDB server is available at *mongodb://localhost:27017*. For more complex deployments I assume you know what you're doing.
