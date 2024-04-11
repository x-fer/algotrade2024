import { createContext, useEffect, useState } from "react";
import {
  ENDPOINT,
  GRAPH_FETCH_INTERVAL,
  PLAYER_FETCH_INTERVAL,
} from "../constants";
import axios from "axios";
import { set } from "react-hook-form";

export const DataContext = createContext();

const DataProvider = ({ children }) => {
  const [gameId, setGameId] = useState(localStorage.getItem("gameId") || "");
  const [playerId, setPlayerId] = useState(
    localStorage.getItem("playerId") || ""
  );
  const [teamSecret, setTeamSecret] = useState(
    localStorage.getItem("teamSecret") || ""
  );

  const [playerData, setPlayerData] = useState({});
  const [playerTimer, setPlayerTimer] = useState(0);

  const [graphData, setGraphData] = useState([]);
  const [graphTimer, setGraphTimer] = useState(0);

  useEffect(() => {
    const graphTimerInterval = setInterval(() => {
      setGraphTimer((prev) => prev + 1);
    }, GRAPH_FETCH_INTERVAL);

    const playerTimerInterval = setInterval(() => {
      setPlayerTimer((prev) => prev + 1);
    }, PLAYER_FETCH_INTERVAL);

    return () => {
      clearInterval(graphTimerInterval);
      clearInterval(playerTimerInterval);
    };
  }, []);

  useEffect(() => {
    localStorage.setItem("gameId", gameId);
    localStorage.setItem("playerId", playerId);
    localStorage.setItem("teamSecret", teamSecret);
  }, [gameId, playerId, teamSecret]);

  function fetchPlayerData() {
    if (!gameId || !playerId || !teamSecret) {
      return;
    }

    axios
      .get(`${ENDPOINT}/game/${gameId}/player/${playerId}/`, {
        params: { team_secret: teamSecret },
      })
      .then((response) => {
        setPlayerData(response.data);
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  useEffect(() => {
    fetchPlayerData();
  }, [playerTimer]);

  return (
    <DataContext.Provider
      value={{
        gameId,
        setGameId,
        playerId,
        setPlayerId,
        teamSecret,
        setTeamSecret,

        playerData,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export default DataProvider;
