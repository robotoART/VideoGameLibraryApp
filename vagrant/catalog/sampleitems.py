from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import GameMachine, VideoGame, Base, User

engine = create_engine('sqlite:///videogamelibrary.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create sample user
User1 = User(name="Robo Gamer", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Library for Nintendo NES
game_machine1 = GameMachine(user_id=1, name="NES", manufacturer="Nintendo")

session.add(game_machine1)
session.commit()

videogame2 = VideoGame(user_id=1, name="Super Mario Bros. 2",
                     description="The bros pickup objects now!",
                     game_machine=game_machine1)


session.add(videogame2)
session.commit()

videogame1 = VideoGame(user_id=1, name="Little Nemo's Dream Land",
                     description="Dreamy adventure side scroller",
                     game_machine=game_machine1)

session.add(videogame1)
session.commit()

videogame2 = VideoGame(user_id=1, name="Mighty Bomb Jack",
                     description="Exciting adventure",
                     game_machine=game_machine1)

session.add(videogame2)
session.commit()

videogame3 = VideoGame(user_id=1, name="Mega Man 3",
                     description="He slides and there's Protoman.",
                     game_machine=game_machine1)

session.add(videogame3)
session.commit()

videogame4 = VideoGame(user_id=1, name="Super Mario Bros.",
                     description="Mama mia! it's the USA original.",
                     game_machine=game_machine1)

session.add(videogame4)
session.commit()

videogame5 = VideoGame(user_id=1, name="Super Mario Bros. 3",
                     description="The bros can fly and more!",
                     game_machine=game_machine1)

session.add(videogame5)
session.commit()

videogame6 = VideoGame(user_id=1, name="Captain Skyhawk",
                     description="Fighter jet shooter.",
                     game_machine=game_machine1)

session.add(videogame6)
session.commit()

videogame7 = VideoGame(user_id=1, name="Marble Madness",
                     description="Obstacle filled maze races.",
                     game_machine=game_machine1)

session.add(videogame7)
session.commit()

videogame8 = VideoGame(user_id=1, name="Bubble Bobble",
                     description="Single screen levels, pop bubbled monsters, play alone or with a friend",
                     game_machine=game_machine1)
session.add(videogame8)
session.commit()


# Library for Sony Playstation 3
game_machine2 = GameMachine(user_id=1, name="Playstation 3", manufacturer="Sony")
session.add(game_machine2)
session.commit()

videogame1 = VideoGame(user_id=1, name="Fifa 2015",
                     description="EA sports soccer Messi on cover.",
                     game_machine=game_machine2)
session.add(videogame1)
session.commit()

videogame2 = VideoGame(user_id=1, name="Gran Turismo GT",
                     description="Top physics realistic car racing.",
                     game_machine=game_machine2)
session.add(videogame2)
session.commit()

videogame3 = VideoGame(user_id=1, name="Little Big Planet",
                     description="Kid's adventure puzzle solving.",
                     game_machine=game_machine2)
session.add(videogame3)
session.commit()


# Library for Microsoft Xbox
game_machine3 = GameMachine(user_id=1, name="Xbox", manufacturer="Microsoft")
session.add(game_machine3)
session.commit()

videogame1 = VideoGame(user_id=1, name="Fifa 2007",
                     description="EA sports soccer during Ronaldinho era.",
                     game_machine=game_machine3)
session.add(videogame1)
session.commit()

videogame2 = VideoGame(user_id=1, name="Project Gotham 2",
                     description="Physics realistic car racing.",
                     game_machine=game_machine3)
session.add(videogame2)
session.commit()

videogame3 = VideoGame(user_id=1, name="Star Wars Battlefront 2",
                     description="First person shooter & strategy.",
                     game_machine=game_machine3)
session.add(videogame3)
session.commit()


print "added sample video game library items!"