import cheerio from "cheerio";
import axios from "axios";

import {
  URLS,
  parsePlace,
  parseDistance,
  parseTime,
  parseClassYear,
  parseTeamId,
} from "./util";
import prisma from "../prisma";
import { Gender } from "@prisma/client";
import { ParsedMeetSearchData } from "./getAllMeets";

export default async function scrapeXCMeet({
  date,
  idTfrrs,
  name,
  state,
}: ParsedMeetSearchData) {
  const url = URLS.meet.xc(idTfrrs);
  console.log(`Scraping ${name}`);
  console.log(` - ${date.toDateString()}`);
  console.log(` - ${url}`);

  // load meet page
  const response = await axios.get(url);
  const $ = cheerio.load(response.data);

  // extract general meet info
  const header = $(".xc-header-row > div > div");

  const location =
    header.find("div:first div:last").text().replaceAll(/\s+/g, " ").trim() ||
    null;

  const attributes = Object.fromEntries(
    header
      .find("> span")
      .map((_, el) => [$(el).text().split(": ")])
      .get()
  );

  const eventIds = $("#quick-links-list a")
    // @ts-ignore (`.attrib` doesn't exists on TextElement, so the compiler complains)
    .map((i, el) => el.attribs.href)
    .get()
    .map((id) => parseInt(id.replace("#event", "")));

  // scrape individual races
  const races = await Promise.all(eventIds.map((id) => scrapeXCRace(id, $)));

  // save meet and all its related info to the database
  // it looks jank but the single query ensures that the write is atomic
  await prisma.meet.create({
    data: {
      name,
      date,
      idTfrrs,
      state,
      location,
      attributes,
      events: {
        create: races.map(({ race_info, race_results }) => ({
          ...race_info,
          results: {
            create: race_results.map(({ result_info: info, athlete, team }) => {
              return {
                ...info,
                athlete: athlete // create athlete if it doesn't exist
                  ? {
                      connectOrCreate: {
                        where: { idTfrrs: athlete.idTfrrs },
                        create: { ...athlete },
                      },
                    }
                  : undefined,
                team: team // create team if it doesn't exist
                  ? {
                      connectOrCreate: {
                        where: { idTfrrs: team.idTfrrs },
                        create: { ...team },
                      },
                    }
                  : undefined,
              };
            }),
          },
        })),
      },
    },
  });

  const nResults = races
    .map(({ race_results: results }) => results.length)
    .reduce((a, b) => a + b, 1);

  console.log(
    `Successfully scraped ${races.length} races and ` +
      `${nResults} results from ${name} (${idTfrrs})`
  );
}

async function scrapeXCRace(id: number, $: cheerio.Root) {
  const titleDiv = $(
    `[name$=${id}] ~ * .custom-table-title:contains('Individual Results')`
  );

  const { name, distance } =
    /(?<name>.*)\s+Individual Results\s+\((?<distance>.+)\)/.exec(
      titleDiv.find("h3").text()
    )?.groups;

  const gender: Gender = name.toLowerCase().includes("women") ? "F" : "M";

  const resultsTable = titleDiv.find("~ table:first, :has(table) table:first");
  const cols = resultsTable
    .find("thead th")
    .map((_, el) => $(el).text().toLowerCase().trim())
    .get();

  const race_results = resultsTable
    .find("tbody tr")
    .get()
    // parse results
    .map((el: HTMLElement) => {
      // mapping to easily retrieve a specific column, e.g. team, pl, score
      const tds: { [k: string]: cheerio.Cheerio } = Object.fromEntries(
        $(el)
          .find("td")
          .map((i, el) => [[cols[i], $(el)]])
          .get()
      );

      let teamId = tds.team
        .find("a")
        .attr("href")
        ?.match(/(?<=\/)[\w\-%\d]+(?=\.html)/)
        ?.pop();

      // we aren't dealing with numeric DirectAthletics ID, so we ignore them
      if (teamId?.match(/^\d+$/)) teamId = undefined;

      const athleteId =
        parseInt(
          tds.name
            .find("a")
            .attr("href")
            ?.match(/(?<=athletes(?:\/track)?\/)\d+(?=\.html|\/)/)
            ?.pop()
        ) || undefined;

      return {
        result_info: {
          score: parsePlace(tds.score.text()),
          place: parsePlace(tds.pl.text()),
          classYear: parseClassYear(tds.year.text()),
          time: parseTime(tds.time.text()),
        },
        team: teamId
          ? {
              idTfrrs: teamId,
              name: tds.team.text().trim(),
              ...parseTeamId(teamId),
            }
          : undefined,
        athlete: athleteId
          ? {
              idTfrrs: athleteId,
              name: tds.name.text().trim(),
            }
          : undefined,
      };
    })
    // remove DNF, DNS, DQ, etc.
    .filter(({ result_info: { place, time } }) => time && place !== 0);

  return {
    race_info: {
      distanceMeters: parseDistance(distance),
      gender,
      idTfrrs: id,
      name,
    },
    race_results,
  };
}
