const BuySell = ({ handleButtonClick, register }) => {
  return (
    <div className="flex flex-col bg-secondary rounded-3xl gap-4 p-4">
      <div className="flex justify-between items-end gap-4">
        <div className="flex flex-col items-start">
          <label className="font-l">Quantity:</label>
          <input
            className="bg-tertiary  p-2 rounded-2xl w-[16vw]"
            type="number"
            id="size"
            name="size"
            {...register("size", { required: true, min: 1 })}
          />
        </div>

        <div className="flex flex-col items-start">
          <label className="font-l">Price:</label>
          <input
            className="bg-tertiary  p-2 rounded-2xl w-[16vw]"
            type="number"
            id="price"
            name="price"
            {...register("price", { required: true, min: 1 })}
          />
        </div>
      </div>

      <div className="flex  justify-around gap-4">
        <div className="flex justify-around font-bold">
          <button
            className="bg-green py-2 px-4 rounded-2xl active:bg-darkgreen"
            type="button"
            onClick={() => handleButtonClick("buy")}
          >
            BUY
          </button>
        </div>

        <div className="flex justify-around font-bold">
          <button
            className="bg-red py-2 px-4 rounded-2xl active:bg-darkred"
            type="button"
            onClick={() => handleButtonClick("sell")}
          >
            SELL
          </button>
        </div>
      </div>
    </div>
  );
};

export default BuySell;
