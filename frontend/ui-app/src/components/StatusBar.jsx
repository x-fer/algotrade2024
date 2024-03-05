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
      <StatusBarItem ammount={status.money} unit="€" />
      <StatusBarItem ammount={status.biomass} unit="biomass" />
      <StatusBarItem ammount={status.coal} unit="coal" />
      <StatusBarItem ammount={status.gas} unit="gas" />
      <StatusBarItem ammount={status.oil} unit="oil" />
      <StatusBarItem ammount={status.uranium} unit="uranium" />
    </div>
  );
};

export default StatusBar;
