import { useContext } from "react";
import { DataContext } from "../DataProvider";

const PowerPlantInfo = () => {
  const { selectedPowerPlant, playerData } = useContext(DataContext);

  return (
    <div className="bg-secondary text-white rounded-3xl p-4 w-[18vw]">
      {selectedPowerPlant ? (
        <>
          <h1>{selectedPowerPlant?.name} Power Plant </h1>
          <p>
            Power plants owned:{" "}
            {playerData.power_plants_owned[selectedPowerPlant.key]}
          </p>
          <p>
            Power plants powered:{" "}
            {playerData.power_plants_powered[selectedPowerPlant.key]}
          </p>
        </>
      ) : (
        <h1>Select a Power Plant</h1>
      )}
    </div>
  );
};

export default PowerPlantInfo;
