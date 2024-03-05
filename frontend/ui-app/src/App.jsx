import React, { useState } from "react";
import "./App.css";
import LeftBar from "./components/LeftBar";
import MiddleScreen from "./components/MiddleScreen";
import RightBar from "./components/RightBar";
import { Context } from "./Context";

const App = () => {
  const [gameId, setGameId] = useState(0);
  const [playerId, setPlayerId] = useState(0);
  const [teamSecret, setTeamSecret] = useState("");

  return (
    <Context.Provider
      value={{
        gameId,
        setGameId,
        playerId,
        setPlayerId,
        teamSecret,
        setTeamSecret,
      }}
    >
      <div className="flex justify-between h-screen p-4 bg-background w-screen">
        <LeftBar />
        <MiddleScreen />
        <RightBar />
      </div>
    </Context.Provider>
  );
};

export default App;
