import axios from "axios";
import ENDPOINT from "../../constants";

const handleSubmit = (e) => {
  e.preventDefault();

  axios
    .get(`${ENDPOINT}/game/list`)
    .then((response) => {
      console.log(response.data);
    })
    .catch((error) => {
      console.log(error);
    });
};

const EnergySell = () => {
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
