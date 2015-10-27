var gameOverTimeout = 4000;

// This function toggles whether a user can drop tokens on the
// board. Toggle is a boolean that if set to true enables and if
// set to false disables a user's ability to play.
function toggleTurn(toggle){
  $('button[name=move_location]').prop('disabled', !toggle);
}

// This function updates the visible game (status, board)
// and expects the data to be a json object with
// board (6x7 array), host_turn (bool), and winner (string)
function updateGame(data) {
  if (data['active']) {
    // Update the game board
    board = data['board'];
    str = "<table class='board'>";
    for (var row = 0; row < board.length; row++) {
      str += "<tr class='game-rows'>";
      for (var col = 0; col < board[row].length; col++) {
        str += "<td class='";
        if (board[row][col] == 'host') {
          str += 'blue';
        }
        else if (board[row][col] == 'challenger') {
          str += 'red';
        }
        str += "'><div class='token'></div></td>";
      }
      str += "</tr>";
    }
    str += "</table>"
    $('.board').replaceWith(str);

    // Update the move selectors
    var hostTurn = data['host_turn'];
    var isHost = $('div#game').hasClass('host');
    if (hostTurn) {
      $('#status').html(data['host_name'] + "'s turn");
      toggleTurn(!$('div#game').hasClass('challenger'));
    }
    else {
      $('#status').html(data['challenger_name'] + "'s turn");
      toggleTurn(!isHost);
    }

    // Update the status bar
    var winner = data['winner'];
    if (winner != 0) {
      if (winner == 'host') {
        $('#status').html(data['host_name'] + " wins!");
      }
      else {
        $('#status').html(data['challenger_name'] + " wins!");
      }
      toggleTurn(false);
      // Stop updating the board
      clearInterval(updateInterval);
      // If we are the host, delete the game. Otherwise just redirect to games list
      indexPage = window.location.pathname.split('/').slice(0,-2).join('/');
      $.post(window.location + '/joint_delete', function(data) {});
      setTimeout(function() {
        window.location = indexPage;
      }, gameOverTimeout);
    }
  }
}