import { useContext } from "react";
import { DataContext } from "../DataProvider";

const BuySell = ({ handleButtonClick, register }) => {
  const { selectedResource } = useContext(DataContext);

  return (
    <div className=" bg-secondary rounded-3xl p-4">
      <p className="text-xl">{selectedResource?.name}</p>

      <div className="grid grid-cols-3 gap-4 mx-4">
        <div className="flex flex-col items-start">
          <label className="font-l">Quantity:</label>
          <input
            className="bg-primary  p-2 rounded-2xl w-full mt-2"
            type="number"
            id="size"
            name="size"
            {...register("size", { required: true, min: 1 })}
          />
        </div>

        <div className="flex flex-col items-start">
          <label className="font-l">Price:</label>
          <input
            className="bg-primary  p-2 rounded-2xl w-full mt-2"
            type="number"
            id="price"
            name="price"
            {...register("price", { required: true, min: 1 })}
          />
        </div>

        <div className="flex flex-col items-start">
          <label className="font-l">Valid for (ticks):</label>
          <input
            className="bg-primary  p-2 rounded-2xl w-full mt-2"
            type="number"
            id="expiration_length"
            name="expiration_length"
            {...register("expiration_length", { required: true, min: 1 })}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 m-4">
        <button
          className="bg-green py-2 px-4 rounded-2xl font-bold active:bg-darkgreen"
          type="button"
          onClick={() => handleButtonClick("buy")}
        >
          BUY
        </button>

        <button
          className="bg-red py-2 px-4 rounded-2xl font-bold active:bg-darkred"
          type="button"
          onClick={() => handleButtonClick("sell")}
        >
          SELL
        </button>
      </div>
    </div>
  );
};

export default BuySell;
