import { NextApiRequest, NextApiResponse } from "next";
import prisma from "../../prisma/client";

// HACK, but it's probably fine since this is only used internally
interface RequestWithBody extends NextApiRequest {
  body: {
    type: "team" | "conference" | "meet" | "athlete";
    data: object;
    key: string;
  };
}

const handler = async (req: RequestWithBody, res: NextApiResponse) => {
  if (req.body.key != process.env.API_KEY) {
    res.status(403).send("Invalid API key.");
    return;
  }

  if (req.method !== "POST") {
    res.status(405).send("Only POST accepted.");
    return;
  }

  console.log(req.body)

  try {
    // @ts-ignore
    prisma[req.body.type].create({ data: req.body.data });
    res.status(200);
  } catch (error) {
    res.status(400); // bad request
  }
};

export default handler;
