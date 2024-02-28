import { useRef, useEffect, useState } from "react";
import "./Smoke.css";

import { createNoise3D } from "simplex-noise";

import home_1 from "../assets/home_1.png";
import home_2 from "../assets/home_2.png";
import home_3 from "../assets/home_3.png";
import home_4 from "../assets/home_4.png";

function Smoke() {
  const canvasRef = useRef(null);
  const [canvasMouse, setCanvasMouse] = useState({ x: 0, y: 0 });

  const mouseHandler = (e) => {
    setCanvasMouse({ x: e.clientX, y: e.clientY });
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    canvas.addEventListener("mousemove", mouseHandler);
    return () => {
      canvas.removeEventListener("mousemove", mouseHandler);
    };
  }, []);

  useEffect(() => {
    const home_images_src = [home_1, home_2, home_3, home_4];
    const movement = [1 / 1000, 1 / 500, 1 / 200, 1 / 100];

    let home_images = [];
    for (let src of home_images_src) {
      const img = new Image();
      img.src = src;
      home_images.push(img);
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    for (let i = 0; i < home_images.length; i++) {
      ctx.drawImage(
        home_images[i],
        0 + canvasMouse.x * movement[i],
        0 + canvasMouse.y * movement[i]
      );
    }
  }, [canvasMouse]);

  return (
    <canvas
      ref={canvasRef}
      className="smoke"
      style={{ width: "100%", height: "100%" }}
      width={1152}
      height={896}
    />
  );
}

export default Smoke;
