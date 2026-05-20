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
