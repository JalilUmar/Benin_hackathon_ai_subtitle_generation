import Image from "next/image";
import React from "react";

export default function Header() {
  return (
    <div className="w-full fixed top-0 bg-white text-black flex justify-center items-center ">
      <Image src={"/logo.png"} alt="logo" width={100} height={100} />
      <h1 className="text-4xl font-bold font-sans">CulturalChords</h1>
    </div>
  );
}
