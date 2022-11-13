import { ReadonlyRequestCookies } from "next/dist/server/app-render";
import prisma from "../prisma";

export async function userFromCookies(
  cookies:
    | ReadonlyRequestCookies
    | Partial<{ "next-auth.session-token": string }>,
  includeTeam: boolean = false
) {
  let token: string | undefined;
  if (cookies instanceof ReadonlyRequestCookies) {
    token = cookies.get("next-auth.session-token")?.value;
  } else {
    token = cookies["next-auth.session-token"]!;
  }

  if (!token) return null;

  const session = await prisma.session.findUnique({
    where: { sessionToken: token },
    include: {
      user: {
        include: {
          team: includeTeam,
        },
      },
    },
  });

  if (!session) return null;

  return session.user;
}
