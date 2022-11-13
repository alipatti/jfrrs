import axios from "axios";
import { URLS } from "./util";
import { State, Level, Gender } from "@prisma/client";

export interface RawTfrrsAutocompleteData {
  text: string;
  url: string;
}

export default async function scrapeAllTeamsAndConferences() {
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
