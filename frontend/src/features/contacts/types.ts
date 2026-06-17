export interface Account {
  id: number;
  name: string;
}

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  job_title: string | null;
  account_id: number | null;
  account: Account | null;
  created_at: string;
  updated_at: string;
}

export interface ContactCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  account_id?: number | null;
}

export interface ContactUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  job_title?: string;
  account_id?: number | null;
}

export interface ContactsListResponse {
  success: boolean;
  data: Contact[];
  meta: {
    total: number;
    count: number;
    offset: number;
    limit: number;
  };
}

export interface ContactResponse {
  success: boolean;
  data: Contact;
}

export interface ContactErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    account_id?: number;
  };
}
