import type { NextPage } from "next";
import Logo from "./Logo";
import Image from "next/image";
import jeffHimself from "../public/colombia_dave.png";

const HomePage: NextPage = () => {
  return (
    <>
      <div className="mx-auto mt-32 text-center group">
        <span className="text-9xl">
          <Logo animated={true} />
        </span>
        <h2 className="text-3xl mt-10">
          <span className="font-jeff mr-1">Jeff&apos;s</span> Fantasy Running
          Race System
        </h2>
      </div>

      <div className="invisible md:visible absolute w-80 right-0 bottom-20">
        <Image src={jeffHimself} alt="Jeff Himself" objectFit="contain" />
      </div>
    </>
  );
};

export default HomePage;
