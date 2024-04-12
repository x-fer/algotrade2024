import { useContext } from "react";
import { DataContext } from "../DataProvider";
import axios from "axios";
import { ENDPOINT } from "../../constants";
import PowerPlantTurnOn from "./PowerPlantTurnOn";

const PowerPlantInfoBox = () => {
  const { selectedPowerPlant, playerData, gameId, playerId, teamSecret } =
    useContext(DataContext);

  const handeBuy = () => {
    axios.post(
      `${ENDPOINT}/game/${gameId}/player/${playerId}/plant/buy`,
      { type: selectedPowerPlant.key },
      {
        params: { team_secret: teamSecret },
      }
    );

    console.log("buy " + selectedPowerPlant.key);
  };

  const handeSell = () => {
    axios.post(
      `${ENDPOINT}/game/${gameId}/player/${playerId}/plant/sell`,
      { type: selectedPowerPlant.key },
      {
        params: { team_secret: teamSecret },
      }
    );

    console.log("sell " + selectedPowerPlant.key);
  };

  return (
    <div className=" text-white p-4">
      <p className="text-xl mb-16">{selectedPowerPlant?.name} Power Plant </p>

      <div className="flex items-start">
        <p>
          Power plants owned:{" "}
          {playerData.power_plants_owned[selectedPowerPlant.key]}
        </p>
        <p>
          Power plants powered:{" "}
          {playerData.power_plants_powered[selectedPowerPlant.key]}
        </p>
      </div>

      <div className="flex items-start justify-around mt-8">
        <button
          className="bg-green py-2 px-4 rounded-2xl font-bold active:bg-darkgreen"
          onClick={() => handeBuy(selectedPowerPlant.key)}
        >
          Buy
        </button>
        <button
          className="bg-red py-2 px-4 rounded-2xl font-bold active:bg-darkred ml-4"
          onClick={() => handeSell(selectedPowerPlant.key)}
        >
          Sell
        </button>
      </div>

      <div className="flex items-start mt-8">
        <PowerPlantTurnOn />
      </div>
    </div>
  );
};

const PowerPlantInfo = () => {
  const { selectedPowerPlant, playerData } = useContext(DataContext);

  return (
    <div className="bg-secondary text-white rounded-3xl p-4 w-[18vw]">
      {selectedPowerPlant ? (
        <PowerPlantInfoBox />
      ) : (
        <h1>Select a Power Plant</h1>
      )}
    </div>
  );
};

export default PowerPlantInfo;
