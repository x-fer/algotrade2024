import { useContext, useEffect, useState } from "react";
import StatusBarItem from "./StatusBarItem";
import instance from "../api/apiInstance";
import { Context } from "../Context";

const StatusBar = () => {
  const { gameId, playerId, teamSecret } = useContext(Context);
  const [status, setStatus] = useState({});

  useEffect(() => {
    instance
      .get(`/game/${gameId}/player/${playerId}`, null, {
        params: { team_secret: teamSecret },
      })
      .then((response) => {
        setStatus(response.data);
      });
  });

  // TODO add settings if gameId, playerId, teamSecret are not set

  return (
    <div className="flex justify-around p-4 rounded-3xl bg-primary text-white gap-4">
      <StatusBarItem ammount={10230} unit="€" />
      <StatusBarItem ammount={230} unit="biomass" />
      <StatusBarItem ammount={870} unit="coal" />
      <StatusBarItem ammount={433} unit="gas" />
      <StatusBarItem ammount={40} unit="oil" />
      <StatusBarItem ammount={2} unit="uranium" />
    </div>
  );
};

export default StatusBar;
