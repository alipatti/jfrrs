# Database Format

## Top-level tables

### Leagues

- name
- id

### Teams

- id (pk)
- gender

### Athletes

- id (pk)
- gender (M | F)
- first name
- last name
- team (refs team.id)

### Meets

- id (pk)
- name (str)
- date (str)
- distance (number)
- venue (str)
- city (str)
- state (str)

### Results

- id (pk autoincrement)
- athlete (refs athletes.id)
- meet (refs meets.id)
- score (int)
- time (number)

## Junction tables

### Team-League

- team (refs teams.id)
- league (refs leagues.id)
- unique (team, league)

### Meet-Team

- meet (refs meets.id)
- team (refs teams.id)
- unique (meet, team)
