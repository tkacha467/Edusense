import { PreferencesRepository, UserRepository } from '../../repositories';
import type { LearningPreferences, StudentProfile } from '../../types';

export class ProfileService {
  async getPreferences(userId: string): Promise<LearningPreferences | null> {
    const all = await PreferencesRepository.findAll();
    return all.find(p => p.userId === userId) || null;
  }

  async savePreferences(userId: string, data: Partial<LearningPreferences>): Promise<LearningPreferences> {
    const existing = await this.getPreferences(userId);
    if (existing) {
      return await PreferencesRepository.update(existing.id, data);
    } else {
      return await PreferencesRepository.create({ ...data, userId } as any);
    }
  }
}

export const profileService = new ProfileService();
