// Graciously provided by Tillbaks:
// https://github.com/tillbaks
const net = require("net");
const WebSocket = require("ws");

const wss = new WebSocket.Server({port: 8080});

// Connects to a LEGACY client.
// STATS SERVER
const sessionScores = {};
let currentGame = {
  gameid: 0,
  score: 0,
  scoreTransition: 0,
  lines: 0,
  level: 0,
  tetris: 0,
  tetris_rate: 0,
  burns: 0,
};

const statsServer = net.createServer(function (socket) {
  socket.on("data", (data) => {
    try {
      const json = JSON.parse(data.toString());
      //console.log(json)
      if (json.score !== null && json.lines !== null && json.level !== null) {
        json.score = parseInt(json.score);
        json.lines = parseInt(json.lines);
        json.level = parseInt(json.level);

        // skip level below 9 starts (mostly cpu player)
        // and 0-scores (false starts?)
        //if (json.level < 9 || json.score === 0) return;

        if (currentGame.gameid === json.gameid) {
          // Current game update
          if (currentGame.score === json.score) return; // no need to update if score has not changed

          // Update tetrises
          const linesChange = json.lines - currentGame.lines;
          if (linesChange === 4) {
            currentGame.tetris += 1;
            currentGame.burns = 0;
          } else {
            currentGame.burns += linesChange;
          }

        } else {
          // New game started
          currentGame = {
            gameid: json.gameid,
            score: 0,
            scoreTransition: 0,
            lines: 0,
            level: 0,
            starting_level: json.level,
            tetris: 0,
            tetris_rate: 0,
            burns: 0,
          }
        }

        // Update tetris rate
        if (json.lines !== 0) {
          currentGame.tetris_rate = Math.round(
            ((currentGame.tetris * 4) / json.lines) * 100
          );
        }

        // Set transition score if lvl 18 => 19
        if (currentGame.level === 18 && json.level === 19) {
          currentGame.scoreTransition = json.score;
        }

        // Update game stats
        currentGame.score = json.score;
        currentGame.lines = json.lines;
        currentGame.level = json.level;
        currentGame.I = json.I;

        sessionScores[currentGame.gameid] = { ...currentGame };

        // Send everything to clients
        wss.clients.forEach((client) =>
          client.send(JSON.stringify({ sessionScores, currentGame }))
        );
      }
    } catch (e) {}
  });
});

statsServer.listen(3338, "127.0.0.1");