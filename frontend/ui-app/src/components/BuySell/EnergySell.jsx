const fetchData = async (e) => {
  e.preventDefault();

  try {
    const response = await fetch("http://86.32.73.226:3000/game/list");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const jsonData = await response.json();
    console.log(jsonData);
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};

const EnergySell = () => {
  return (
    <div className="bg-secondary rounded-3xl p-4">
      <h1>EnergySell</h1>
      <button className="" onClick={fetchData}>
        TEST
      </button>
    </div>
  );
};

export default EnergySell;
