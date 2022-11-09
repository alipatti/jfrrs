import { Gender, Level, Sport, State } from "@prisma/client";
import axios from "axios";
import prisma from "../prisma";
import { mapLimit } from "async";

import { parseTeamId, URLS } from "./util";
import { scrapeTFMeet } from "./tfMeet";
import { scrapeXCMeet } from "./xcMeet";

// shape of scraped data before processing
interface RawDirectAthleticsMeetData {
  url: string;
  tfrrs: "1" | "0";
  venue_state: string;
  name: string;
  meetpro: "1" | "0";
  date_begin: string;
  meet_hnd: string;
  sport: "track" | "xc" | "swimming";
  outdoors?: "1" | "0";
}

export interface RawTfrrsAutocompleteData {
  text: string;
  url: string;
}

// after processing
export interface ParsedDirectAthleticsMeetData {
  name: string;
  date: Date;
  idTfrrs: number;
  sport: Sport;
  outdoors: boolean;
  state: State;
}

export const MAX_CONCURRENT_REQUESTS = 10;

export async function main() {
  // await scrapeAllTeamsAndConferences();
  await scrapeAllMeets();
}

export async function scrapeAllMeets() {
  const response = await axios.get(URLS.direct_athletics_script);

  const data: RawDirectAthleticsMeetData[] = JSON.parse(
    response.data
      .match(/var data =\s+(\[.*?\]);/s)[1] // find the JSON string
      .replaceAll("\t", " ") // parser doesn't like tabs
  );

  const allMeets: ParsedDirectAthleticsMeetData[] = data
    .filter((meet) => meet.tfrrs === "1") // only keep meets on TFRRS
    .filter((meet) => meet.sport !== "swimming") // drop swim meets
    .map((meet) => ({
      name: meet.name,
      date: new Date(meet.date_begin),
      idTfrrs: parseInt(meet.meet_hnd),
      sport: (meet.sport == "track" ? "tf" : "xc") as Sport,
      outdoors: !meet.outdoors ? null : meet.outdoors === "1",
      state: meet.venue_state as State,
    }));

  // filter out previously-scraped meets
  const scrapedMeets = await prisma.meet.findMany();
  const scrapedMeetIds = scrapedMeets.map((meet) => meet.idTfrrs);
  const meetsToScrape = allMeets
    .filter((meet) => !scrapedMeetIds.includes(meet.idTfrrs))
    .reverse() // most-recent first
    .slice(0, 4); // limit the number of meets during debugging

  console.log(
    `Found ${allMeets.length} meets, ${scrapedMeets.length} of which have previously been scraped.`
  );
  console.log(`Scraping ${meetsToScrape.length} meets...`);

  // send out requests while limiting concurrency to not break TFRRS
  const scrapedIds = (
    await mapLimit(
      meetsToScrape,
      MAX_CONCURRENT_REQUESTS,
      async (meet: ParsedDirectAthleticsMeetData) => {
        try {
          if (meet.sport === "xc") await scrapeXCMeet(meet);
          else await scrapeTFMeet(meet);
          return meet.idTfrrs;
        } catch (error) {
          console.error(`Error scraping ${meet.name}:`);
          console.error(error);
          return null;
        }
      }
    )
  ).filter((id) => id);  // remove null values

  console.log(`Successfully scraped ${scrapedIds.length} meets.`);
  return scrapedIds.length
}

export async function scrapeAllTeamsAndConferences() {
  const response = await axios.get(URLS.tfrrs_autocomplete_script);

  // helper function to extract json arrays from the script
  const getData = (regex: RegExp): RawTfrrsAutocompleteData[] =>
    JSON.parse(
      response.data
        // quote the object keys to make valid json
        .replaceAll("url:", '"url":')
        .replaceAll("text:", '"text":')
        .match(regex)[1]
    );

  const teams = getData(/var autocomplete_teams = (\[.+?\]);/s).map(
    ({ text, url }) => {
      // TODO DRY: use the parseTeamId() function here
      const match = url.match(
        /(?<state>[A-Z]{2})_(?<level>j?college)_(?<gender>m|f)_.*(?=\.html)/
      )!;
      return {
        name: text,
        gender: match.groups!.gender.toUpperCase() as Gender,
        state: match.groups!.state as State,
        level: match.groups!.level as Level,
        idTfrrs: match[0],
      };
    }
  );

  const conferences = getData(/var autocomplete_conferences = (\[.+?\]);/s).map(
    ({ text, url }) => ({
      name: text,
      idTfrrs: parseInt(url.match(/\/leagues\/(\d+)\.html/)[1]),
    })
  );

  // save to database
  const { length: nTeams } = await Promise.all(
    teams.map(
      async (team) =>
        await prisma.team.upsert({
          where: { idTfrrs: team.idTfrrs },
          create: { ...team },
          update: {},
        })
    )
  );

  const { length: nConferences } = await Promise.all(
    conferences.map(
      async (conference) =>
        await prisma.conference.upsert({
          where: { idTfrrs: conference.idTfrrs },
          create: { ...conference },
          update: {},
        })
    )
  );
  console.log(`Added ${nTeams} teams and ${nConferences} conferences.`);
}

(async () => await main())();
