import axios from "axios";
import cheerio from "cheerio";
import { URLS } from "./util";
import { State } from "@prisma/client";

export interface ParsedMeetSearchData {
  name: string;
  date: Date;
  idTfrrs: number;
  state: State;
}

export default async function getAllMeets() {
  const url = URLS.tfrrs_search_page;
  console.log(`Collecting all meet information from ${url}`)

  const response = await axios.get(URLS.tfrrs_search_page, {
    params: { with_sports: "xc" },
  });
  const $ = cheerio.load(response.data);
  const nPages = parseInt($("ul.pagination li:nth-last-child(2)").text());

  // const nPages = 10;

  const meets = await Promise.all(
    Array(nPages)
      .fill(undefined)
      .map(async (_, i) => {
        // stagger requests a bit
        await new Promise((r) => setTimeout(r, 100 * i));

        const response = await axios.get(url, {
          params: { page: i + 1, with_sports: "xc" },
        });

        const $ = cheerio.load(response.data);

        const meets: ParsedMeetSearchData[] = $("table tbody tr")
          .get()
          .map((tr) => {
            const tds = $(tr).find("td").get();
            return {
              // put date into ISO format (YYYY-MM-DD)
              date: new Date(
                $(tds[0])
                  .text()
                  .replace(/(\d+)\/(\d+)\/(\d+)/, "20$3-$1-$2")
              ),
              name: $(tds[1]).text(),
              state: $(tds[3]).text() as State,
              idTfrrs: parseInt(
                $(tds[1])
                  .find("a")
                  .attr("href")
                  .match(/\/xc\/(\d+)\//)[1]
              ),
            };
          });

        return meets;
      })
  );

  return meets.flat();
}
