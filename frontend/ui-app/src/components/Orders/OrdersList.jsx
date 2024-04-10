import axios from "axios";
import React, { useContext, useEffect, useState } from "react";
import { DataContext } from "../DataProvider";
import instance from "../../api/apiInstance";

const OrdersListItem = ({ order }) => {
  const { teamSecret, gameId, playerId } = useContext(DataContext);

  const handleCancel = (order_id) => {
    instance
      .post(
        `/game/${gameId}/player/${playerId}/orders/cancel`,
        { ids: [order_id] },
        {
          params: { team_secret: teamSecret },
        }
      )
      .then((response) => {
        console.log(response);
      });
  };

  return (
    <div className="flex justify-between items-center p-2 rounded-3xl bg-secondary text-white shadow-xl">
      <div className="flex justify-between  ml-2">
        <p>
          {order.quantity} {order.name} at {order.price}&nbsp; [{order.side[0]}]
        </p>
      </div>
      <div className="flex justify-around font-bold h-[5vh]">
        <button
          className="bg-red py-2 px-4 rounded-2xl active:bg-darkred"
          type="button"
          onClick={() => handleCancel(order.id)}
        >
          CANCEL
        </button>
      </div>
    </div>
  );
};

const OrdersList = () => {
  const [ordersList, setOrdersList] = useState([
    { order_id: 1, resource: "COAL", size: 10, price: 20, side: "BUY" },
    { order_id: 2, resource: "BIOMASS", size: 50, price: 10, side: "SELL" },
    { order_id: 3, resource: "GAS", size: 90, price: 15, side: "BUY" },
  ]);

  useEffect(() => {
    axios.get("http://localhost:3001/orders").then((response) => {
      setOrdersList(response.data);
    });
  }, []);

  return (
    <div className="flex flex-col py-4 h-full gap-4 rounded-3xl bg-primary">
      <div className="text-white">
        <h2>My orders</h2>
      </div>

      <div className="flex flex-col h-full p-4  gap-4 rounded-3xl  ">
        {ordersList.map((order) => (
          <OrdersListItem
            key={order.order_id}
            order={{
              id: order.order_id,
              name: order.resource,
              quantity: order.size,
              price: order.price,
              side: order.side,
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default OrdersList;
