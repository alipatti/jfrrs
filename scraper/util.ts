import { ClassYear, Gender, Level, State, Team } from "@prisma/client";

export const URLS = {
  // base url
  base: "https://tfrrs.org",

  // urls for specific pages
  conference: (id: number) => `${URLS.base}/leagues/${id}`,
  athlete: (id: number) => `${URLS.base}/athletes/${id}`,
  team: (id: string) => `${URLS.base}/teams/${id}`,
  meet: {
    xc: (id: number) => `${URLS.base}/results/xc/${id}`,
    tf: (id: number) => `${URLS.base}/results/tf/${id}`,
  },

  // urls for site scripts
  tfrrs_autocomplete_script: "https://www.tfrrs.org/js/navbar_autocomplete.js",
  direct_athletics_script:
    "https://www.directathletics.com/scripts/fuseDriver.js",

  tfrrs_search_page: "https://tfrrs.org/results_search_page.html",
};

export function parseDistance(str: string): number {
  const { distance, unit } = /(?<distance>[\d.]+) ?(?<unit>.*)/.exec(str)
    ?.groups as { distance: string; unit: string };

  switch (unit) {
    case "Mile":
    case "mile":
    case "M":
      return parseFloat(distance) * 1609;

    case "Kilometer":
    case "kilometer":
    case "K":
    case "k":
      return parseFloat(distance) * 1000;

    case "m":
    case "":
      return parseFloat(distance) * 1;

    default:
      console.error(`'${unit}' is not a valid unit.`);
      return null;
  }
}

export function parsePlace(str: string): number | null {
  return parseInt(str) || null;
}

export function parseTime(str: string): number | null {
  const multipliers = [1, 60, 60 * 60];
  const time = str
    .split(":")
    .reverse()
    .map((x, i) => parseFloat(x) * multipliers[i])
    .reduce((a, b) => a + b, 0);
  return time || null;
}

export function parseClassYear(str: string): ClassYear {
  switch (str.toUpperCase().trim()) {
    case "FY-1":
    case "FR-1":
    case "FR":
    case "FY":
    case "FRESHMAN":
      return "FR";

    case "SO-2":
    case "SO":
    case "SOPHOMORE":
      return "SO";

    case "JR-3":
    case "JR":
    case "JUNIOR":
      return "JR";

    case "SR-4":
    case "SR":
    case "SENIOR":
      return "SR";

    case /^\d+$/.exec(str)?.input:
      // string is the class year, e.g. 2024
      // TODO implement
      return null;

    case "": // weird space character
      return null;

    default:
      return null;
  }
}

export function parseTeamId(id: string): {
  state: State;
  level: Level;
  gender: Gender;
} {
  const groups = id?.match(
    /(?<state>[A-Z]{2})_(?<level>j?college)_(?<gender>m|f)_.*/
  )?.groups;

  if (!groups) {
    throw new Error(`Unable to parse team id: ${id}`);
  }

  return {
    state: groups.state as State,
    level: groups.level as Level,
    gender: groups.gender.toUpperCase() as Gender,
  };
}
