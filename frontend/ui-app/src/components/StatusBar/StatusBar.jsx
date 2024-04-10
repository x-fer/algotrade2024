import { useContext, useEffect, useState } from "react";
import StatusBarItem from "./StatusBarItem";
import { DataContext } from "../DataProvider";

const StatusBar = () => {
  const { gameId, playerId, teamSecret } = useContext(DataContext);
  const [status, setStatus] = useState({});

  //TODO

  useEffect(() => {
    /* instance
      .get(`/game/${gameId}/player/${playerId}`, null, {
        params: { team_secret: teamSecret },
      })
      .then((response) => {
        setStatus(response.data);
      }); */
  }, []);

  return (
    <div className="flex justify-around p-4 rounded-3xl gap-6 bg-primary text-white shadow-xl">
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
