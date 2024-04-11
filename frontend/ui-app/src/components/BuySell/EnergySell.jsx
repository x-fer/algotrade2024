import axios from "axios";
import { ENDPOINT } from "../../constants";
import { useContext } from "react";
import { DataContext } from "../DataProvider";

const EnergySell = () => {
  const { playerData } = useContext(DataContext);

  const handleSubmit = (e) => {
    e.preventDefault();
    /* axios
      .get(`${ENDPOINT}/game/${gameId}/player/${playerId}/`, {
        params: { team_secret: teamSecret },
      })
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      }); */

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
