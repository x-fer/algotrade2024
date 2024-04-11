import { createContext, useEffect, useState } from "react";
import {
  ENDPOINT,
  GRAPH_FETCH_INTERVAL,
  GRAPH_LAST_N,
  ORDERS_LIST_FETCH_INTERVAL,
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

  const [selectedResource, setSelectedResource] = useState(null);
  const [selectedPowerPlant, setSelectedPowerPlant] = useState(null);

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

    const ordersListTimerInterval = setInterval(() => {
      setOrdersListTimer((prev) => prev + 1);
    }, ORDERS_LIST_FETCH_INTERVAL);

    return () => {
      clearInterval(graphTimerInterval);
      clearInterval(playerTimerInterval);
      clearInterval(ordersListTimerInterval);
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

  function fetchOrdersListData() {
    if (!gameId || !playerId || !teamSecret) {
      return;
    }

    axios
      .get(`${ENDPOINT}/game/${gameId}/player/${playerId}/orders/`, {
        params: { team_secret: teamSecret },
      })
      .then((response) => {
        let ordersObject = response.data;

        let orders = [];

        for (let resource in ordersObject) {
          for (let side in ordersObject[resource]) {
            ordersObject[resource][side].forEach((order) => {
              orders.push({
                resource: resource,
                side: side,
                order_id: order.order_id,
                player_id: order.player_id,
                price: order.price,
                size: order.size,
                tick: order.tick,
                timestamp: order.timestamp,
                order_status: order.order_status,
                filled_size: order.filled_size,
                expiration_tick: order.expiration_tick,
              });
            });
          }
        }

        setOrdersListData(orders);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  useEffect(() => {
    fetchOrdersListData();
  }, [ordersListTimer]);

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
        ordersListData,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};

export default DataProvider;
