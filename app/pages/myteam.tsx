import { unstable_getServerSession } from "next-auth";
import { useSession } from "next-auth/react";
import { authOptions } from "./api/auth/[...nextauth]";
import { GetServerSideProps, NextPage } from "next";
import Layout from "../components/Layout";

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await unstable_getServerSession(
    context.req,
    context.res,
    authOptions
  );

  return { props: { session } };
};

// TODO: change database so that each user can only have one team

const MyTeam: NextPage = () =>  {
  const { data: session, status } = useSession({ required: true });

  return (
    <Layout title={`${session?.user?.name}'s team`}>
      {session?.user?.name}&apos;s team

      {session?.user?.image}

      {session?.user?.name}
    </Layout>
  );
}

export default MyTeam
