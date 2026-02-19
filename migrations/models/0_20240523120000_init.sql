-- upgrade --
CREATE TABLE IF NOT EXISTS "usersetting" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "stats" INT NOT NULL  DEFAULT 1,
    "first_places" INT NOT NULL  DEFAULT 0,
    "games_played" INT NOT NULL  DEFAULT 0,
    "cards_atack" INT NOT NULL  DEFAULT 0,
    "cards_beaten" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
