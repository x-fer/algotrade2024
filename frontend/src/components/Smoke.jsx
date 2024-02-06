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

  useEffect(() => {
    const noise3D = createNoise3D();
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    // clear

    const particleX = 500;
    const particleY = 500;
    const particleStd = 50;

    let particles = Array(100)
      .fill()
      .map(() => {
        return {
          x: particleX + Math.random() * particleStd,
          y: particleY + Math.random() * particleStd,
          vx: 0,
          vy: 0,
          radius: Math.random() * 50,
          time: Math.random() * 10,
        };
      });

    let z = 0;
    // animation
    const animate = () => {
      //   ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = "rgba(0, 0, 0, 1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < canvas.height; i += 10) {
        for (let j = 0; j < canvas.width; j += 10) {
          const x = noise3D(j / 100, i / 100, z);
          const y = noise3D(j / 100, i / 100, z + 1000);

          // plot vector field

          ctx.beginPath();
          ctx.moveTo(j, i);
          ctx.lineTo(j + x * 10, i + y * 10);
          ctx.strokeStyle = "white";
          ctx.stroke();
        }
      }

      z += 0.01;
      //   console.log(z);

      for (let particle of particles) {
        ctx.beginPath();
        // radial gradient
        const gradient = ctx.createRadialGradient(
          particle.x,
          particle.y,
          0,
          particle.x,
          particle.y,
          particle.radius
        );
        gradient.addColorStop(
          0,
          `rgba(255, 255, 255, ${particle.time / 6000})`
        );
        gradient.addColorStop(1, "rgba(255, 255, 255, 0)");
        ctx.fillStyle = gradient;

        let new_radius = particle.radius / (particle.time / 1000);

        ctx.arc(particle.x, particle.y, new_radius, 0, Math.PI * 2);

        ctx.fill();

        particle.x += particle.vx;
        particle.y += particle.vy;

        particle.vx += noise3D(particle.x / 100, particle.y / 100, z) / 5;
        particle.vy +=
          noise3D(particle.x / 100, particle.y / 100, z + 1000) / 5 - 0.3;

        particle.vx *= 0.9;
        particle.vy *= 0.9;

        particle.vx *= 1 + Math.random() * 0.2;
        // particle.vy *= 1 + Math.random() * 0.4;

        particle.time -= 1;
      }

      particles = particles.filter((p) => p.time > 0);
      particles = particles.filter(
        (p) =>
          p.x > 0 &&
          p.x < canvas.width &&
          p.y > 0 &&
          p.y < canvas.height &&
          p.radius > 0
      );

      console.log(particles.length);

      let i = 0;
      while (particles.length < 1000 && i++ < 5) {
        particles.push({
          x: particleX + Math.random() * particleStd,
          y: particleY + Math.random() * particleStd,
          vx: 0,
          vy: 0,
          radius: Math.random() * 100,
          time: Math.random() * 1000,
        });
      }

      requestAnimationFrame(animate);
    };

    animate();
  }, []);

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
