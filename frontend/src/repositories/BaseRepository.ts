/**
 * Base Repository interface enforcing consistent CRUD operations across all entities.
 */
import apiClient from '../api/apiClient';

export interface IRepository<T extends { id: string }> {
  findAll(): Promise<T[]>;
  findById(id: string): Promise<T | null>;
  create(item: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<T>;
  update(id: string, item: Partial<T>): Promise<T>;
  delete(id: string): Promise<boolean>;
}

/**
 * Production API Repository connecting directly to FastAPI endpoints.
 */
export class ApiRepository<T extends { id: string, createdAt?: string, updatedAt?: string }> implements IRepository<T> {
  private endpointPath: string;

  constructor(endpointPath: string) {
    this.endpointPath = endpointPath;
  }

  private getCollectionKey(): string {
    return `edu_cache_${this.endpointPath.replace(/\//g, '_')}`;
  }

  private getLocalCache(): T[] {
    const data = localStorage.getItem(this.getCollectionKey());
    return data ? JSON.parse(data) : [];
  }

  private saveLocalCache(items: T[]): void {
    localStorage.setItem(this.getCollectionKey(), JSON.stringify(items));
  }

  async findAll(): Promise<T[]> {
    const response = await apiClient.get(`/${this.endpointPath}`);
    const data = Array.isArray(response.data) ? response.data : (response.data.items || []);
    this.saveLocalCache(data);
    return data;
  }

  async findById(id: string): Promise<T | null> {
    const response = await apiClient.get(`/${this.endpointPath}/${id}`);
    return response.data;
  }

  async create(item: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<T> {
    const response = await apiClient.post(`/${this.endpointPath}`, item);
    const created = response.data;
    const cache = this.getLocalCache();
    cache.push(created);
    this.saveLocalCache(cache);
    return created;
  }

  async update(id: string, updates: Partial<T>): Promise<T> {
    const response = await apiClient.put(`/${this.endpointPath}/${id}`, updates);
    return response.data;
  }

  async delete(id: string): Promise<boolean> {
    await apiClient.delete(`/${this.endpointPath}/${id}`);
    const cache = this.getLocalCache().filter(i => i.id !== id);
    this.saveLocalCache(cache);
    return true;
  }
}
