# Teeny Weeny Analytics

Super small, privacy focused, analytics package. Currently no frontend, but... whatever.

What is the future of this project? IDK. I'll use it on a few personal sites and see how I like it. Maybe I'll make a frontend eventually, if I feel like it. For right now I'm going to stick with just querying the DB myself.


## Inspiration

This project was inspired by the following other minimally invasive, self-hosted, analytics packages:

- [matomo](https://matomo.org/)
- [fathom](https://usefathom.com)
- [simple analytics](https://simpleanalytics.io)

## Installation

1. Clone repo
2. Create virtualenv with python 3.7
3. Install django requirements `pip install -r backend/requirements.txt`
4. Add `local_settings.py` to `backend/backend` with the `SECRET_KEY` and `DEBUG` fields
5. Start server in your desired fashion (would suggest gunicorn)
6. Ensure any reverse proxy configurations allows `/assets/v1` to point to the `assets/dist` directory where `collect.js` prod version lives
