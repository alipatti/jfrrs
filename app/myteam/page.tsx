import TeamDashboard, { Team } from "./TeamDashboard";

import { cookies } from "next/headers";

import prisma from "../../prisma";

export default async function ProfilePage() {
  const token = cookies().get("next-auth.session-token")?.value;
  if (token === null) return <>sign in</>;

  const session = await prisma.session.findUnique({
    where: { sessionToken: token },
    include: {
      user: {
        include: {
          team: {
            include: { athletes: { include: { athlete: true } }, league: true },
          },
        },
      },
    },
  });

  return <TeamDashboard team={session?.user.team} />;
}
