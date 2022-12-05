import { randomBytes } from "crypto";
import { NextApiHandler } from "next";
import { userFromCookies } from "../../../app/serverUtil";

import prisma from "../../../prisma";

const handler: NextApiHandler = async (req, res) => {
  console.log(req.body);
  console.log(typeof req.body);

  const user = await userFromCookies(req.cookies, true);

  if (!user) {
    res.status(401).send("Not logged in.");
    return;
  }

  if (user.team) {
    res.status(403).send("User already has a team.");
    return;
  }

  // TODO check if user is the owner of a league
  

  const slug = randomBytes(3).toString("hex").toUpperCase();

  const league = await prisma.fantasyLeague.create({
    data: {
      name: req.body.name,
      slug,
      owner: {
        connect: {
          id: user?.id,
        },
      },
    },
    select: { slug: true },
  });

  console.log("league created");

  res.status(200).send(league);
};

export default handler;
