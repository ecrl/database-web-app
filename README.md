# ECRL's database/web-app

A comprehensive database of combustion properties for over 1000 compounds that can be run locally or in the cloud. All you need is Docker.

https://database.uml-ecrl.org/

## Installation

```
$ git clone https://github.com/ecrl/database-web-app
$ cd database-web-app
$ chmod +x /mongo/import.sh
$ docker compose up -d
```

After composing, the *ecrl-db-mongo-seed* container can be removed.

If containers are created locally, the web app is available at *http://localhost:8080*. For more complex applications I assume you know what you're doing.
