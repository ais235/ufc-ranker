export interface Fighter {
  id: number
  name: string  // Основное имя для отображения
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
  wins: number
  losses: number
  draws: number
  weight_class_id?: number
}

export interface WeightClass {
  id: number
  name: string  // Основное имя для отображения
  name_ru: string
  name_en?: string
  weight_min?: number
  weight_max?: number
  weight_limit?: string  // Строка для отображения
  gender: string
  is_p4p: boolean
}

export interface Ranking {
  id: number
  fighter: Fighter
  weight_class: string
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

export interface Event {
  id: number
  name: string
  event_number?: string
  event_type?: string
  event_date?: string
  location?: string
  venue?: string
  venue_url?: string
  location_url?: string
  event_url?: string
  reference_url?: string
  status?: string
  attendance?: number
  gate_revenue?: string
  image_url?: string
  description?: string
  is_upcoming?: boolean
}

export interface Fight {
  id: number
  event_name?: string
  fighter1_name?: string
  fighter2_name?: string
  weight_class?: string
  scheduled_rounds: number
  method?: string
  method_details?: string
  round?: number
  time?: string
  fight_date?: string
  location?: string
  notes?: string
  is_title_fight: boolean
  is_main_event: boolean
  is_win?: string
  is_loss?: string
  is_draw?: string
  is_nc?: string
  fighter1_record?: string
  fighter2_record?: string
  fighter1_country?: string
  fighter2_country?: string
  card_type?: string
  referee?: string
  winner_name?: string
  judges_score?: string
  fight_order?: number
}

export interface FightStats {
  id: number
  fighter: Fighter
  round_number: number
  knockdowns: number
  significant_strikes_landed: number
  significant_strikes_attempted: number
  significant_strikes_rate: number
  total_strikes_landed: number
  total_strikes_attempted: number
  takedown_successful: number
  takedown_attempted: number
  takedown_rate: number
  submission_attempt: number
  reversals: number
  head_landed: number
  head_attempted: number
  body_landed: number
  body_attempted: number
  leg_landed: number
  leg_attempted: number
  distance_landed: number
  distance_attempted: number
  clinch_landed: number
  clinch_attempted: number
  ground_landed: number
  ground_attempted: number
  result?: string
  last_round: boolean
  time?: string
  winner?: string
}

export interface FighterStatsSummary {
  fighter: Fighter
  total_fights: number
  total_rounds: number
  total_significant_strikes_landed: number
  total_significant_strikes_attempted: number
  average_significant_strikes_rate: number
  total_takedowns_successful: number
  total_takedowns_attempted: number
  average_takedown_rate: number
  total_knockdowns: number
  total_submission_attempts: number
  total_reversals: number
}