import { UserRepository } from '../repositories';
import type { User } from '../types';

export class AuthService {
  async getCurrentUser(): Promise<User | null> {
    const session = localStorage.getItem('edu_session');
    if (!session) return null;
    try {
      const parsed = JSON.parse(session);
      return await UserRepository.findById(parsed.user.id);
    } catch {
      return null;
    }
  }
}

export const authService = new AuthService();
