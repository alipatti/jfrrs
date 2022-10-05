# JFRRS

Jeff's Fantasy Running Race System

## TODO

- Dockerize
  - Next server
    - Uses prisma to interact with the database
  - Scraper
    - Python docker image
    - runs at specified interval and sends data directly to server
    - doesn't interact with frontend at all
  - Database
    - MySQL
    - interacts with frontend via prisma
- Finish scraper
- Built frontend
  - Create landing page for a team
    - Users can set their starting 7
    - 


## Known issues:

Run `export ARCHFLAGS="-arch x86_64"` before installing python dependencies.
This fixes a build error with lxml (don't ask me how...).
