"""Seed data for the arcade games catalogue."""

GAMES = [
    {
        "slug": "super-mario-bros",
        "title": "Super Mario Bros.",
        "year": 1985,
        "publisher": "Nintendo",
        "cover_art_path": "covers/super-mario-bros.png",
    },
    {
        "slug": "the-legend-of-zelda",
        "title": "The Legend of Zelda",
        "year": 1986,
        "publisher": "Nintendo",
        "cover_art_path": "covers/the-legend-of-zelda.png",
    },
    {
        "slug": "metroid",
        "title": "Metroid",
        "year": 1986,
        "publisher": "Nintendo",
        "cover_art_path": "covers/metroid.png",
    },
    {
        "slug": "mega-man-2",
        "title": "Mega Man 2",
        "year": 1988,
        "publisher": "Capcom",
        "cover_art_path": "covers/mega-man-2.png",
    },
    {
        "slug": "contra",
        "title": "Contra",
        "year": 1987,
        "publisher": "Konami",
        "cover_art_path": "covers/contra.png",
    },
    {
        "slug": "castlevania",
        "title": "Castlevania",
        "year": 1986,
        "publisher": "Konami",
        "cover_art_path": "covers/castlevania.png",
    },
    {
        "slug": "punch-out",
        "title": "Punch-Out!!",
        "year": 1987,
        "publisher": "Nintendo",
        "cover_art_path": "covers/punch-out.png",
    },
    {
        "slug": "tetris",
        "title": "Tetris",
        "year": 1989,
        "publisher": "Nintendo",
        "cover_art_path": "covers/tetris.png",
    },
    {
        "slug": "duck-hunt",
        "title": "Duck Hunt",
        "year": 1984,
        "publisher": "Nintendo",
        "cover_art_path": "covers/duck-hunt.png",
    },
    {
        "slug": "kid-icarus",
        "title": "Kid Icarus",
        "year": 1986,
        "publisher": "Nintendo",
        "cover_art_path": "covers/kid-icarus.png",
    },
]


def seed_games(db) -> None:
    """Insert seed games if the table is empty. Idempotent."""
    from app.models import Game

    if db.query(Game).count() == 0:
        db.add_all([Game(**g) for g in GAMES])
        db.commit()
