import React from "react";

const BuySell = ({ quantity, setQuantity }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(quantity);
  };

  const handleChange = (e) => {
    setQuantity(e.target.value);
  };

  return (
    <form className="text-white" onSubmit={handleSubmit}>
      <input
        className="bg-dark-gray mx-2 mt-8 p-2 rounded-xl w-16"
        type="number"
        value={quantity}
        onChange={handleChange}
      />
      <div className="flex justify-around mt-4 font-bold">
        <button className="bg-green p-2 rounded-xl" type="submit">
          BUY
        </button>
        <button className="bg-red p-2 rounded-xl" type="submit">
          SELL
        </button>
      </div>
    </form>
  );
};

export default BuySell;
