const BuySell = ({ quantity, setQuantity }) => {
  return (
    <form className="flex flex-col text-white">
      <div>
        <input type="number" value={quantity} min={1} max={5000} />
      </div>
      <div className="flex justify-around">
        <button>BUY</button>
        <button>SELL</button>
      </div>
    </form>
  );
};

export default BuySell;
