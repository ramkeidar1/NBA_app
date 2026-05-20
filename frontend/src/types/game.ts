export interface TeamData {
  name: string;
  record: string;
  odds: string;
}

export interface GameData {
  Time: string;
  'Home team': TeamData;
  'Away team': TeamData;
}

export interface TeamStanding {
  wins: number;
  losses: number;
  seed: number;
}

export interface TeamProfile {
  name: string;
  conference: string;
  division: string;
  homeCourtName: string;
  standing: TeamStanding;
  offensiveRating: number;
  defensiveRating: number;
  starPlayer: string;
}
