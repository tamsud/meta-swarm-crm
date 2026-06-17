export interface MockEmail {
  id: string;
  subject: string;
  from_email: string;
  to_email: string;
  body: string | null;
  status: 'unread' | 'read';
  created_at: string;
}

export interface MockEmailListItem {
  id: string;
  subject: string;
  from_email: string;
  to_email: string;
  preview: string;
  status: 'unread' | 'read';
  created_at: string;
}

export interface MockEmailCreate {
  to_email: string;
  subject: string;
  body?: string;
}

export interface MockEmailsListResponse {
  success: boolean;
  data: MockEmailListItem[];
  meta: {
    total: number;
    count: number;
    offset: number;
    limit: number;
  };
}

export interface MockEmailResponse {
  success: boolean;
  data: MockEmail;
}

export interface ClearMockEmailsResponse {
  success: boolean;
  data: {
    deleted_count: number;
  };
}
