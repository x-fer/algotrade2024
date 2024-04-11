import axios from "axios";
import { ENDPOINT } from "../../constants";
import { useContext } from "react";
import { DataContext } from "../DataProvider";
import { useForm } from "react-hook-form";

const EnergySell = ({ register, handleButtonClick }) => {
  const { gameId, playerId, teamSecret, playerData } = useContext(DataContext);

  return (
    <div className="bg-secondary rounded-3xl px-8 pb-8 pt-4">
      <p className="text-xl mb-4">Energy</p>

      <div className="flex items-start">
        <label className="text-l">
          Current sell price: {playerData.energy_price} €
        </label>
      </div>

      <div className="flex flex-col items-start mt-4">
        <label className="font-l">Set sell price:</label>
        <div className="flex items-center">
          <input
            className="bg-tertiary  p-2 rounded-2xl w-[15vw] mt-2"
            type="number"
            id="energy_price"
            name="energy_price"
            {...register("energy_price", { required: true, min: 1 })}
          />

          <button
            className="bg-green py-2 px-4 rounded-2xl font-bold active:bg-darkgreen ml-4 mt-2"
            onClick={(e) => {
              e.preventDefault();
              handleButtonClick("set");
            }}
          >
            SET
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnergySell;
