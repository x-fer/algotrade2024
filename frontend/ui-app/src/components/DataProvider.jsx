import { createContext, useEffect, useState } from "react";
import {
  ENDPOINT,
  GRAPH_FETCH_INTERVAL,
  GRAPH_LAST_N,
  PLAYER_FETCH_INTERVAL,
} from "../constants";
import axios from "axios";

export const DataContext = createContext();

const DataProvider = ({ children }) => {
  const [gameId, setGameId] = useState(localStorage.getItem("gameId") || "");
  const [playerId, setPlayerId] = useState(
    localStorage.getItem("playerId") || ""
  );
  const [teamSecret, setTeamSecret] = useState(
    localStorage.getItem("teamSecret") || ""
  );

  const [selectedResource, setSelectedResource] = useState("");
  const [selectedPowerPlant, setSelectedPowerPlant] = useState("");

  const [playerData, setPlayerData] = useState({});
  const [playerTimer, setPlayerTimer] = useState(0);

  const [graphData, setGraphData] = useState([]);
  const [graphTimer, setGraphTimer] = useState(0);

  const [ordersListData, setOrdersListData] = useState([]);
  const [ordersListTimer, setOrdersListTimer] = useState(0);

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
      })
      .catch((error) => {
        console.error(error);
      });
  }

  useEffect(() => {
    fetchPlayerData();
  }, [playerTimer]);

  function fetchGraphData() {
    if (!gameId || !playerId || !teamSecret) {
      return;
    }

    axios
      .get(`${ENDPOINT}/game/${gameId}/dataset/`, {
        params: {
          team_secret: teamSecret,
          start_tick: -GRAPH_LAST_N,
          end_tick: -1,
        },
      })
      .then((response) => {
        setGraphData(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  useEffect(() => {
    fetchGraphData();
  }, [graphTimer]);

  return (
    <DataContext.Provider
      value={{
        gameId,
        setGameId,
        playerId,
        setPlayerId,
        teamSecret,
        setTeamSecret,

        selectedResource,
        setSelectedResource,
        selectedPowerPlant,
        setSelectedPowerPlant,

        playerData,
        graphData,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export default DataProvider;
