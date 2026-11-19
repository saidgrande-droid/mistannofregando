/**
 * src/core/dataset.ts
 * Typed wrapper and O(1) indexed lookup utilities for dataset.json.
 */

import datasetJson from './dataset.json';
import { Category, CategoryId, Dataset, Prestation, Province } from './types';

export const dataset: Dataset = datasetJson as unknown as Dataset;

// O(1) index maps
export const provincesBySigla = new Map<string, Province>(
  dataset.provinces.map((p) => [p.sigla.toUpperCase(), p])
);

export const prestationsById = new Map<string, Prestation>(
  dataset.prestations.map((p) => [p.id, p])
);

export const categoriesById = new Map<CategoryId, Category>(
  dataset.categories.map((c) => [c.id, c])
);

export function getProvinceBySigla(sigla: string): Province | undefined {
  if (!sigla) return undefined;
  return provincesBySigla.get(sigla.trim().toUpperCase());
}

export function getPrestationById(id: string): Prestation | undefined {
  if (!id) return undefined;
  const cleanId = id.trim();
  const direct = prestationsById.get(cleanId);
  if (direct) return direct;
  // Fallback alias for legacy/alternate naming
  if (cleanId === 'affitto_ufficio') {
    return prestationsById.get('affitto_quadrilocale');
  }
  return undefined;
}

export function getCategoryById(id: CategoryId): Category | undefined {
  return categoriesById.get(id);
}

export function getPrestationsByCategory(categoryId: CategoryId): Prestation[] {
  return dataset.prestations.filter((p) => p.categoryId === categoryId);
}
