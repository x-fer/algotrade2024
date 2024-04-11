import axios from "axios";
import { ENDPOINT } from "../../constants";
import { useContext } from "react";
import { DataContext } from "../DataProvider";

const EnergySell = () => {
  const { playerData } = useContext(DataContext);

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log(playerData);
  };

  return (
    <div className="bg-secondary rounded-3xl p-4">
      <h1>EnergySell</h1>
      <button className="" onClick={handleSubmit}>
        TEST
      </button>
    </div>
  );
};

export default EnergySell;
