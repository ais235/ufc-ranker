export interface Fighter {
  id: number
  name_ru: string
  name_en?: string
  nickname?: string
  country?: string
  country_flag_url?: string
  image_url?: string
  height?: number
  weight?: number
  reach?: number
  age?: number
}

export interface WeightClass {
  id: number
  name_ru: string
  name_en?: string
  gender: string
  is_p4p: boolean
}

export interface Ranking {
  fighter: Fighter
  rank_position?: number
  is_champion: boolean
  rank_change: number
}

export interface FightRecord {
  wins: number
  losses: number
  draws: number
  no_contests: number
  total_fights: number
  win_percentage: number
}

export interface FighterDetail extends Fighter {
  fight_record?: FightRecord
}

export interface UpcomingFight {
  id: number
  fighter1: Fighter
  fighter2: Fighter
  weight_class: WeightClass
  is_main_event: boolean
  is_title_fight: boolean
}

export interface Comparison {
  fighter1: FighterDetail
  fighter2: FighterDetail
  comparison: {
    height: {
      fighter1: number | null
      fighter2: number | null
      difference: number
    }
    weight: {
      fighter1: number | null
      fighter2: number | null
      difference: number
    }
    reach: {
      fighter1: number | null
      fighter2: number | null
      difference: number
    }
    age: {
      fighter1: number | null
      fighter2: number | null
      difference: number
    }
  }
}
