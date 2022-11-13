import { NextApiHandler } from "next";

const handler: NextApiHandler = (req, res) => {
  console.log(req.body);

  res.status(200).send("Hello World");
};

export default handler;
