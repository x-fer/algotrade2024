const SelectFuelButton = ({ type, active, setSelectedFuel, image }) => {
  return (
    <button
      className={`bg-dark-gray hover:bg-gray text-white text-xl p-2 rounded-3xl border-2 ${
        active ? "border-red" : "border-black-gray"
      }`}
      onClick={() => setSelectedFuel(type)}
    >
      <img src={image} alt={type} width={40} height={40} />
    </button>
  );
};

export default SelectFuelButton;
