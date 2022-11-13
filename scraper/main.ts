import prisma from "../prisma";
import { mapLimit } from "async";

import { URLS } from "./util";
import scrapeXCMeet from "./scrapeXCMeet";
import getAllMeets from "./getAllMeets";

export const MAX_CONCURRENT_REQUESTS = 10;

export async function main() {
  await scrapeAllMeets();
}

export async function scrapeAllMeets() {
  const allMeets = await getAllMeets();

  // filter out previously-scraped meets
  const scrapedMeets = await prisma.meet.findMany();
  const scrapedMeetIds = scrapedMeets.map((meet) => meet.idTfrrs);
  const meetsToScrape = allMeets.filter(
    (meet) => !scrapedMeetIds.includes(meet.idTfrrs)
  );

  console.log(
    `Found ${allMeets.length} XC meets, ${scrapedMeets.length} of which have previously been scraped.`
  );
  console.log(`Scraping ${meetsToScrape.length} meets...`);

  // send out requests while limiting concurrency to not break TFRRS
  const scrapedIds = await mapLimit(
    meetsToScrape,
    MAX_CONCURRENT_REQUESTS,
    async (meet, callback) => {
      try {
        await scrapeXCMeet(meet);
        callback(null, meet.idTfrrs);
      } catch (error) {
        console.error(`Error scraping ${meet.name}`);
        console.error(` - ${URLS.meet.xc(meet.idTfrrs)})`);
        // console.error(error);
        callback(null, null);
      }
    }
  );

  console.log(
    `Successfully scraped ${scrapedIds.filter((id) => id).length} meets.`
  );
}

(async () => await main())();
