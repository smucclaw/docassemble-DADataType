#pred game(X) :: '@(X) is a game of rock, paper, scissors'.
#pred player(X) :: '@(X) is a player'.
#pred participant_in(X,Y) :: '@(X) is a participant in @(Y)'.
#pred sign(X) :: '@(X) is a sign'.
#pred beats(X,Y) :: '@(X) beats @(Y)'.
#pred player_throw(X,Y) :: '@(X) throws @(Y)'.
#pred winner(X,Y) :: 'in accordance with {TechShow 2021 Rock Paper Scissors Act s 4}, @(X) is the winner of @(Y)'.

sign(rock).
sign(paper).
sign(scissors).
beats(rock,scissors).
beats(scissors,paper).
beats(paper,rock).

winner(Player1,Game) :-
    game(Game),
    participant_in(Player1,Game),
    player(Player1),
    player_throw(Player1,Throw1),
    player(Player2),
    participant_in(Player2,Game),
    player_throw(Player2,Throw2),
    beats(Throw1,Throw2),
    Player1 \= Player2.