export interface User {
  id: number;
  email: string;
  display_name: string | null;
  role_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  display_name?: string;
  role_id: number;
  is_active?: boolean;
}

export interface UserUpdate {
  email?: string;
  display_name?: string;
  role_id?: number;
  is_active?: boolean;
}

export interface UsersListResponse {
  success: boolean;
  data: User[];
  meta: {
    total: number;
    count: number;
    offset: number;
    limit: number;
  };
}

export interface UserResponse {
  success: boolean;
  data: User;
}

export interface Role {
  id: number;
  name: string;
  description: string | null;
  is_system: boolean;
  permission_count?: number;
  user_count?: number;
}

export interface RolesListResponse {
  success: boolean;
  data: Role[];
  meta: {
    total: number;
    count: number;
    offset: number;
    limit: number;
  };
}

export interface UserErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
  };
}
