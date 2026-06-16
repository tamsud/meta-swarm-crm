export interface Account {
  id: number;
  name: string;
  industry: string | null;
  website: string | null;
  phone: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  name: string;
  industry?: string;
  website?: string;
  phone?: string;
  address?: string;
}

export interface AccountUpdate {
  name?: string;
  industry?: string;
  website?: string;
  phone?: string;
  address?: string;
}

export interface AccountsListResponse {
  success: boolean;
  data: Account[];
  meta: {
    total: number;
    count: number;
    offset: number;
    limit: number;
  };
}

export interface AccountResponse {
  success: boolean;
  data: Account;
}

export interface AccountErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    contact_count?: number;
    opportunity_count?: number;
  };
}
