import React, { useState } from 'react';

// Define the enum types
const PowerPlantType = {
  SOLAR: 'solar',
  WIND: 'wind',
  HYDRO: 'hydro',
};

const SelectPowerPlantButton = () => {

  const handleSelectType = (type) => {
    setSelectedType(type);
  };

  return (
    <div>
      <button onClick={() => handleSelectType(PowerPlantType.SOLAR)}>Solar</button>
    </div>
  );
};

export default SelectPowerPlantButton;
