#C4 4 PG

A small connect four implementation for PlanGrid.

![Image of C4](http://i.imgur.com/266Fi1h.png)

A first visit requires a user to set a user name. Once a name is set, a user is permitted to browse existing connect four games or create their own. Upon creating their own, other users may join it or they may send the link to a friend. Games are played with users taking opposite turns dropping a chip into a column. When four chips of one kind are placed in a row, column, or diagonal, the game ends, a winner is declared, and the users are redirected to the game lobby.

##Features

- Users determined by session
- Users identified by user name
- Users may create connect four games
- Connect four games are displayed along with their hosts
- The creator of a game may delete it
- Game board updates in realtime
- Game board displayed with CSS3 rounded tokens
- Turn based gameplay
- Vertical, horizontal, and diagonal scoring
- Win detection and automatic game deletion
- Share a game by simply copying its link
- Users spectate a game by joining 3rd

##Stack
- jQuery
- Flask
- MongoDB
- Redis

##Deployment

Ensure to have both Redis and MongoDB running on default settings.

```shell
pip install -r requirements.txt
python server.py
```

##Testing
```shell
nosetests <path>
nosetests tests/test_board.py
```

##TODO
- Scoring sytem and player history
- Match making