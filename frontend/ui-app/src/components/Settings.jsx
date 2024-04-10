import React, { useContext } from "react";
import { DataContext } from "./DataProvider";

const Settings = () => {
  const {
    gameId,
    setGameId,
    playerId,
    setPlayerId,
    teamSecret,
    setTeamSecret,
  } = useContext(DataContext);

  return (
    <div className="flex flex-col mt-2 p-4 rounded-3xl bg-primary text-white">
      <div className="flex flex-col">
        <label className="font-l">Game Id</label>
        <input
          className="bg-secondary p-2 rounded-2xl mt-2"
          value={gameId}
          onChange={(e) => setGameId(e.target.value)}
        />
      </div>
      <div className="flex flex-col mt-2">
        <label className="font-l">Player Id</label>
        <input
          className="bg-secondary p-2 rounded-2xl mt-2"
          value={playerId}
          onChange={(e) => setPlayerId(e.target.value)}
        />
      </div>
      <div className="flex flex-col mt-2">
        <label className="font-l">Team Secret</label>
        <input
          className="bg-secondary p-2 rounded-2xl mt-2"
          value={teamSecret}
          onChange={(e) => setTeamSecret(e.target.value)}
        />
      </div>
    </div>
  );
};

export default Settings;
