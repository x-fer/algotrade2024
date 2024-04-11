import axios from "axios";
import React, { useContext, useState } from "react";
import { DataContext } from "../DataProvider";
import { ENDPOINT } from "../../constants";

const OrdersListItem = ({ order }) => {
  const { teamSecret, gameId, playerId } = useContext(DataContext);

  console.log("CANCEL ORDER: " + order.order_id + " " + order.order_status);

  const handleCancel = (order_id) => {
    axios
      .get(
        `${ENDPOINT}/game/${gameId}/player/${playerId}/orders/${order_id}/cancel`,
        { params: { team_secret: teamSecret } }
      )
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <div className="flex justify-between items-center p-2 mb-4 rounded-3xl bg-secondary text-white shadow-xl">
      <div className="flex justify-between  ml-2">
        <p>
          {order.size} {order.resource} at {order.price}&nbsp; [{order.side[0]}]
        </p>
      </div>
      <div className="flex justify-around font-bold h-[5vh]">
        <button
          className="bg-red py-2 px-4 rounded-2xl active:bg-darkred"
          type="button"
          onClick={() => handleCancel(order.order_id)}
        >
          CANCEL
        </button>
      </div>
    </div>
  );
};

const OrdersList = () => {
  const { ordersListData } = useContext(DataContext);

  return (
    <div className="flex flex-col py-4 h-full gap-4 rounded-3xl bg-primary">
      <div className="text-white">
        <h2>My orders</h2>
      </div>

      <div className="h-[50vh] p-4  gap-4 rounded-3xl overflow-y-auto">
        {ordersListData.map((order) => (
          <OrdersListItem key={order.order_id} order={order} />
        ))}
      </div>
    </div>
  );
};

export default OrdersList;
