telegram-likes-and-reviews-bot
===========
#### Simple bot for Telegram. Registers the user and adds his information to the database. The user can leave reviews about other users and rate them.

In the environment variables, you need to set the bot API token

`TELEGRAM_API_TOKEN` — Bot token API

Usage with Docker is shown below. Pre-fill the ENV variable mentioned above in the Dockerfile, and also in the start command specify the local directory with the project instead of `local_project_path`. The SQLite database will be located in the project folder `db/reviews.db`.

```
docker build -t telegram-likes-and-reviews-bot ./
docker run -d --name tg -v /local_project_path/db:/home/db telegram-likes-and-reviews-bot
```

To enter a running container:

```
docker exec -ti tg bash
```

Enter the container in the SQL shell:

```
docker exec -ti tg bash
sqlite3 /home/db/reviews.db
```

#### If you like my work you can support me on Buy Me a Coffee or Patreon.

[<img src="http://webgrimes.com/buymeacoffee.svg" height="40px">](https://www.buymeacoffee.com/shotariya)
[<img src="http://webgrimes.com/patreon.png" height="40px">](https://www.patreon.com/join/shotariya?)

Links
===========
[![](http://webgrimes.com/discord.svg) shotariya#4269](https://discordapp.com/users/275608234595713024)