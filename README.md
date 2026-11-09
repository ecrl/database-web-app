[![UML Energy & Combustion Research Laboratory](https://sites.uml.edu/hunter-mack/files/2021/11/ECRL_final.png)](http://faculty.uml.edu/Hunter_Mack/)

# ECRL's database/web-app

A comprehensive database of combustion properties for over 1,200 compounds that can be run locally or in the cloud. All you need is Docker.

https://database.uml-ecrl.org/

## Run it

```bash
docker compose up -d --build
```

The app listens on port 8000. By default it stores the molecules in SQLite
inside the container, loaded from `src/db/molecules.json` at startup. A `.env`
file is optional (`SECRET_KEY`, `DATABASE_URL`).

To run it on Postgres instead, put `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_EXT_PORT` and `DATABASE_URL=postgresql://USER:PASSWORD@db:5432/postgres`
in `.env`, then:

```bash
docker compose --profile postgres up -d --build
```

Needs Docker Compose 2.20 or newer.
