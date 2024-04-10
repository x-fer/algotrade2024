import React, { useState } from "react";
import "./App.css";
import DataProvider from "./components/DataProvider";
import PowerPlantsBox from "./components/PowerPlants/PowerPlantsBox";
import ResourcesBox from "./components/BuySell/ResourcesBox";
import StatusBar from "./components/StatusBar/StatusBar";

const App = () => {
  const [gameId, setGameId] = useState(0);
  const [playerId, setPlayerId] = useState(0);
  const [teamSecret, setTeamSecret] = useState("");

  return (
    <DataProvider>
      <div className="flex flex-col justify-between h-screen p-4 gap-4 bg-background w-screen">
        <div className="flex bg-background h-full w-full gap-4">
          <PowerPlantsBox />
          <ResourcesBox />
        </div>
        <StatusBar />
      </div>
    </DataProvider>
  );
};

export default App;
