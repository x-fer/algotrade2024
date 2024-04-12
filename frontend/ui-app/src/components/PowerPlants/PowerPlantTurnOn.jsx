import { useContext, useState } from "react";
import { DataContext } from "../DataProvider";
import { useForm } from "react-hook-form";
import { ENDPOINT } from "../../constants";
import axios from "axios";

const PowerPlantTurnOn = () => {
  const { gameId, playerId, teamSecret, selectedPowerPlant } =
    useContext(DataContext);
  const [powerOn, setPowerOn] = useState(0);

  const handleSet = () => {
    axios
      .post(
        `${ENDPOINT}/game/${gameId}/player/${playerId}/plant/on`,
        {
          type: selectedPowerPlant.key,
          number: powerOn,
        },
        {
          params: { team_secret: teamSecret },
        }
      )
      .then((response) => {
        console.log(response.data);
      });

    console.log("set power " + selectedPowerPlant.key + " " + powerOn);
  };

  return (
    <form>
      <div className="flex flex-col justify-start">
        <label className="font-l">Set power plants running:</label>
        <div className="flex justify-start">
          <input
            className="bg-primary  p-2 rounded-2xl w-[10vw] mt-2"
            type="number"
            id="turnOn"
            name="turnOn"
            value={powerOn}
            onChange={(event) => setPowerOn(event.target.value)}
          />

          <button
            className="bg-green py-2 px-4 rounded-2xl font-bold active:bg-darkgreen ml-4 mt-2"
            onClick={(e) => {
              e.preventDefault();
              handleSet();
            }}
          >
            SET
          </button>
        </div>
      </div>
    </form>
  );
};

export default PowerPlantTurnOn;
