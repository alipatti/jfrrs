import { Session } from "next-auth";
import { ReadonlyRequestCookies } from "next/dist/server/app-render";
import prisma from "../prisma";

export async function sessionFromCookies(
  cookies: ReadonlyRequestCookies
): Promise<Session | null> {
  const token = cookies.get("next-auth.session-token")?.value;
  if (!token) return null;

  const session = await prisma.session.findUnique({
    where: { sessionToken: token },
  });

  if (!session) return null;

  return {
    ...session,
    expires: session.expires.toISOString(),
  };
}
