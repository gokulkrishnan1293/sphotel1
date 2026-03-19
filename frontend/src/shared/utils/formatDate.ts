// INVARIANT: DB stores TIMESTAMPTZ UTC. API returns ISO 8601. Display converts to IST.
// NEVER display raw UTC timestamps. NEVER accept Unix epoch numbers.
// Full IST formatting implemented in the story that first displays dates.
export const formatDate = (isoUtc: string): string => {
  // TODO: proper IST formatting — placeholder for TypeScript compilation
  return new Date(isoUtc).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}
