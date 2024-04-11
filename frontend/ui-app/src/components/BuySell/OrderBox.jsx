import React, { useContext, useState } from "react";
import { useForm } from "react-hook-form";
import SelectResourceBar from "./SelectResourceBar";
import { DataContext } from "../DataProvider";
import BuySell from "./BuySell";
import EnergySell from "./EnergySell";
import axios from "axios";
import { ENDPOINT } from "../../constants";

const OrderBox = () => {
  const {
    selectedResource,
    setSelectedResource,
    gameId,
    playerId,
    teamSecret,
  } = useContext(DataContext);

  const { register, handleSubmit, setValue } = useForm();

  const onSubmit = async (data) => {
    if (data.action === "set") {
      try {
        axios
          .post(
            `${ENDPOINT}/game/${gameId}/player/${playerId}/energy/set_price`,
            { price: data.energy_price },
            { params: { team_secret: teamSecret } }
          )
          .then((response) => {
            console.log(response.data);
          });
      } catch (error) {
        console.log(error);
      }
    } else {
      const order = {
        side: data.action,
        resource: selectedResource.key,
        size: data.size,
        price: data.price,
        expiration_length: data.expiration_length,
      };

      try {
        axios
          .post(
            `${ENDPOINT}/game/${gameId}/player/${playerId}/orders/create`,
            order,
            { params: { team_secret: teamSecret } }
          )
          .then((response) => {
            console.log(response.data);
          });
      } catch (error) {
        console.log(error);
      }
      console.log(order);
    }
  };

  const handleButtonClick = (action) => {
    setValue("action", action);
    handleSubmit(onSubmit)();
  };

  return (
    <form className="text-white">
      <div className="flex flex-col mt-4 mx-4 p-4 gap-8 rounded-3xl bg-primary">
        <SelectResourceBar
          selectedResource={selectedResource}
          setSelectedResource={setSelectedResource}
        />
        {selectedResource ? (
          <>
            {selectedResource?.key === "electricity" ? (
              <EnergySell
                handleButtonClick={handleButtonClick}
                register={register}
              />
            ) : (
              <BuySell
                handleButtonClick={handleButtonClick}
                register={register}
              />
            )}
          </>
        ) : (
          <p className="text-l">Select a resource</p>
        )}
      </div>
    </form>
  );
};

export default OrderBox;
