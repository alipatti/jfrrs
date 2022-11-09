import axios from "axios";
import cheerio from "cheerio";
import { mapLimit } from "async";
import { URLS } from "./util";
import { MAX_CONCURRENT_REQUESTS, ParsedMeetSearchData } from "./main";
import { State } from "@prisma/client";

export async function getAllMeetInfo() {
  const url = URLS.tfrrs_search_page;

  // TODO
  //   const nPages = 295;
  const nPages = 20;

  const pageNumbers = Array(nPages)
    .fill(undefined)
    .map((x, i) => i);

  // const numPromise = await mapLimit(
  //   [1, 2, 3, 4, 5],
  //   2,
  //   async (num, callback) => {
  //     await new Promise((r) => setTimeout(r, 500));
  //     console.log(num);
  //     callback(null, num ** 2);
  //   }
  // );

  // console.log(numPromise);

  const meets = (
    await mapLimit(
      pageNumbers,
      MAX_CONCURRENT_REQUESTS,
      async (i, callback) => {
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

        callback(null, meets);
      }
    )
  ).flat() as ParsedMeetSearchData[];

  
  return meets;
}
