import axios from "axios";
import cheerio from "cheerio";
import { mapLimit } from "async";
import { URLS } from "./util";
import { MAX_CONCURRENT_REQUESTS, ParsedDirectAthleticsMeetData } from "./main";

export async function getAllMeetInfo() {
  const url = URLS.tfrrs_search_page;

  // TODO
  //   const nPages = 295;
  const nPages = 5;

  const pageNumbers = Array(nPages)
    .fill(undefined)
    .map((x, i) => i + 1);

  const meets: ParsedDirectAthleticsMeetData[] = (
    await mapLimit(pageNumbers, MAX_CONCURRENT_REQUESTS, async (i: number) => {
      const response = await axios.get(url, {
        params: { page: i + 1, with_sports: "xc" },
      });

      const $ = cheerio.load(response.data);

      const results = $("table tbody tr")
        .get()
        .map((tr) => {
          const tds = $(tr).find("td").get();
          return {
            date: new Date(tds[0].innerText),
            name: tds[1].innerText,
            state: tds[3].innerText,
            idTfrrs: parseInt(
              $(tds[1])
                .find("a")
                .attr("href")
                .match(/\/xc\/(\d+)\//)[1]
            ),
          };
        });
      return results;
    })
  ).flat();
}
