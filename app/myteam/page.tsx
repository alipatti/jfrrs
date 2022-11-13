import TeamDashboard from "./TeamDashboard";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import prisma from "../../prisma";

export default async function ProfilePage() {
  const token = cookies().get("next-auth.session-token")?.value;
  if (!token) redirect("/api/auth/signin");

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

  const team = session?.user?.team;

  if (!team) redirect("/createteam");

  return <TeamDashboard team={session?.user.team} />;
}
