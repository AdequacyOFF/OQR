export type UserRole = 'participant' | 'admitter' | 'scanner' | 'admin';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: UserRole;
}

export interface UserInfo {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface ParticipantProfile {
  id: string;
  user_id: string;
  full_name: string;
  school: string;
  grade: number;
  created_at: string;
  updated_at: string;
}

export interface Competition {
  id: string;
  name: string;
  date: string;
  registration_start: string;
  registration_end: string;
  variants_count: number;
  max_score: number;
  status: string;
  created_by: string;
  created_at: string;
}

export interface Registration {
  id: string;
  participant_id: string;
  competition_id: string;
  status: string;
  created_at: string;
  entry_token?: string;
  attempt_id?: string;
  variant_number?: number;
  final_score?: number | null;
}

export interface ScanItem {
  id: string;
  attempt_id: string | null;
  file_path: string;
  ocr_score: number | null;
  ocr_confidence: number | null;
  ocr_raw_text: string | null;
  verified_by: string | null;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface ResultEntry {
  rank: number;
  participant_name: string;
  school: string;
  grade: number;
  score: number;
  max_score: number;
}

export interface AuditLogEntry {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  user_id: string | null;
  ip_address: string | null;
  details: Record<string, unknown>;
  timestamp: string;
}
