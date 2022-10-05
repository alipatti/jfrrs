import type { NextPage } from "next";
import Layout from "../components/Layout";
import JFRRS from "../components/Logo";
import Image from "next/image";
import jeffHimself from "../public/colombia_dave.png";
import { trpc } from "../utils/trpc";

const HomePage: NextPage = () => {
  const hello = trpc.useQuery(["example.hello", { text: "from tRPC" }]);
  return (
    <Layout>
      <div className="mx-auto mt-32 text-center group">
        <JFRRS size="9xl" animated={true} />
        <h2 className="text-3xl mt-10">
          <span className="font-jeff mr-1">Jeff&apos;s</span> Fantasy Running Race
          System
        </h2>
      </div>

      <div className="invisible md:visible absolute w-80 right-0 bottom-20 translate-y-2">
        <Image src={jeffHimself} objectFit="contain" />
      </div>
    </Layout>
  );
};

export default HomePage;
