const BuySell = ({ handleButtonClick, register }) => {
  return (
    <div className="grid grid-cols-2 bg-secondary rounded-3xl gap-4 p-4">
      <div className="flex flex-col items-start">
        <label className="font-l">Quantity:</label>
        <input
          className="bg-tertiary  p-2 rounded-2xl w-full"
          type="number"
          id="size"
          name="size"
          {...register("size", { required: true, min: 1 })}
        />
      </div>

      <div className="flex flex-col items-start">
        <label className="font-l">Price:</label>
        <input
          className="bg-tertiary  p-2 rounded-2xl w-full"
          type="number"
          id="price"
          name="price"
          {...register("price", { required: true, min: 1 })}
        />
      </div>

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
  );
};

export default BuySell;
