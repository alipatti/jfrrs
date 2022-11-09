# JFRRS

Jeff's Fantasy Running Race System

## TODO

- [ ] port scraper to typescript (I don't think this is actually as much work as it seems at first)

- Dockerize
  - Next server
    - Uses prisma to interact with the database
  - Scraper
    - Python docker image
    - runs at specified interval and sends data directly to server
    - doesn't interact with frontend at all
- Finish scraper
- Built frontend
  - Create landing page for a team
    - Users can set their starting 7
    -

## Known issues

You may need to run `export ARCHFLAGS="-arch x86_64"` before installing python dependencies.
This fixes a build error with lxml (don't ask me how...).
