export interface TeamData {
  id: string;
  name: string;
}

export interface GameData {
  Time: string;
  'Home team': TeamData;
  'Away team': TeamData;
}
export interface TeamProfile {
  name: string;
  conference: string;
  division: string;
  home_court_name: string;
  record: string;
  seed: Int16Array;
  offensive_rating: number;
  defensive_rating: number;
  star_player: string;
}
