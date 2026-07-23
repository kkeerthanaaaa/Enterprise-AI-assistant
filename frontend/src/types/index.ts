export type Role = "employee" | "manager" | "hr" | "admin";

export interface UserOut {
  id: string;
  company_id: string;
  full_name: string;
  email: string;
  role: Role;
  department_id: string | null;
}

export interface Citation {
  document_id: string;
  title: string;
  doc_type: string;
  chunk_index: number;
  snippet: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  citations: Citation[];
  used_sql_context: boolean;
  used_business_rules: boolean;
}

export interface LeaveBalance {
  leave_type: string;
  year: number;
  entitled_days: number;
  used_days: number;
  remaining_days: number;
}

export interface EmployeeOut {
  id: string;
  employee_code: string;
  full_name: string;
  email: string;
  role: Role;
  designation: string | null;
  department_id: string | null;
  manager_id: string | null;
  is_active: boolean;
}

export interface DocumentOut {
  id: string;
  title: string;
  doc_type: string;
  original_filename: string;
  version: number;
  status: string;
  is_active: boolean;
  created_at: string;
}
