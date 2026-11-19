/**
 * src/core/storage.ts
 * Repository pattern for client storage with transparent in-memory fallback.
 */

import { CrowdsourceRecord, IDataStore } from './types';

export const CROWDSOURCE_STORAGE_KEY = 'msf:crowdsource_records';

/**
 * Robust in-memory data store for server-side, test runners, or private mode.
 */
export class InMemoryDataStore implements IDataStore {
  private memoryMap: Map<string, string> = new Map();
  private crowdsourceRecords: Map<string, CrowdsourceRecord> = new Map();

  getItem<T = unknown>(key: string): T | null {
    const raw = this.memoryMap.get(key);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  }

  setItem<T = unknown>(key: string, value: T): boolean {
    try {
      this.memoryMap.set(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  }

  removeItem(key: string): boolean {
    return this.memoryMap.delete(key);
  }

  clear(): void {
    this.memoryMap.clear();
    this.crowdsourceRecords.clear();
  }

  isAvailable(): boolean {
    return true;
  }

  private makeRecordKey(categoryId: string, prestationId: string, provinceSigla: string): string {
    return `${categoryId.toLowerCase()}:${prestationId.toLowerCase()}:${provinceSigla.toUpperCase()}`;
  }

  // Simple record API
  getRecord(prestationId: string, provinceSigla: string): CrowdsourceRecord | null {
    const cleanPid = prestationId.toLowerCase();
    const cleanSigla = provinceSigla.toUpperCase();
    for (const record of this.crowdsourceRecords.values()) {
      if (
        record.prestationId.toLowerCase() === cleanPid &&
        record.provinceSigla.toUpperCase() === cleanSigla
      ) {
        return { ...record };
      }
    }
    return null;
  }

  saveRecord(record: CrowdsourceRecord): void {
    this.saveCrowdsourceOverride(record);
  }

  getAllRecords(): Record<string, CrowdsourceRecord> {
    return this.getAllCrowdsourceOverrides();
  }

  // Domain Crowdsource Override API
  getCrowdsourceOverride(
    categoryId: string,
    prestationId: string,
    provinceSigla: string
  ): CrowdsourceRecord | null {
    const key = this.makeRecordKey(categoryId, prestationId, provinceSigla);
    const record = this.crowdsourceRecords.get(key);
    return record ? { ...record } : null;
  }

  saveCrowdsourceOverride(record: CrowdsourceRecord): boolean {
    const key = this.makeRecordKey(record.categoryId, record.prestationId, record.provinceSigla);
    this.crowdsourceRecords.set(key, { ...record });
    return true;
  }

  getAllCrowdsourceOverrides(): Record<string, CrowdsourceRecord> {
    const out: Record<string, CrowdsourceRecord> = {};
    for (const [k, v] of this.crowdsourceRecords.entries()) {
      out[k] = { ...v };
    }
    return out;
  }

  clearCrowdsourceOverrides(): void {
    this.crowdsourceRecords.clear();
  }
}

/**
 * LocalStorage repository with automatic graceful fallback to InMemoryDataStore.
 */
export class LocalStorageDataStore implements IDataStore {
  private fallback: InMemoryDataStore = new InMemoryDataStore();
  private storageUsable: boolean = false;

  constructor() {
    this.storageUsable = this.testStorageAvailability();
  }

  private testStorageAvailability(): boolean {
    if (typeof window === 'undefined' || !window.localStorage) {
      return false;
    }
    try {
      const probeKey = '__msf_canary__';
      window.localStorage.setItem(probeKey, '1');
      window.localStorage.removeItem(probeKey);
      return true;
    } catch {
      return false;
    }
  }

  isAvailable(): boolean {
    return this.storageUsable;
  }

  getItem<T = unknown>(key: string): T | null {
    if (!this.storageUsable) {
      return this.fallback.getItem<T>(key);
    }
    try {
      const item = window.localStorage.getItem(key);
      if (!item) return null;
      return JSON.parse(item) as T;
    } catch {
      return this.fallback.getItem<T>(key);
    }
  }

  setItem<T = unknown>(key: string, value: T): boolean {
    if (!this.storageUsable) {
      return this.fallback.setItem<T>(key, value);
    }
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      // QuotaExceededError or SecurityError -> Fallback to memory
      this.storageUsable = false;
      return this.fallback.setItem<T>(key, value);
    }
  }

  removeItem(key: string): boolean {
    if (!this.storageUsable) {
      return this.fallback.removeItem(key);
    }
    try {
      window.localStorage.removeItem(key);
      return true;
    } catch {
      return this.fallback.removeItem(key);
    }
  }

  clear(): void {
    if (this.storageUsable) {
      try {
        window.localStorage.clear();
      } catch {
        // Fallback
      }
    }
    this.fallback.clear();
  }

  private makeRecordKey(categoryId: string, prestationId: string, provinceSigla: string): string {
    return `${categoryId.toLowerCase()}:${prestationId.toLowerCase()}:${provinceSigla.toUpperCase()}`;
  }

  getAllCrowdsourceOverrides(): Record<string, CrowdsourceRecord> {
    if (!this.storageUsable) {
      return this.fallback.getAllCrowdsourceOverrides();
    }
    try {
      const raw = window.localStorage.getItem(CROWDSOURCE_STORAGE_KEY);
      if (!raw) return {};
      return JSON.parse(raw) as Record<string, CrowdsourceRecord>;
    } catch {
      return this.fallback.getAllCrowdsourceOverrides();
    }
  }

  getCrowdsourceOverride(
    categoryId: string,
    prestationId: string,
    provinceSigla: string
  ): CrowdsourceRecord | null {
    const all = this.getAllCrowdsourceOverrides();
    const key = this.makeRecordKey(categoryId, prestationId, provinceSigla);
    return all[key] ? { ...all[key] } : null;
  }

  saveCrowdsourceOverride(record: CrowdsourceRecord): boolean {
    const key = this.makeRecordKey(record.categoryId, record.prestationId, record.provinceSigla);
    const all = this.getAllCrowdsourceOverrides();
    all[key] = { ...record };

    if (!this.storageUsable) {
      return this.fallback.saveCrowdsourceOverride(record);
    }
    try {
      window.localStorage.setItem(CROWDSOURCE_STORAGE_KEY, JSON.stringify(all));
      return true;
    } catch {
      this.storageUsable = false;
      return this.fallback.saveCrowdsourceOverride(record);
    }
  }

  clearCrowdsourceOverrides(): void {
    if (this.storageUsable) {
      try {
        window.localStorage.removeItem(CROWDSOURCE_STORAGE_KEY);
      } catch {
        // Fallback
      }
    }
    this.fallback.clearCrowdsourceOverrides();
  }

  getRecord(prestationId: string, provinceSigla: string): CrowdsourceRecord | null {
    const all = this.getAllCrowdsourceOverrides();
    const cleanPid = prestationId.toLowerCase();
    const cleanSigla = provinceSigla.toUpperCase();
    for (const record of Object.values(all)) {
      if (
        record.prestationId.toLowerCase() === cleanPid &&
        record.provinceSigla.toUpperCase() === cleanSigla
      ) {
        return { ...record };
      }
    }
    return null;
  }

  saveRecord(record: CrowdsourceRecord): void {
    this.saveCrowdsourceOverride(record);
  }

  getAllRecords(): Record<string, CrowdsourceRecord> {
    return this.getAllCrowdsourceOverrides();
  }
}

// Global active store singleton
let activeStore: IDataStore | null = null;

export function getDataStore(): IDataStore {
  if (!activeStore) {
    activeStore = new LocalStorageDataStore();
  }
  return activeStore;
}

export function setDataStore(store: IDataStore): void {
  activeStore = store;
}

export function createInMemoryDataStore(): InMemoryDataStore {
  return new InMemoryDataStore();
}

export function resetDataStore(): void {
  activeStore = null;
}
