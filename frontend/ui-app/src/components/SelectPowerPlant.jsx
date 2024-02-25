import React from "react";

const SelectPowerPlant = ({ type }) => {
  return (
    <button className="bg-dark-gray text-white w-60 h-24 rounded-3xl">
      {type}
    </button>
  );
};

export default SelectPowerPlant;
