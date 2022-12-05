import { NextApiHandler } from "next";
import { userFromCookies } from "../../../app/serverUtil";
import prisma from "../../../prisma";

const handler: NextApiHandler = async (req, res) => {
  const user = await userFromCookies(req.cookies, true);

  if (!user) {
    res.status(401).send("Not logged in.");
    return;
  }

  if (user.team) {
    res.status(403).send("User already has a team.");
    return;
  }

  const team = prisma.fantasyTeam.create({
    data: {
      name: req.body.name,
      shortName: req.body.shortName,
      user: {
        connect: {
          id: user.id,
        },
      },
      league: {
        connect: {
          slug: req.body.league,
        },
      },
    },
  });
};

export default handler;
