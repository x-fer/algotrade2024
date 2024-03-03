import React, { useContext } from "react";
import { Context } from "../Context";

const Settings = () => {
  const {
    gameId,
    setGameId,
    playerId,
    setPlayerId,
    teamSecret,
    setTeamSecret,
  } = useContext(Context);

  return (
    <div className="flex flex-col text-white mt-12">
      <div className="flex flex-col">
        <label className="font-l">Game Id</label>
        <input
          className="bg-gray p-2 rounded-xl mt-2"
          value={gameId}
          onChange={(e) => setGameId(e.target.value)}
        />
      </div>
      <div className="flex flex-col mt-2">
        <label className="font-l">Player Id</label>
        <input
          className="bg-gray p-2 rounded-xl mt-2"
          value={playerId}
          onChange={(e) => setPlayerId(e.target.value)}
        />
      </div>
      <div className="flex flex-col mt-2">
        <label className="font-l">Team Secret</label>
        <input
          className="bg-gray p-2 rounded-xl mt-2"
          value={teamSecret}
          onChange={(e) => setTeamSecret(e.target.value)}
        />
      </div>
    </div>
  );
};

export default Settings;
