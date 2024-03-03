import React, { useEffect } from "react";

const OrdersListItem = ({ order }) => {
  return (
    <div className="flex justify-between items-center bg-gray my-2 p-1.5 rounded-xl">
      <div className="flex justify-between text-white ml-2">
        <p>
          {order.name}:&nbsp;{order.quantity}
        </p>
      </div>
      <div className="flex justify-around font-bold h-12">
        <button className="bg-red py-2 px-4 rounded-xl" type="submit">
          CANCEL
        </button>
      </div>
    </div>
  );
};

const OrdersList = ({ orders }) => {
  useEffect(() => {
    console.log(orders);
  });

  return (
    <div>
      {orders.map((order) => (
        <OrdersListItem
          key={order.id}
          order={{ name: "Coal", quantity: "123" }}
        />
      ))}
    </div>
  );
};

export default OrdersList;
